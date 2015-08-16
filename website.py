#!/use/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import json
import argparse

from flask import Flask, Blueprint, render_template
from flask import abort
from flask_frozen import Freezer
from flask.ext.markdown import Markdown

from colorama import Fore

INCOMPLETE = 1
MISSING = 2
EXTRA = 3

formularprojekt = Blueprint('formularprojekt', __name__)
forms = {}
_translations = {}
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
                        form = json.load(fh)

                        keys = set([r[1] for r in form['rows']])
                        if '' in keys:
                            keys.remove('')
                        form['keys'] = keys

                        forms[form_id] = form
                else:
                    if lang_id not in _translations:
                        _translations[lang_id] = {}
                    with open(path) as fh:
                        _translations[lang_id][form_id] = json.load(fh)

    for lang_id in _translations:
        if 'meta' in _translations[lang_id]:
            translations[lang_id] = {}
            translations[lang_id]['meta'] = _translations[lang_id]['meta']

            for form_id, translation in _translations[lang_id].items():
                if form_id in forms:
                    form = forms[form_id]
                    if len(translation) >= 0.8 * len(form['keys']):
                        translations[lang_id][form_id] = translation


def log(s, style=None, indent=0):
    if sys.stdout.isatty():
        reset = Fore.RESET

        if style == INCOMPLETE:
            color = Fore.GREEN
        elif style == MISSING:
            color = Fore.YELLOW
        elif style == EXTRA:
            color = Fore.RED
        else:
            color = ''
    else:
        reset = ''
        color = ''

    print(' ' * indent + color + s + reset)


def _check_form(form_id, langs, verbose):
        print(form_id)

        form = forms[form_id]
        keys = form['keys']
        n = len(keys)

        for lang_id in langs:
            if form_id in _translations[lang_id]:
                translation = _translations[lang_id][form_id]
                tkeys = set(translation.keys())

                translated = tkeys.intersection(keys)
                untranslated = keys.difference(tkeys)
                extra = tkeys.difference(keys)
            else:
                translated = []
                untranslated = []
                extra = []

            if len(extra) > 0:
                style = EXTRA
            elif len(translated) == 0:
                style = MISSING
            elif len(translated) < n:
                style = INCOMPLETE
            else:
                style = None

            s = '%s: %i/%i/%i' % (lang_id, len(translated), n, len(extra))
            log(s, style, 2)

            if verbose:
                for s in untranslated:
                    log(s, MISSING, 4)
                for s in extra:
                    log(s, EXTRA, 4)

        print('')


def check_translations(form_id=None, lang_id=None, verbose=False):
    if lang_id is None:
        langs = _translations.keys()
        langs.remove('de')
    else:
        langs = [lang_id]

    if form_id is None:
        for form_id in forms.keys():
            _check_form(form_id, langs, verbose)
    else:
        _check_form(form_id, langs, verbose)


@formularprojekt.app_template_filter('translate')
def translate_filter(s, lang_id, form_id, default=None):
    try:
        return translations[lang_id][form_id][s]
    except KeyError:
        pass

    if default is None:
        if form_id == 'meta':
            try:
                return translations['de'][form_id][s]
            except:
                pass

        return s
    else:
        return default


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
        lang_id='de')


@formularprojekt.route('/<lang_id>/')
def language_route(lang_id):
    if lang_id not in translations:
        abort(404)

    return render_template(
        'language.html',
        translations=translations,
        forms=forms,
        lang_id=lang_id,
        any_translations=len(translations[lang_id]) > 0)


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
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.register_blueprint(formularprojekt)
    Markdown(app)
    return app


def create_freezer(app):
    app.config.update({
        'FREEZER_BASE_URL': '/formularprojekt/',
        'FREEZER_REMOVE_EXTRA_FILES': True,
    })
    return Freezer(app)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', dest='DEBUG')
    subparsers = parser.add_subparsers(title='commands')

    parser_build = subparsers.add_parser('build', help='generate static HTML')
    parser_build.set_defaults(cmd='build')

    parser_check = subparsers.add_parser('check', help='validate translations')
    parser_check.add_argument('--verbose', '-v', action='store_true')
    parser_check.add_argument('--lang', '-l')
    parser_check.add_argument('form', nargs='?')
    parser_check.set_defaults(cmd='check')

    parser_serve = subparsers.add_parser('serve', help='run a test server')
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    return parser.parse_args(argv)


def main():  # pragma: no cover
    args = parse_args()
    load_data('data')

    app = create_app(args)

    if args.cmd == 'serve':
        app.run(port=args.port)
    elif args.cmd == 'check':
        check_translations(args.form, args.lang, args.verbose)
    else:
        freezer = create_freezer(app)
        freezer.freeze()


if __name__ == '__main__':
    sys.exit(main())
