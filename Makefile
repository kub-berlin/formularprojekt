.PHONY: build
build: static/style.css static/* templates/*
	. ./.env/bin/activate && python website.py build

push: build
	rsync -rv build/ spline:public_html/webroot/formularprojekt/

static/style.css: static_src/style.less static_src/bower_components
	lessc $< $@

static_src/bower_components:
	cd static_src && bower install mfbs
