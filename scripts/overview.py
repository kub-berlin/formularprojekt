import os
import csv
import json
import functools

BASEPATH = 'data'
BASEURL = '/formularprojekt'
LANG_IDS = ['ar', 'de-simple', 'en', 'es', 'fa', 'fr', 'ru', 'tr']


def iter_forms():
	items = sorted(os.walk(BASEPATH), key=lambda a: a[0].lower())
	for dirpath, dirnames, filenames in items:
		for filename in filenames:
			if filename == 'form.json':
				form_id = os.path.basename(dirpath)
				path = os.path.join(dirpath, filename)
				with open(path) as fh:
					form = json.load(fh)
					yield form_id, form


def iter_pdfs(form_id, form):
	for lang_id in LANG_IDS:
		fn = '{form_id}_{lang_id}_{date}.pdf'.format(
			lang_id=lang_id,
			form_id=form_id,
			date=form['date'])
		if os.path.exists(os.path.join('static', 'pdf', fn)):
			yield lang_id, fn


@functools.lru_cache()
def get_meta(lang_id):
	data = {}
	with open(os.path.join(BASEPATH, 'meta', lang_id + '.csv')) as fh:
		r = csv.reader(fh)
		for row in r:
			key = row[0]
			value = row[1]
			data[key] = value
	return data


def meta(s, lang_id):
	translation = get_meta(lang_id)
	de = get_meta('de')
	return translation.get(s, de.get(s))


for form_id, form in iter_forms():
	pdfs = list(iter_pdfs(form_id, form))
	if pdfs or 'external' in form:
		print('<h3 lang="de">{}</h3>'.format(form['title']))
		print('<ul>')
		for lang_id, fn in pdfs:
			print('  <li><a href="{href}" lang="{lang_id}" hreflang="{lang_id}">{lang}</a></li>'.format(
				href='{}/static/pdf/{}'.format(BASEURL, fn),
				lang_id=lang_id,
				lang=meta('language', lang_id)
			))
		if 'external' in form:
			print('  <li>Weitere Übersetzungen&hellip;<ul>')
			for name, href in sorted(form['external'].items()):
				print('    <li><a href="{href}" rel="external">{name}</a></li>'.format(
					href=href,
					name=name
				))
			print('  </ul></li>')
		print('</ul>')
