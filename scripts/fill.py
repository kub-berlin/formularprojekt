"""Helper script to automatically fill corresponding terms in all forms."""

import json
import re
import os

translations = {}
forms = {}

BASEPATH = os.path.abspath('data')

ensure_str = lambda s: s if isinstance(s, str) else s.encode('utf8')


def normalize(s):
    a = s\
        .replace('\n\n', 'PARAGRAPH')\
        .replace('\n', ' ')\
        .replace('PARAGRAPH', '\n\n')\
        .strip()
    return re.sub(' +', ' ', a)


def iter_translations():
    items = sorted(os.walk(BASEPATH), key=lambda a: '/zz' if a[0].endswith('all') else a[0].lower())
    for dirpath, dirnames, filenames in items:
        for filename in filenames:
            form_id = os.path.basename(dirpath)
            path = os.path.join(dirpath, filename)

            if filename.endswith('.json'):
                lang_id = filename[:-5]

                yield form_id, lang_id, path


for form_id, lang_id, path in iter_translations():
    if form_id != 'meta':
        with open(path) as fh:
            try:
                data = json.load(fh)
            except:
                print(path)
                raise

        if lang_id == 'form':
            forms[form_id] = data
        else:
            if lang_id not in translations:
                translations[lang_id] = {}
            translations[lang_id].update(data)


for form_id, form in forms.items():
    for lang_id, translation in translations.items():
        data = {}

        keys = set([r['content'] for r in form['rows']])
        if '' in keys:
            keys.remove('')
        for key in keys:
            if key in translation:
                data[key] = translation[key]

        if data:
            path = os.path.join(BASEPATH, form_id, lang_id + '.json')
            with open(path, 'wb') as fh:
                s = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
                fh.write(s.encode('utf8'))


# for form_id, lang_id, path in iter_translations():
#     with open(path) as fh:
#         data = json.load(fh)
#
#     if lang_id != 'form':
#         data = {normalize(k): normalize(v) for k, v in data.items()}
#     else:
#        for row in data['rows']:
#            row['content'] = normalize(row['content'])
#
#     with open(path, 'w') as fh:
#         s = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
#         fh.write(s.encode('utf8'))
