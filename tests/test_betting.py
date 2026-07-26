import unittest

from blackjack_sim.betting import (
    BettingContext,
    FlatBetting,
    HiLoCounter,
    HiLoHalfKellyBetting,
    HiLoSpreadBetting,
    MartingaleBetting,
    ParoliBetting,
)


def context(true_count: float = 0.0, bankroll: float = 1_000.0) -> BettingContext:
    return BettingContext(
        running_count=0,
        true_count=true_count,
        decks_remaining=3.0,
        bankroll=bankroll,
        min_bet=1.0,
        max_bet=12.0,
    )


class HiLoCounterTests(unittest.TestCase):
    def test_balanced_single_deck_ends_at_zero(self) -> None:
        counter = HiLoCounter()
        ranks = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10) * 4
        counter.observe(ranks)
        self.assertEqual(counter.running_count, 0)

    def test_true_count_uses_remaining_decks(self) -> None:
        counter = HiLoCounter()
        counter.observe((2, 3, 4, 5))
        self.assertEqual(counter.true_count(2.0), 2.0)
        counter.reset()
        self.assertEqual(counter.running_count, 0)


class BettingPolicyTests(unittest.TestCase):
    def test_flat_bet_uses_table_minimum(self) -> None:
        self.assertEqual(FlatBetting().wager(context()), 1.0)

    def test_martingale_doubles_after_losses_and_resets_after_win(self) -> None:
        policy = MartingaleBetting()
        self.assertEqual(policy.wager(context()), 1.0)
        policy.record_result(-1.0)
        self.assertEqual(policy.wager(context()), 2.0)
        policy.record_result(-2.0)
        self.assertEqual(policy.wager(context()), 4.0)
        policy.record_result(4.0)
        self.assertEqual(policy.wager(context()), 1.0)

    def test_paroli_progresses_after_wins_and_resets_after_loss(self) -> None:
        policy = ParoliBetting()
        policy.record_result(1.0)
        self.assertEqual(policy.wager(context()), 2.0)
        policy.record_result(2.0)
        self.assertEqual(policy.wager(context()), 4.0)
        policy.record_result(-4.0)
        self.assertEqual(policy.wager(context()), 1.0)

    def test_hi_lo_spread_tracks_true_count_tiers(self) -> None:
        policy = HiLoSpreadBetting()
        self.assertEqual(policy.wager(context(1.9)), 1.0)
        self.assertEqual(policy.wager(context(2.0)), 2.0)
        self.assertEqual(policy.wager(context(4.0)), 8.0)
        self.assertEqual(policy.wager(context(6.0)), 12.0)

    def test_half_kelly_scales_with_count_and_bankroll(self) -> None:
        policy = HiLoHalfKellyBetting()
        self.assertEqual(policy.wager(context(0.0)), 1.0)
        self.assertGreater(policy.wager(context(4.0)), 1.0)
        self.assertGreater(
            policy.wager(context(4.0, bankroll=2_000)),
            policy.wager(context(4.0, bankroll=500)),
        )


if __name__ == "__main__":
    unittest.main()
