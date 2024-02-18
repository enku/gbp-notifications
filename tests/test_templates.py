"""Tests for the templates subpackage"""

# pylint: disable=missing-docstring
from gentoo_build_publisher.types import Build
from jinja2 import Template

from gbp_notifications.exceptions import TemplateNotFoundError
from gbp_notifications.templates import load_template, render_template

from . import TestCase


class LoadTemplateTests(TestCase):
    def test_loads_template(self):
        template = load_template("email_build_pulled.eml")

        self.assertIsInstance(template, Template)
        self.assertEqual(template.name, "email_build_pulled.eml")

    def test_template_not_found(self):
        with self.assertRaises(TemplateNotFoundError):
            load_template("bogus")


class RenderTemplateTests(TestCase):
    def test_build_pulled_template(self):
        template = load_template("email_build_pulled.eml")
        event = {"build": Build(machine="babette", build_id="test")}
        context = {"event": event}

        render_template(template, context)

    def test_build_published_template(self):
        template = load_template("email_build_published.eml")
        event = {"build": Build(machine="babette", build_id="test")}
        context = {"event": event}

        render_template(template, context)
