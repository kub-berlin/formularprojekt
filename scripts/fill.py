"""Helper script to automatically fill corresponding terms in all forms."""

import csv
import json
import re
import os
import sys

UPSTREAM_LANGS = {
    'ar': 'Arabisch',
    'bs': 'BosnischKroatischSerbisch',
    'de-simple': 'Einfache Sprache',
    'el': 'Griechisch',
    'en': 'Englisch',
    'es': 'Spanisch',
    'fa': 'Persisch',
    'fr': 'Französisch',
    'ru': 'Russisch',
    'tr': 'Türkisch',
}

UPSTREAM_FORMS = {
    'AlgII': 'Alg II Hauptantrag_{lang}_2017_01',
    'BerH': 'Beratungshilfe_{lang}_2014_01',
    'KG': 'Kindergeld_Hauptantrag_{lang}_2016_09',
    'PKH': 'Prozesskostenhilfe_{lang}_2014_01',
    'PKH-ZP40': 'PKH_wirtschaftliche Verhältnisse_{lang}_2014_01',
    'Rundfunkbeitrag': 'Rundfunkbeitrag_Befreiung_{lang}_2017',
    'SozIIIB1.2': 'Sozialhilfe_Anlage 2_{lang}_2014_02',
    'SozIIIB1': 'Sozialhilfe_Antragsbogen A_{lang}_2014_01',
    # '': 'Erklärung_Verfahren_Verurteilungen_{lang}_2017_04',
}

BASEPATH = os.path.abspath('data')

translations = {}
forms = {}
langs = set()


def dump_json(data, filename):
    with open(filename, 'wb') as fh:
        s = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
        fh.write(s.encode('utf8'))


def load_translation(form_id, lang_id):
    path = os.path.join('data', form_id, lang_id + '.csv')
    data = {}
    with open(path) as fh:
        r = csv.reader(fh)
        for row in r:
            key = row[0]
            value = row[1]
            data[key] = value
    return data


def write_translation(form_id, lang_id, data):
    form = forms[form_id]

    path = os.path.join('data', form_id, lang_id + '.csv')
    keys = []
    with open(path, 'w') as fh:
        w = csv.writer(fh, dialect='unix')
        for row in form['rows']:
            key = row.get('content')
            if key and key not in keys:
                keys.append(key)
                value = data.get(key)
                if value:
                    w.writerow((key, value))


def iter_forms():
    items = sorted(os.walk(BASEPATH), key=lambda a: a[0].lower())
    for dirpath, dirnames, filenames in items:
        for filename in filenames:
            if filename == 'form.json':
                form_id = os.path.basename(dirpath)
                path = os.path.join(dirpath, filename)

                yield form_id, path


def iter_translations():
    items = sorted(os.walk(BASEPATH), key=lambda a: a[0].lower())
    for dirpath, dirnames, filenames in items:
        for filename in filenames:
            if filename.endswith('.csv'):
                form_id = os.path.basename(dirpath)
                path = os.path.join(dirpath, filename)
                lang_id = filename[:-4]

                yield form_id, lang_id, path


def get_any_translation(lang_id, key):
    for form_id in sorted(translations.keys()):
        if lang_id in translations[form_id]:
            translation = translations[form_id][lang_id]
            if key in translation:
                return translation[key]


def ask_for_map(key, candidates):
    # TODO automatic guesses based on levenshtein distance
    candidates = [c for c in sorted(candidates) if abs(len(c) - len(key)) / (len(c) + len(key)) < 0.2]
    if candidates:
        print('Match for:', key)
        for i, c in enumerate(candidates):
            print(i, c)
        answer = input()
        print()
        if answer == 'x':
            return answer
        try:
            i = int(answer)
            return candidates[i]
        except:
            pass


def get_mapping():
    try:
        with open('.mapping.json') as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def normalize(s):
    s = s\
        .replace('\n\n', 'PARAGRAPH')\
        .replace('\n', ' ')\
        .replace('PARAGRAPH', '\n\n')\
        .replace('…', '...')\
        .strip()
    s = re.sub('  +', ' ', s)
    s = re.sub(' +\\n', '\\n', s)
    s = re.sub('\\n +', '\\n', s)
    return s


def get_upstream(form_id, lang_id):
    if not form_id in UPSTREAM_FORMS:
        return {}
    if not lang_id in UPSTREAM_LANGS:
        return {}

    s = UPSTREAM_FORMS[form_id].format(lang=UPSTREAM_LANGS[lang_id])
    path = os.path.abspath('.exports/{}_exports/{}.csv'.format(s, s))

    try:
        with open(path) as fh:
            rows = list(csv.reader(fh))
    except FileNotFoundError:
        return {}

    data = {}
    for row in rows[2:]:
        if len(row) > 2:
            key = normalize(row[1])
            value = normalize(row[2])
            if key and value:
                data[key] = value

    return data


for form_id, path in iter_forms():
    with open(path) as fh:
        forms[form_id] = json.load(fh)

for form_id, lang_id, path in iter_translations():
    langs.add(lang_id)
    if form_id != 'meta':
        if form_id not in translations:
            translations[form_id] = {}
        translations[form_id][lang_id] = load_translation(form_id, lang_id)



if __name__ == '__main__':
    interactive = sys.argv[1:] == ['-i']
    verbose = sys.argv[1:] == ['-v']

    mapping = get_mapping()

    for form_id, form in sorted(forms.items()):
        keys = set([r['content'] for r in form['rows']])
        for lang_id in sorted(langs):
            data = {}
            current = translations[form_id].get(lang_id, {})
            upstream = get_upstream(form_id, lang_id)

            for key in keys:
                if key in upstream:
                    data[key] = upstream[key]
                elif key in current:
                    data[key] = current[key]
                else:
                    any_translation = get_any_translation(lang_id, key)
                    if any_translation:
                        data[key] = any_translation

            available = set(upstream.keys()).union(current.keys())

            for key in sorted(available - keys):
                value = upstream.get(key, current.get(key))
                if key in mapping:
                    if mapping[key] in keys and mapping[key] not in data:
                        data[mapping[key]] = value
                elif interactive:
                    mapped = ask_for_map(key, keys - available)
                    if mapped:
                        mapping[key] = mapped
                        if mapping[key] in data:
                            data[mapping[key]] = value

            if data:
                write_translation(form_id, lang_id, data)

            dump_json(mapping, '.mapping.json')

    if verbose:
        for form_id in UPSTREAM_FORMS:
            keys = set([r['content'] for r in forms[form_id]['rows']])

            upstream = set()
            for lang_id in UPSTREAM_LANGS:
                u = get_upstream(form_id, lang_id)
                upstream = upstream.union([normalize(k) for k in u.keys()])

            print('--- ' + form_id + ' ---')
            for key in sorted(keys - upstream):
                print('+ ' + key)
            for key in sorted(upstream - keys):
                print('- ' + key)
            print()
