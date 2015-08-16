import json
import re
import os

translations = {}
forms = {}

BASEPATH = 'data'


def normalize(s):
    a = s\
        .replace('\n\n', 'PARAGRAPH')\
        .replace('\n', ' ')\
        .replace('PARAGRAPH', '\n\n')\
        .strip()
    return re.sub(' +', ' ', a)


def iter_translations():
    for dirpath, dirnames, filenames in os.walk(BASEPATH):
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

        keys = set([r[1] for r in form['rows']])
        for key in keys:
            if key in translation:
                data[key] = translation[key]

        if data:
            path = os.path.join(BASEPATH, form_id, lang_id + '.json')
            with open(path, 'w') as fh:
                json.dump(data, fh, indent=2, separators=(',', ': '), sort_keys=True)


# for form_id, lang_id, path in iter_translations():
#     with open(path) as fh:
#         data = json.load(fh)
#
#     if lang_id != 'form':
#         data = {normalize(k): normalize(v) for k, v in data.items()}
#     else:
#         data['rows'] = [(a, normalize(b)) for a, b in data['rows']]
#
#     with open(path, 'w') as fh:
#         json.dump(data, fh, indent=2, separators=(',', ': '), sort_keys=True)
