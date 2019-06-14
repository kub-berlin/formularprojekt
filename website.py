#!/use/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import csv
import json
import argparse
from collections import OrderedDict
from glob import glob

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Markup

from colorama import Fore
import commonmark

TARGET_DIR = 'build'
BASE_URL = '/formularprojekt'

NEAR_COMPLETE = 1
INCOMPLETE = 2
NEAR_MISSING = 3
MISSING = 4
EXTRA = 5

forms = OrderedDict()
translations = OrderedDict()
stats = OrderedDict()
template_env = Environment(
    loader=FileSystemLoader('templates'),
)


def template_filter(name):
    def decorator(fn):
        template_env.filters[name] = fn
        return fn
    return decorator


def render_template(path, **kwargs):
    template = template_env.get_template(path)
    return template.render(**kwargs, url_for=url_for)


def url_for(view, **kwargs):
    if view == 'static':
        return BASE_URL + '/static/' + kwargs['filename']
    elif view == 'formularprojekt.index_route':
        return BASE_URL + '/'.format(**kwargs)
    elif view == 'formularprojekt.language_route':
        return BASE_URL + '/{lang_id}/'.format(**kwargs)
    elif view == 'formularprojekt.translation_route':
        return BASE_URL + '/{lang_id}/{form_id}/'.format(**kwargs)
    elif view == 'formularprojekt.print_route':
        return BASE_URL + '/{lang_id}/{form_id}/'.format(**kwargs)
    else:
        raise KeyError


def load_data():
    for dirpath, dirnames, filenames in os.walk('data'):
        for filename in filenames:
            form_id = os.path.basename(dirpath)
            path = os.path.join(dirpath, filename)

            if filename == 'form.json':
                with open(path) as fh:
                    forms[form_id] = json.load(fh)
            elif filename.endswith('.csv'):
                lang_id = filename[:-4]

                if lang_id not in translations:
                    translations[lang_id] = OrderedDict()

                if lang_id != 'de' or form_id == 'meta':
                    with open(path) as fh:
                        translations[lang_id][form_id] = dict(csv.reader(fh))


def load_stats():
    for lang_id in translations:
        stats[lang_id] = OrderedDict()

        for form_id in list(forms.keys()) + ['meta']:
            if form_id == 'meta':
                keys = set(translations['en']['meta'].keys())
            else:
                keys = set(r['content'] for r in forms[form_id]['rows'])

            n = len(keys)

            if form_id in translations[lang_id]:
                translation = translations[lang_id][form_id]
                tkeys = set(translation.keys())

                data = {
                    'translated': tkeys.intersection(keys),
                    'untranslated': keys.difference(tkeys),
                    'extra': tkeys.difference(keys),
                }
            else:
                data = {
                    'translated': [],
                    'untranslated': keys,
                    'extra': [],
                }

            if len(data['extra']) > 0:
                data['style'] = EXTRA
            elif len(data['translated']) == 0:
                data['style'] = MISSING
            elif len(data['translated']) < n * 0.2:
                data['style'] = NEAR_MISSING
            elif len(data['translated']) < n * 0.8:
                data['style'] = INCOMPLETE
            elif len(data['translated']) < n:
                data['style'] = NEAR_COMPLETE
            else:
                data['style'] = None

            stats[lang_id][form_id] = data


def get_pdf(lang_id, form_id, url=True):
    fn = '{form_id}_{lang_id}_{date}.pdf'.format(
        lang_id=lang_id,
        form_id=form_id,
        date=forms[form_id]['date'])
    if os.path.exists(os.path.join('static', 'pdf', fn)):
        if url:
            return url_for('static', filename='pdf/' + fn)
        else:
            return True


def get_latest_pdf(lang_id, form_id):
    fn = '{form_id}_{lang_id}_*.pdf'.format(
        lang_id=lang_id,
        form_id=form_id)
    path = os.path.join('static', 'pdf', fn)
    matches = glob(path)
    if matches:
        return sorted(matches)[-1]


def log(s, style=None, indent=0):
    if sys.stdout.isatty():
        reset = Fore.RESET

        if style == EXTRA:
            color = Fore.RED
        elif style == MISSING:
            color = Fore.MAGENTA
        elif style == NEAR_MISSING:
            color = Fore.YELLOW
        elif style == INCOMPLETE:
            color = Fore.CYAN
        elif style == NEAR_COMPLETE:
            color = Fore.GREEN
        else:
            color = ''
    else:
        reset = ''
        color = ''

    print(' ' * indent + color + s + reset)


def _form_stats(form_id, langs, verbose):
    print(form_id)

    for lang_id in langs:
        translated = stats[lang_id][form_id]['translated']
        untranslated = stats[lang_id][form_id]['untranslated']
        extra = stats[lang_id][form_id]['extra']
        style = stats[lang_id][form_id]['style']

        n = len(translated) + len(untranslated)
        s = '%s: %i/%i/%i' % (lang_id, len(translated), n, len(extra))
        if form_id != 'meta':
            if get_pdf(lang_id, form_id, url=False):
                s += ' (pdf)'
            if lang_id in forms[form_id].get('external_langs', []):
                s += ' (external)'
        log(s, style, 2)

        if verbose:
            for s in untranslated:
                log(s, MISSING, 4)
            for s in extra:
                log(s, EXTRA, 4)

    print('')


def print_stats(form_id=None, lang_id=None, verbose=False):
    if lang_id is None:
        langs = list(stats.keys())
        if 'de' in langs:
            langs.remove('de')
        langs.sort()
    else:
        langs = [lang_id]

    if form_id is None:
        _form_stats('meta', langs, verbose)
        for form_id in sorted(forms.keys()):
            _form_stats(form_id, langs, verbose)
    else:
        _form_stats(form_id, langs, verbose)


@template_filter('markdown')
def markdown_filter(text):
    return Markup(commonmark.commonmark(text))


@template_filter('translate')
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


@template_filter('transifex')
def transifex_filter(form_id, lang_id):
    if lang_id == 'de-simple':
        lang_id = 'de_DE'
    url = 'https://www.transifex.com/kub/formulare/translate/#{}/{}/'
    return url.format(lang_id, form_id)


@template_filter('text_direction')
def text_direction_filter(lang_id):
    try:
        return translations[lang_id]['meta']['direction']
    except KeyError:
        return 'auto'


def render_index():
    return render_template(
        'index.html',
        translations=translations,
        lang_id='de')


def render_language(lang_id):
    return render_template(
        'language.html',
        translations=translations,
        forms=forms,
        lang_id=lang_id,
        any_translations=len(translations[lang_id]) > 1)  # only meta


def render_translation(lang_id, form_id):
    available_languages = [l for l in translations
        if form_id in translations[l]]

    return render_template(
        'translation.html',
        forms=forms,
        lang_id=lang_id,
        form_id=form_id,
        pdf=get_pdf(lang_id, form_id),
        form_view_url=forms[form_id].get('form_view_url', 'print/'),
        available_languages=available_languages)


def render_print(lang_id, form_id):
    page_n = max((row['page'] for row in forms[form_id]['rows']))
    pages = []
    bg_template = 'static/forms/%s/bg-%i.svg'
    for i in range(page_n + 1):
        pages.append({
            'bg': os.path.exists(bg_template % (form_id, i)),
            'rows': []
        })

    trans = lambda s: translate_filter(s, lang_id, form_id, '')

    for row in forms[form_id]['rows']:
        n = int(row['page'])

        if row.get('append') is None:
            pages[n]['rows'].append(row)
            row['appended'] = row['content']
            row['translation'] = trans(row['content'])
        else:
            host = pages[n]['rows'][-1]
            host['appended'] += row['append']
            host['appended'] += row['content']
            host['translation'] += row['append']
            host['translation'] += trans(row['content'])

    return render_template(
        'print.html',
        forms=forms,
        pages=pages,
        lang_id=lang_id,
        form_id=form_id)


def render_resource(lang_id, form_id, resource_id):
    return render_template(
        os.path.join('forms', form_id, resource_id),
        forms=forms,
        direction=text_direction_filter(lang_id),
        lang_id=lang_id,
        form_id=form_id)


def render_stats():
    langs = list(stats.keys())
    langs.remove('de')
    langs.sort()

    return render_template(
        'stats.html',
        stats=stats,
        langs=langs,
        forms=forms)


def render_overview():
    data = []

    for form_id, form in sorted(forms.items()):
        pdfs = {}
        for lang_id in sorted(stats):
            pdf = get_latest_pdf(lang_id, form_id)
            if pdf:
                pdfs[lang_id] = pdf
        if pdfs or 'external' in form:
            data.append((form_id, form, pdfs))

    return render_template(
        'overview.html',
        data=data)


def link_if_missing(src):
    target = os.path.join(TARGET_DIR, src)
    if not os.path.exists(target):
        print('linking', target)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        os.link(src, target)


def link_dir(path):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            link_if_missing(path)


def is_stale(target, dependencies):
    if not os.path.exists(target):
        return True
    mtime = os.path.getmtime(target)
    return any(mtime < os.path.getmtime(p) for p in dependencies)


def write_file(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    current = None
    if os.path.exists(path):
        with open(path) as fh:
            current = fh.read()
    if s != current:
        print('writing', path)
        with open(path, 'w') as fh:
            fh.write(s)


def render_if_stale(name, lang_id, form_id):
    args = (lang_id, form_id)
    form_fn = os.path.join('data', form_id, 'form.json')
    translation_fn = os.path.join('data', form_id, lang_id + '.csv')
    template_fn = os.path.join('templates', name + '.html')
    base_fn = os.path.join('templates', 'base.html')
    dependencies = [form_fn, translation_fn]

    # TODO generic
    if name == 'print':
        path = os.path.join(TARGET_DIR, lang_id, form_id, 'print/index.html')
        render = render_print
        dependencies.append(template_fn)
    elif name == 'translation':
        path = os.path.join(TARGET_DIR, lang_id, form_id, 'index.html')
        render = render_translation
        dependencies.append(template_fn)
        dependencies.append(base_fn)
    else:
        args = (lang_id, form_id, name)
        path = os.path.join(TARGET_DIR, lang_id, form_id, 'r', name)
        template_fn = os.path.join('templates', 'forms', form_id, name)
        render = render_resource
        dependencies.append(template_fn)
        dependencies.append(base_fn)

    if is_stale(path, dependencies):
        write_file(path, render(*args))


def build():
    link_dir('static')
    link_dir('data')

    link_if_missing('annotator/annotator.build.js')
    link_if_missing('annotator/sw.js')
    link_if_missing('annotator/annotator.css')
    link_if_missing('annotator/index.html')
    link_if_missing('annotator/template.html')

    path = os.path.join(TARGET_DIR, 'index.html')
    write_file(path, render_index())

    path = os.path.join(TARGET_DIR, 'stats', 'index.html')
    write_file(path, render_stats())

    path = os.path.join(TARGET_DIR, 'overview', 'index.html')
    write_file(path, render_overview())

    for lang_id in translations:
        path = os.path.join(TARGET_DIR, lang_id, 'index.html')
        write_file(path, render_language(lang_id))

        for form_id in translations[lang_id]:
            if form_id != 'meta':
                render_if_stale('translation', lang_id, form_id)
                render_if_stale('print', lang_id, form_id)

                resource_path = os.path.join('templates', 'forms', form_id)
                for dirpath, dirnames, filenames in os.walk(resource_path):
                    for filename in filenames:
                        render_if_stale(filename, lang_id, form_id)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', dest='DEBUG')
    subparsers = parser.add_subparsers(title='commands')

    parser_build = subparsers.add_parser('build', help='generate static HTML')
    parser_build.set_defaults(cmd='build')

    parser_stats = subparsers.add_parser('stats', help='validate translations')
    parser_stats.add_argument('--verbose', '-v', action='store_true')
    parser_stats.add_argument('--lang', '-l')
    parser_stats.add_argument('form', nargs='?')
    parser_stats.set_defaults(cmd='stats')

    return parser.parse_args(argv)


def main():  # pragma: no cover
    args = parse_args()
    load_data()
    load_stats()

    if args.cmd == 'stats':
        print_stats(args.form, args.lang, args.verbose)
    else:
        build()


if __name__ == '__main__':
    sys.exit(main())
