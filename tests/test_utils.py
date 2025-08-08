"""Tests for the utils module"""

# pylint: disable=missing-docstring
import collections
import unittest

from unittest_fixtures import Fixtures, given, where

from gbp_notifications.utils import (
    find_subscribers,
    parse_header_conf,
    parse_webhook_config,
    sort_items_by,
    split_string_by,
)

from . import lib


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


@given(r1=lib.recipient, r2=lib.recipient, r3=lib.recipient)
@where(r1__name="foo", r2__name="bar", r3__name="baz")
class FindSubscribersTests(unittest.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        recipients = [fixtures.r1, fixtures.r2, fixtures.r3]
        subs = find_subscribers(recipients, ["bar", "baz"])

        self.assertEqual({fixtures.r2, fixtures.r3}, subs)

    def test_bogus_name(self, fixtures: Fixtures) -> None:
        recipients = [fixtures.r1, fixtures.r2, fixtures.r3]
        subs = find_subscribers(recipients, ["bar", "bogus"])

        self.assertEqual({fixtures.r2}, subs)


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


class ParseWebhookConfigTests(unittest.TestCase):
    def test_url_only(self) -> None:
        result = parse_webhook_config("http://host.invalid/webhook")

        self.assertEqual(result, ("http://host.invalid/webhook", {}))

    def test_headers(self) -> None:
        result = parse_webhook_config("http://host.invalid/webhook|This=that|The=other")

        self.assertEqual(
            result, ("http://host.invalid/webhook", {"This": "that", "The": "other"})
        )

    def test_delim_but_no_header(self) -> None:
        result = parse_webhook_config("http://host.invalid/webhook|")

        self.assertEqual(result, ("http://host.invalid/webhook", {}))


class ParseHeaderConfTests(unittest.TestCase):
    """Tests for parse_header_conf()"""

    def test(self) -> None:
        header_conf = "This=that|The=other"

        self.assertEqual(
            {"This": "that", "The": "other"}, parse_header_conf(header_conf)
        )

    def test_empty_string(self) -> None:
        self.assertEqual({}, parse_header_conf(""))

    def test_empty_value(self) -> None:
        header_conf = "This=that|The="

        self.assertEqual({"This": "that", "The": ""}, parse_header_conf(header_conf))

    def test_missing_equals(self) -> None:
        header_conf = "This=that|Theother"

        with self.assertRaises(ValueError) as exc_info:
            parse_header_conf(header_conf)

        error = exc_info.exception

        self.assertEqual("Invalid header assignment: 'Theother'", str(error))

    def test_duplicate(self) -> None:
        header_conf = "This=that|THIS=other"

        self.assertEqual({"THIS": "other"}, parse_header_conf(header_conf))

    def test_empty_header_name(self) -> None:
        header_conf = "=that"

        with self.assertRaises(ValueError) as exc_info:
            parse_header_conf(header_conf)

        error = exc_info.exception

        self.assertEqual(f"Invalid header assignment: {header_conf!r}", str(error))
