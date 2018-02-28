DE_FILES := $(shell find 'data' -name 'form.json' | sed 's/form\.json$$/de.csv/g')

.PHONY: build serve push clean

build: .env static/style.css static/* templates/* annotator/annotator.build.js
	. .env/bin/activate && python website.py build

serve: .env static/style.css static/* templates/* annotator/annotator.build.js
	. .env/bin/activate && python website.py serve

fill: .env
	. .env/bin/activate && python scripts/fill.py

pull:
	cd .drive && drive pull -ignore-name-clashes -export=csv -exports-dir="../.exports/" -explicitly-export

txpull:
	tx pull -af --mode=onlytranslated --minimum-perc=10
	for f in $$(find data -name *.csv); do python scripts/csv_normalize.py $$f; done

push: build
	rsync -rcv --delete build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.scss node_modules
	node_modules/.bin/node-sass $< > $@

annotator/annotator.build.js: annotator/annotator.js annotator/app.js annotator/node_modules
	annotator/node_modules/.bin/browserify $< -o $@

annotator/node_modules:
	cd annotator && npm install "mustache" "set-dom" "markdown-it" "browserify"

de: $(DE_FILES)
data/%/de.csv: data/%/form.json scripts/de.py
	python scripts/de.py $< $@

.env:
	virtualenv .env
	. .env/bin/activate && pip install Flask Frozen-Flask CommonMark colorama transifex-client

node_modules:
	npm install mfbs node-sass

clean:
	rm -f -r .env
	rm -f -r build
	rm -f -r node_modules
	rm -f -r annotator/node_modules
	rm -f static/style.css
