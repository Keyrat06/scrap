"""Rules-driven blackjack round engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Action, Hand, Rules
from .shoe import Shoe
from .strategies import Strategy


@dataclass(frozen=True)
class RoundResult:
    net: float
    wagered: float
    hands: int
    observed_cards: tuple[int, ...]


class BlackjackEngine:
    def __init__(self, rules: Rules, shoe: Shoe) -> None:
        self.rules = rules
        self.shoe = shoe

    def prepare_round(self) -> bool:
        """Shuffle if the cut card was reached; return whether a shuffle occurred."""
        if self.shoe.needs_shuffle:
            self.shoe.shuffle()
            return True
        return False

    def play_round(self, strategy: Strategy, base_wager: float = 1.0) -> RoundResult:
        if base_wager <= 0:
            raise ValueError("base wager must be positive")
        self.prepare_round()

        observed: list[int] = []

        def deal_visible() -> int:
            card = self.shoe.deal()
            observed.append(card)
            return card

        player = Hand([deal_visible()], wager=base_wager)
        dealer = Hand([deal_visible()])
        player.cards.append(deal_visible())
        dealer.cards.append(self.shoe.deal())

        if player.is_blackjack or dealer.is_blackjack:
            if dealer.is_blackjack:
                observed.append(dealer.cards[1])
            if player.is_blackjack and dealer.is_blackjack:
                net = 0.0
            elif player.is_blackjack:
                net = base_wager * self.rules.blackjack_payout
            else:
                net = -base_wager
            return RoundResult(
                net=net,
                wagered=base_wager,
                hands=1,
                observed_cards=tuple(observed),
            )

        hands = [player]
        wagered = base_wager
        index = 0
        while index < len(hands):
            hand = hands[index]
            while not hand.is_bust:
                allowed = self._allowed_actions(hand, len(hands))
                action = strategy.decide(
                    hand,
                    dealer.cards[0],
                    self.rules,
                    frozenset(allowed),
                )
                if action not in allowed:
                    raise ValueError(f"strategy selected disallowed action: {action}")
                if action is Action.STAND:
                    break
                if action is Action.HIT:
                    hand.cards.append(deal_visible())
                    continue
                if action is Action.DOUBLE:
                    wagered += hand.wager
                    hand.wager *= 2
                    hand.doubled = True
                    hand.cards.append(deal_visible())
                    break

                wagered += hand.wager
                split_rank = hand.cards[0]
                first = Hand(
                    [split_rank, deal_visible()],
                    wager=hand.wager,
                    from_split=True,
                    split_aces=split_rank == 1,
                )
                second = Hand(
                    [split_rank, deal_visible()],
                    wager=hand.wager,
                    from_split=True,
                    split_aces=split_rank == 1,
                )
                hands[index] = first
                hands.insert(index + 1, second)
                hand = first
            index += 1

        if any(not hand.is_bust for hand in hands):
            observed.append(dealer.cards[1])
            self._play_dealer(dealer, observed)

        net = sum(self._settle(hand, dealer) for hand in hands)
        return RoundResult(
            net=net,
            wagered=wagered,
            hands=len(hands),
            observed_cards=tuple(observed),
        )

    def _allowed_actions(self, hand: Hand, hand_count: int) -> set[Action]:
        allowed = {Action.STAND}
        split_allowed = (
            hand.can_split
            and hand_count < self.rules.max_split_hands
            and (hand.cards[0] != 1 or not hand.from_split or self.rules.resplit_aces)
        )
        if split_allowed:
            allowed.add(Action.SPLIT)
        if not hand.split_aces or self.rules.hit_split_aces:
            allowed.add(Action.HIT)
            if len(hand.cards) == 2 and (
                not hand.from_split or self.rules.double_after_split
            ):
                allowed.add(Action.DOUBLE)
        return allowed

    def _play_dealer(self, dealer: Hand, observed: list[int]) -> None:
        while dealer.total < 17 or (
            dealer.total == 17 and dealer.is_soft and self.rules.dealer_hits_soft_17
        ):
            card = self.shoe.deal()
            dealer.cards.append(card)
            observed.append(card)

    @staticmethod
    def _settle(player: Hand, dealer: Hand) -> float:
        if player.is_bust:
            return -player.wager
        if dealer.is_bust or player.total > dealer.total:
            return player.wager
        if player.total < dealer.total:
            return -player.wager
        return 0.0
