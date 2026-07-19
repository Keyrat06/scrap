import unittest

from blackjack_sim.models import Hand, Rules


class HandTests(unittest.TestCase):
    def test_ace_is_downgraded_to_avoid_bust(self) -> None:
        hand = Hand([1, 7, 9])
        self.assertEqual(hand.total, 17)
        self.assertFalse(hand.is_soft)

    def test_blackjack_excludes_split_twenty_one(self) -> None:
        self.assertTrue(Hand([1, 10]).is_blackjack)
        self.assertFalse(Hand([1, 10], from_split=True).is_blackjack)

    def test_pair_and_bust_properties(self) -> None:
        self.assertTrue(Hand([8, 8]).can_split)
        self.assertTrue(Hand([10, 6, 8]).is_bust)


class RulesTests(unittest.TestCase):
    def test_invalid_penetration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Rules(penetration=1.0)


if __name__ == "__main__":
    unittest.main()
