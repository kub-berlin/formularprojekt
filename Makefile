DE_FILES := $(shell find 'data' -name 'form.json' | sed 's/form\.json$$/de.json/g')

.PHONY: build serve push clean

build: .env static/style.css static/* templates/* annotator/annotator.build.js
	. .env/bin/activate && python website.py build

serve: .env static/style.css static/* templates/* annotator/annotator.build.js
	. .env/bin/activate && python website.py serve

fill: .env
	. .env/bin/activate && python scripts/fill.py

pull:
	cd .drive && drive pull -ignore-name-clashes -export=csv -exports-dir="../.exports/" -explicitly-export

push: build
	rsync -rcv --delete build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.scss static_src/node_modules .env
	. .env/bin/activate && node-sass $< > $@

static_src/node_modules:
	. .env/bin/activate && cd static_src && npm install mfbs

annotator/annotator.build.js: annotator/annotator.js annotator/app.js annotator/node_modules
	browserify $< -o $@

annotator/node_modules:
	. .env/bin/activate && cd annotator && npm install "mustache" "set-dom" "markdown-it"

de: $(DE_FILES)
data/%/de.json: data/%/form.json scripts/de.py
	python scripts/de.py $< $@

.env:
	virtualenv .env
	. .env/bin/activate && pip install Flask Frozen-Flask CommonMark colorama transifex-client nodeenv
	echo node-sass >> node_deps
	. .env/bin/activate && nodeenv --node=system --python-virtualenv -r node_deps
	rm node_deps

clean:
	rm -f -r .env
	rm -f -r build
	rm -f -r static_src/node_modules
	rm -f -r annotator/node_modules
	rm -f static/style.css
