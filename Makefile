DE_FILES := $(shell find 'data' -name 'form.json' | sed 's/form\.json$$/de.csv/g')

.PHONY: build fill pull txpull push clean

build: .env static/style.css static/* templates/* annotator/annotator.build.js
	. .env/bin/activate && python website.py build

fill: .env
	. .env/bin/activate && python scripts/fill.py

txpull:
	tx pull -af --mode=onlytranslated --minimum-perc=10
	for f in $$(find data -name *.csv); do python scripts/csv_normalize.py $$f; ./scripts/restore_mtime.sh $$f; done

push: build
	rsync -rcv --delete build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.scss node_modules
	sassc $< > $@

annotator/annotator.build.js: annotator/annotator.js annotator/app.js annotator/node_modules
	annotator/node_modules/.bin/browserify $< -o $@

annotator/node_modules:
	cd annotator && npm install "mustache" "set-dom" "markdown-it" "browserify"

de: $(DE_FILES)
data/%/de.csv: data/%/form.json scripts/de.py
	python scripts/de.py $< $@

.env:
	virtualenv .env
	. .env/bin/activate && pip install Jinja2 CommonMark colorama transifex-client

node_modules:
	npm install mfbs

clean:
	rm -f -r .env
	rm -f -r build
	rm -f -r node_modules
	rm -f -r annotator/node_modules
	rm -f static/style.css
