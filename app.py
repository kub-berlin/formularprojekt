#!/use/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from flask import Flask, Blueprint, render_template
from flask import current_app, url_for
from flask import Markup, escape
from flask_frozen import Freezer

formularprojekt = Blueprint('formularprojekt', __name__)


@formularprojekt.route('/')
def index_route():
    return 'index'


@formularprojekt.route('/<lang>/')
def language_route(lang):
    return 'language'


@formularprojekt.route('/<lang>/<form>/')
def translation_route(lang, form):
    return 'translation'


def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(formularprojekt)
    return app


def create_freezer(*args, **kwargs):
    # add url generators here
    freezer = Freezer(create_app(*args, **kwargs))
    return freezer


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', '-d', action='store_true', dest='DEBUG')
    subparsers = parser.add_subparsers(title='commands')

    parser_build = subparsers.add_parser(
        'build', help='generate static sites')
    parser_build.add_argument(
        '--destination', '-d', default=None,
        help='directory where Flekky will write files '
               '(default: <source>_build)')
    parser_build.set_defaults(cmd='build')

    parser_serve = subparsers.add_parser(
        'serve', help='run a test server for development')
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    return parser.parse_args(argv)


def main():  # pragma: no cover
    args = parse_args()

    if True:
        app = create_app(args)
        app.run()
    else:
        freezer = create_freezer()
        freezer.freeze()


if __name__ == '__main__':
    sys.exit(main())
