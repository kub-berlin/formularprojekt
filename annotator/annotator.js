(function(xhr, muu) {
	'use strict';

	var registry = new muu.Registry();

	xhr.get('template.html').then(function(template) {
		registry.registerDirective('forms', template, function(self) {
			var data = {};

			var rget = function(row) {
				return function(key) {
					return data.layer2 ? row[key + '2'] : row[key];
				};
			};

			var rset = function(row) {
				return function(key, value) {
					if (data.layer2) {
						row[key + '2'] = value;
					} else {
						row[key] = value;
					}
				};
			};

			var update = function() {
				if (data.form) {
					data.rows = data.form.rows.filter(function(row) {
						return row.page === data.page;
					});
				} else {
					data.rows = void 0;
					data.selected = void 0;
				}
				data.bg = '../static/forms/' + data.formId + '/bg-' + data.page + '.png';
				data.layer1 = !data.layer2;

				self.update(data);

				self.setModel('formId', data.formId);
				self.setModel('page', data.page + 1);

				if (data.selected !== void 0) {
					var row = data.rows[data.selected];
					var get = rget(row);
					self.setModel('x1', get('x1'));
					self.setModel('x2', get('x2'));
					self.setModel('y1', get('y1'));
					self.setModel('y2', get('y2'));
					self.setModel('width', get('width'));
					self.setModel('size', get('size'));
				}

				localStorage.setItem('formId', data.formId);
				localStorage.setItem('page', data.page);
				localStorage.setItem('selected', data.selected);
				localStorage.setItem(data.formId, JSON.stringify(data.form));
			}

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
					formPromise = xhr.getJSON(url).then(function(form) {
						for (var i = 0; i < form.rows.length; i++) {
							var row = form.rows[i];
							row.width = row.x2 - row.x1;
							row.size = row.y2 - row.y1;
							row.width2 = row.x22 - row.x12;
							row.size2 = row.y22 - row.y12;
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
				while (i > 0 && list[--i] !== li) {};
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
					var x = Math.round(event.clientX - page.offsetLeft - container.offsetLeft + container.scrollLeft);
					var y = Math.round(event.clientY - page.offsetTop - container.offsetTop + container.scrollTop);

					var row = data.rows[data.selected];
					var get = rget(row);
					var set = rset(row);

					if (event.ctrlKey) {
						set('x2', x);
						set('y2', y);
						set('width', get('x2') - get('x1'));
						set('size', get('y2') - get('y1'));
					} else {
						set('x1', x);
						set('y1', y);
						set('x2', get('x1') + get('width'));
						set('y2', get('y1') + get('size'));
					}

					update();
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

			self.on('change-layer', function(event) {
				data.layer2 = self.getModel('layer2');
				update();
			});

			self.on('force-update', function(event) {
				event.preventDefault();
				var formId = self.getModel('formId');
				select();
				getForm(formId, true).then(update);
			});

			self.on('export', function(event) {
				event.preventDefault();

				var clone = JSON.parse(JSON.stringify(data.form));
				for (var i = 0; i < clone.rows.length; i++) {
					var row = clone.rows[i];

					delete row.width;
					delete row.size;
					delete row.width2;
					delete row.size2;
					if (row.hasOwnProperty('selected')) {
						delete row.selected;
					}
				}

				var s = JSON.stringify(clone, null, 2);

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
		});

		muu.$.ready(function() {
			registry.linkAll(document);
		});
	});
})(PromiseXHR, muu);
