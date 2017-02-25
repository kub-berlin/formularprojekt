(function(fetch, muu, markdown) {
	'use strict';

	// register service worker
	if ('serviceWorker' in navigator) {
		navigator.serviceWorker.register('sw.js').then(function(reg) {
			console.log('Registration succeeded. Scope is ' + reg.scope);
		}).catch(function(error) {
			console.log('Registration failed with ' + error);
		});
	}

	var registry = new muu.Registry();

	fetch('template.html').then(function(response) {
		return response.ok ? response.text() : Promise.reject(response);
	}).then(function(template) {
		registry.registerDirective('forms', template, function(self) {
			var data = {};

			var rget = function(row) {
				return function(key) {
					return row[key];
				};
			};

			var rset = function(row) {
				return function(key, value) {
					row[key] = value;
				};
			};

			var update = function(undoable) {
				if (data.form) {
					data.rows = data.form.rows.filter(function(row) {
						return row.page === data.page;
					});
				} else {
					data.rows = void 0;
					data.selected = void 0;
				}
				data.bg = '../static/forms/' + data.formId + '/bg-' + data.page + '.svg';
				data.zoom = data.zoom || 1;

				self.update(data);

				self.setModel('formId', data.formId);
				self.setModel('page', data.page + 1);
				self.setModel('zoom', Math.round(data.zoom * 100));

				if (data.selected !== void 0) {
					var row = data.rows[data.selected];
					var get = rget(row);
					self.setModel('x1', get('x1'));
					self.setModel('x2', get('x2'));
					self.setModel('y1', get('y1'));
					self.setModel('y2', get('y2'));
					self.setModel('width', get('width'));
					self.setModel('size', get('size'));
					self.setModel('align', get('align'));
				}

				localStorage.setItem('formId', data.formId);
				localStorage.setItem('page', data.page);
				localStorage.setItem('selected', data.selected);
				localStorage.setItem(data.formId, JSON.stringify(data.form));
			};

			var select = function(i) {
				if (data.selected !== void 0) {
					delete data.rows[data.selected].selected;
				}
				data.selected = i;
				if (i != void 0) {
					data.rows[data.selected].selected = true;
				}
			};

			var getForm = function(formId, force) {
				if (!formId) {
					return new Promise(function(resolve, reject) {
						resolve();
					});
				}

				var formPromise;

				var cached = localStorage.getItem(formId);
				if (
					cached &&
					!force &&
					cached !== 'null' &&
					cached !== 'undefined' &&
					cached !== 'NaN'
				) {
					formPromise = new Promise(function(resolve) {
						resolve(JSON.parse(cached));
					});
				} else {
					var url = '../data/' + formId + '/form.json';
					formPromise = fetch(url).then(function(response) {
						return response.ok ? response.json() : Promise.reject(response);
					}).then(function(form) {
						for (var i = 0; i < form.rows.length; i++) {
							var row = form.rows[i];
							row.width = row.x2 - row.x1;
							row.size = row.y2 - row.y1;
						}

						var last = null;
						for (var i = 0; i < form.rows.length; i++) {
							var row = form.rows[i];
							if (!row.hasOwnProperty('append') || !last) {
								last = row;
								row.appended = row.content;
							} else {
								last.appended += row.append + row.content;
								row.skip = true;
							}
						}

						return form;
					});
				}

				return formPromise.then(function(form) {
					data.formId = formId;
					data.form = form;
				});
			};

			self.on('select-row', function(event) {
				event.preventDefault();

				var li = event.target.parentElement;
				var list = li.parentElement.children;

				var i = list.length;
				while (i > 0 && list[--i] !== li) {}
				select(i);
				update();
			});

			self.on('unselect-row', function(event) {
				event.preventDefault();
				select();
				update();
			});

			self.on('canvas-click', function(event) {
				if (data.selected !== void 0) {
					var container = self.querySelector('.canvas');
					var page = self.querySelector('.page');
					var x = Math.round((event.clientX - page.offsetLeft - container.offsetLeft + container.scrollLeft) / data.zoom / 96 * 72);
					var y = Math.round((event.clientY - page.offsetTop - container.offsetTop + container.scrollTop) / data.zoom / 96 * 72);

					var row = data.rows[data.selected];
					var get = rget(row);
					var set = rset(row);

					if (event.ctrlKey) {
						set('x2', x);
						set('y2', y);
						set('width', get('x2') - get('x1'));
						set('size', get('y2') - get('y1'));
					} else {
						if (!get('width')) {
							set('width', 100);
						}
						if (!get('size')) {
							set('size', 10);
						}
						set('x1', x);
						set('y1', y);
						set('x2', get('x1') + get('width'));
						set('y2', get('y1') + get('size'));
					}

					update();
					window.history.pushState(data.form, null);
				}
			});

			self.on('update-selected', function(event) {
				if (data.selected !== void 0) {
					var row = data.rows[data.selected];
					var get = rget(row);
					var set = rset(row);

					set('x1', self.getModel('x1'));
					set('y1', self.getModel('y1'));
					set('width', self.getModel('width'));
					set('size', self.getModel('size'));
					set('x2', get('x1') + get('width'));
					set('y2', get('y1') + get('size'));
					set('align', self.getModel('align'));

					update();
					window.history.pushState(data.form, null);
				}
			});

			self.on('update-selected-2', function(event) {
				if (data.selected !== void 0) {
					var row = data.rows[data.selected];
					var get = rget(row);
					var set = rset(row);

					set('x2', self.getModel('x2'));
					set('y2', self.getModel('y2'));
					set('width', get('x2') - get('x1'));
					set('size', get('y2') - get('y1'));

					update();
					window.history.pushState(data.form, null);
				}
			});

			self.on('change-form', function(event) {
				var formId = self.getModel('formId');

				select();
				localStorage.setItem(data.formId, JSON.stringify(data.form));

				getForm(formId).then(function() {
					data.page = 0;
					update();
				});
			});

			self.on('change-page', function(event) {
				select();
				data.page = parseInt(self.getModel('page'), 10) - 1;
				update();
			});

			self.on('change-zoom', function(event) {
				data.zoom = self.getModel('zoom') / 100;
				update();
			});

			self.on('force-update', function(event) {
				event.preventDefault();
				var formId = self.getModel('formId');
				select();
				getForm(formId, true).then(function() {
					update();
					window.history.pushState(data.form, null);
				});
			});

			self.on('export', function(event) {
				event.preventDefault();

				var clone = JSON.parse(JSON.stringify(data.form));
				for (var i = 0; i < clone.rows.length; i++) {
					var row = clone.rows[i];

					delete row.width;
					delete row.size;
					delete row.appended;
					if (row.hasOwnProperty('selected')) {
						delete row.selected;
					}
					if (row.hasOwnProperty('skip')) {
						delete row.skip;
					}
				}

				var s = JSON.stringify(clone, null, 4);

				var download = document.createElement('a');
				download.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(s));
				download.setAttribute('download', 'form-' + data.formId + '.json');

				download.style.display = 'none';
				document.body.appendChild(download);
				download.click();
				document.body.removeChild(download);
			});

			data.formId = localStorage.getItem('formId');
			if (data.formId === "null") {
				data.formId = null;
			}
			data.page = parseInt(localStorage.getItem('page'), 10);
			data.selected = localStorage.getItem('selected');
			if (data.selected === "undefined" || data.selected === null) {
				data.selected = void 0;
			}
			getForm(data.formId).then(update);

			return muu.$.on(window, 'popstate', function(event) {
				data.form = event.state;
				data.form.rows.forEach(function(row, key) {
					row.selected = key === data.selected;
				});
				update();
			});
		});

		registry.registerDirective('markdown', '', function(self, element) {
			var oldValue = null;

			var update = function() {
				var value = element.dataset.value;
				if (value !== oldValue) {
					oldValue = value;
					element.innerHTML = markdown.render(value);
				}
			};

			self.on('parent-update', update);
			update();
		});

		muu.$.ready(function() {
			registry.linkAll(document);
		});
	});
})(PromiseXHR, muu, new markdownit());
