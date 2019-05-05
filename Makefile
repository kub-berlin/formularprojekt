DE_FILES := $(shell find 'data' -name 'form.json' | sed 's/form\.json$$/de.csv/g')

.PHONY: build fill pull txpull push clean

build: .venv annotator/annotator.build.js static/style.css static/* templates/*
	.venv/bin/python website.py build

fill: .venv
	.venv/bin/python scripts/fill.py

txpull: .venv
	.venv/bin/tx pull -af --mode=onlytranslated --minimum-perc=10
	for f in $$(find data -name *.csv); do python scripts/csv_normalize.py $$f; ./scripts/restore_mtime.sh $$f; done

push: build
	xiftp push formularprojekt

static/style.css: static_src/style.scss node_modules
	sassc $< > $@

annotator/annotator.build.js: annotator/annotator.js annotator/app.js annotator/node_modules
	annotator/node_modules/.bin/browserify $< -o $@

annotator/node_modules:
	cd annotator && npm install "mustache" "set-dom" "markdown-it" "browserify"

de: $(DE_FILES)
data/%/de.csv: data/%/form.json scripts/de.py
	.venv/bin/python scripts/de.py $< $@

.venv:
	python3 -m venv .venv
	.venv/bin/pip install Jinja2 CommonMark colorama transifex-client

node_modules:
	npm install mfbs

clean:
	rm -f -r .venv
	rm -f -r build
	rm -f -r node_modules
	rm -f -r annotator/node_modules
	rm -f static/style.css
