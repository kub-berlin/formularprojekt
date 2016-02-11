import json
import os

BASEPATH = os.path.abspath('data')

EXCEPTIONS = [
    'BIC',
    'IBAN',
]

ensure_str = lambda s: s if isinstance(s, str) else s.encode('utf8')


def iter_translations():
    for dirpath, dirnames, filenames in os.walk(BASEPATH):
        for filename in filenames:
            form_id = os.path.basename(dirpath)
            path = os.path.join(dirpath, filename)

            if filename.endswith('.json') and filename != 'form.json':
                lang_id = filename[:-5]

                yield form_id, lang_id, path


for form_id, lang_id, path in iter_translations():
    if lang_id != 'de':
        with open(path) as fh:
            data = json.load(fh)

        deletes = set()
        for key in data:
            if data[key] == key and key not in EXCEPTIONS:
                deletes.add(key)

        for key in deletes:
            del data[key]

        with open(path, 'wb') as fh:
            s = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
            fh.write(ensure_str(s))
