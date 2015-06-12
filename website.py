#!/use/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import json
import datetime
import argparse

from flask import Flask, Blueprint, render_template
from flask import abort
from flask_frozen import Freezer
from flask.ext.markdown import Markdown

formularprojekt = Blueprint('formularprojekt', __name__)
forms = {}
translations = {}


def load_data(top):
    for dirpath, dirnames, filenames in os.walk(top):
        for filename in filenames:
            form_id = os.path.basename(dirpath)
            path = os.path.join(dirpath, filename)

            if filename.endswith('.json'):
                lang_id = filename[:-5]

                if lang_id == 'form':
                    with open(path) as fh:
                        forms[form_id] = json.load(fh)
                else:
                    if not lang_id in translations:
                        translations[lang_id] = {}
                    with open(path) as fh:
                        translations[lang_id][form_id] = json.load(fh)


@formularprojekt.app_template_filter('translate')
def translate_filter(s, lang_id, form_id):
    try:
        return translations[lang_id][form_id][s]
    except KeyError:
        return s


@formularprojekt.app_template_filter('text_direction')
def text_direction_filter(lang_id):
    try:
        return translations[lang_id]['meta']['direction']
    except KeyError:
        return 'auto'


@formularprojekt.route('/')
def index_route():
    return render_template(
        'index.html',
        translations=translations,
        lang_id='en')


@formularprojekt.route('/<lang_id>/')
def language_route(lang_id):
    if lang_id not in translations:
        abort(404)

    return render_template(
        'language.html',
        translations=translations,
        forms=forms,
        lang_id=lang_id,
        any_translations=len(translations[lang_id]) > 1)


@formularprojekt.route('/<lang_id>/<form_id>/')
def translation_route(lang_id, form_id):
    available_languages = [l for l in translations
        if form_id in translations[l]]

    if lang_id not in translations:
        abort(404)
    if form_id not in forms:
        abort(404)
    if form_id not in translations[lang_id]:
        abort(404)

    return render_template(
        'translation.html',
        forms=forms,
        lang_id=lang_id,
        form_id=form_id,
        available_languages=available_languages)


def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(formularprojekt)
    Markdown(app)
    return app


def create_freezer(*args, **kwargs):
    freezer = Freezer(create_app(*args, **kwargs))
    return freezer


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', dest='DEBUG')
    subparsers = parser.add_subparsers(title='commands')

    parser_build = subparsers.add_parser('build', help='generate static HTML')
    parser_build.set_defaults(cmd='build')

    parser_serve = subparsers.add_parser('serve', help='run a test server')
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    return parser.parse_args(argv)


def main():  # pragma: no cover
    args = parse_args()
    load_data('data')

    if args.cmd == 'serve':
        app = create_app(args)
        app.run(port=args.port)
    else:
        freezer = create_freezer()
        freezer.freeze()


if __name__ == '__main__':
    sys.exit(main())
