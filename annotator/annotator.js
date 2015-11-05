(function(xhr, muu) {
	'use strict';

	var registry = new muu.Registry();

	xhr.get('template.html').then(function(template) {
		registry.registerDirective('forms', template, function(self) {
			var data = {};

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

				self.update(data);

				self.setModel('formId', data.formId);
				self.setModel('page', data.page + 1);

				if (data.selected !== void 0) {
					var row = data.rows[data.selected];
					self.setModel('x1', row.x1);
					self.setModel('x2', row.x2);
					self.setModel('y1', row.y1);
					self.setModel('y2', row.y2);
					self.setModel('width', row.width);
					self.setModel('size', row.size);
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

					if (event.ctrlKey) {
						row.x2 = x;
						row.y2 = y;
						row.width = row.x2 - row.x1;
						row.size = row.y2 - row.y1;
					} else {
						row.x1 = x;
						row.y1 = y;
						row.x2 = row.x1 + row.width;
						row.y2 = row.y1 + row.size;
					}

					update();
				}
			});

			self.on('update-selected', function(event) {
				if (data.selected !== void 0) {
					var row = data.rows[data.selected];

					row.x1 = parseInt(self.getModel('x1'), 10);
					row.y1 = parseInt(self.getModel('y1'), 10);
					row.width = parseInt(self.getModel('width'), 10);
					row.size = parseInt(self.getModel('size'), 10);
					row.x2 = row.x1 + row.width;
					row.y2 = row.y1 + row.size;

					update();
				}
			});

			self.on('update-selected-2', function(event) {
				if (data.selected !== void 0) {
					var row = data.rows[data.selected];

					row.x2 = parseInt(self.getModel('x2'), 10);
					row.y2 = parseInt(self.getModel('y2'), 10);
					row.width = row.x2 - row.x1;
					row.size = row.y2 - row.y1;

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
