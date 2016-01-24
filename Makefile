.PHONY: build serve push

build: .env static/style.css static/* templates/*
	. .env/bin/activate && python website.py build

serve: .env static/style.css static/* templates/* annotator/bower_components
	. .env/bin/activate && python website.py serve

push: build
	rsync -rcv --delete build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.less static_src/bower_components
	lessc $< $@

static_src/bower_components:
	cd static_src && bower install mfbs

annotator/bower_components:
	cd annotator && bower install "xi/muu#~0.1.2" "wildlyinaccurate/promise-xhr#~0.0.1" "markdown-it"

de: data/KG/de.json data/KG1/de.json data/KG11a/de.json data/KG3a/de.json data/KG3b/de.json data/KG5/de.json data/KG5a/de.json data/KG5d/de.json data/Rundfunkbeitrag_Befreiung/de.json data/SozIIIB1/de.json data/SozIIIB1.1/de.json data/SozIIIB1.2/de.json
data/%/de.json: data/%/form.json scripts/de.py
	python scripts/de.py $< $@

.env:
	virtualenv .env
	. .env/bin/activate && pip install Flask Flask-Markdown Frozen-Flask colorama transifex-client
