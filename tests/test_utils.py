"""Tests for the utils module"""

# pylint: disable=missing-docstring
import collections
import unittest

from gbp_notifications.types import Recipient
from gbp_notifications.utils import find_subscribers, sort_items_by, split_string_by


class SplitStringByTests(unittest.TestCase):
    def test(self) -> None:
        s = "prefix|suffix"

        self.assertEqual(("prefix", "suffix"), split_string_by(s, "|"))

    def test_delim_does_not_in_string(self) -> None:
        s = "prefixsuffix"

        with self.assertRaises(ValueError):
            split_string_by(s, "|")

    def test_string_starting_with_delim(self) -> None:
        s = "|suffix"

        self.assertEqual(("", "suffix"), split_string_by(s, "|"))

    def test_string_ending_with_delim(self) -> None:
        s = "prefix|"

        self.assertEqual(("prefix", ""), split_string_by(s, "|"))

    def test_string_with_back_to_back_delim(self) -> None:
        s = "prefix||suffix"

        self.assertEqual(("prefix", "|suffix"), split_string_by(s, "|"))


class FindSubscribersTests(unittest.TestCase):
    recipients = [
        Recipient(name="foo", config={}),
        Recipient(name="bar", config={}),
        Recipient(name="baz", config={}),
    ]

    def test(self) -> None:
        subs = find_subscribers(self.recipients, ["bar", "baz"])

        self.assertEqual(
            {Recipient(name="bar", config={}), Recipient(name="baz", config={})}, subs
        )

    def test_bogus_name(self) -> None:
        subs = find_subscribers(self.recipients, ["bar", "bugus"])

        self.assertEqual({Recipient(name="bar", config={})}, subs)


class SortItemsByTests(unittest.TestCase):
    def test(self) -> None:
        Bag = collections.namedtuple("Bag", "spam eggs")
        bags = [Bag(3, 6), Bag(2, 8), Bag(0, 4), Bag(9, 1)]

        self.assertEqual(
            [Bag(9, 1), Bag(0, 4), Bag(3, 6), Bag(2, 8)], sort_items_by(bags, "eggs")
        )
        self.assertEqual(
            [Bag(0, 4), Bag(2, 8), Bag(3, 6), Bag(9, 1)], sort_items_by(bags, "spam")
        )
