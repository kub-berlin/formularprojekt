.PHONY: build serve push

build: .env static/style.css static/* templates/*
	. .env/bin/activate && python website.py build

serve: .env static/style.css static/* templates/* annotator/bower_components
	. .env/bin/activate && python website.py serve

push: build
	rsync -rv --delete build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.less static_src/bower_components
	lessc $< $@

static_src/bower_components:
	cd static_src && bower install mfbs

annotator/bower_components:
	cd annotator && bower install "xi/muu#~0.1.1" "wildlyinaccurate/promise-xhr#~0.0.1"

.env:
	virtualenv .env
	. .env/bin/activate && pip install Flask Flask-Markdown Frozen-Flask colorama
