"""Tests for the templates subpackage"""

# pylint: disable=missing-docstring,unused-argument
import gbp_testkit.fixtures as testkit
from jinja2 import Template
from unittest_fixtures import Fixtures, given

from gbp_notifications.exceptions import TemplateNotFoundError
from gbp_notifications.templates import load_template, render_template

from . import lib


@given(testkit.build)
class LoadTemplateTests(lib.TestCase):
    def test_loads_template(self, fixtures: Fixtures) -> None:
        template = load_template("email_build_pulled.eml")

        self.assertIsInstance(template, Template)
        self.assertEqual(template.name, "email_build_pulled.eml")

    def test_template_not_found(self, fixtures: Fixtures) -> None:
        with self.assertRaises(TemplateNotFoundError):
            load_template("bogus")


@given(testkit.build)
class RenderTemplateTests(lib.TestCase):
    def test_build_pulled_template(self, fixtures: Fixtures) -> None:
        template = load_template("email_build_pulled.eml")
        event = {"build": fixtures.build}
        context = {"event": event}

        render_template(template, context)

    def test_build_published_template(self, fixtures: Fixtures) -> None:
        template = load_template("email_build_published.eml")
        event = {"build": fixtures.build}
        context = {"event": event}

        render_template(template, context)
