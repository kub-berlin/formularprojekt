#!/use/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import argparse

from flask import Flask, Blueprint, render_template
from flask import abort
from flask_frozen import Freezer
from flask.ext.markdown import Markdown

formularprojekt = Blueprint('formularprojekt', __name__)
forms = {
    'kindergeld': {
        'title': 'Antrag auf Kindergeld',
        'date': datetime.date.today(),
        'rows': [
            ('2.1.1', 'foo')
        ]
    }
}
translations = {
    'en': {
        'meta': {
            'disclaimer': 'This is an unofficial translation',
            'language': 'English',
        },
        'kindergeld': {
            'foo': 'bar',
        }
    }
}


@formularprojekt.route('/')
def index_route():
    return render_template(
        'index.html',
        translations=translations)


@formularprojekt.route('/<lang_id>/')
def language_route(lang_id):
    if lang_id not in translations:
        abort(404)

    return render_template(
        'language.html',
        translations=translations,
        forms=forms,
        lang_id=lang_id)


@formularprojekt.route('/<lang_id>/<form_id>/')
def translation_route(lang_id, form_id):
    if lang_id not in translations:
        abort(404)
    if form_id not in forms:
        abort(404)
    if form_id not in translations[lang_id]:
        abort(404)

    return render_template(
        'translation.html',
        translations=translations,
        forms=forms,
        lang_id=lang_id,
        form_id=form_id)


def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(formularprojekt)
    Markdown(app)
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

    if args.cmd == 'serve':
        app = create_app(args)
        app.run()
    else:
        freezer = create_freezer()
        freezer.freeze()


if __name__ == '__main__':
    sys.exit(main())
