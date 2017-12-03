	var createApp = require('./app');
	var MarkdownIt = require('markdown-it');
	var Mustache = require('mustache');

	var markdown = new MarkdownIt();

	// register service worker
	if ('serviceWorker' in navigator) {
		navigator.serviceWorker.register('sw.js').then(function(reg) {
			console.log('Registration succeeded. Scope is ' + reg.scope);
		}).catch(function(error) {
			console.log('Registration failed with ' + error);
		});
	}

	fetch('template.html').then(function(response) {
		return response.ok ? response.text() : Promise.reject(response);
	}).then(function(template) {
		Mustache.parse(template);

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

			var select = function(state, i) {
				if (state.selected !== void 0) {
					delete state.rows[state.selected].isSelected;
				}
				state.selected = i;
				if (i != void 0) {
					state.rows[state.selected].isSelected = true;
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

				return formPromise;
			};

			var onSelectRow = function(event, state) {
				event.preventDefault();

				var li = event.target.parentElement;
				var list = li.parentElement.children;

				var i = list.length;
				while (i > 0 && list[--i] !== li) {}
				select(state, i);

				return state;
			};

			var onUnselectRow = function(event, state) {
				event.preventDefault();
				select(state);
				return state;
			};

			var onCanvasClick = function(event, state) {
				if (state.selected !== void 0) {
					var container = document.querySelector('.canvas');
					var page = document.querySelector('.page');
					var x = Math.round((event.clientX - page.offsetLeft - container.offsetLeft + container.scrollLeft) / state.zoom / 96 * 72);
					var y = Math.round((event.clientY - page.offsetTop - container.offsetTop + container.scrollTop) / state.zoom / 96 * 72);

					var row = state.rows[state.selected];
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

					window.history.pushState(state.form, null);
					return state;
				}
			};

			var onUpdateSelected = function(event, state) {
				if (state.selected !== void 0) {
					var row = state.rows[state.selected];
					var get = rget(row);
					var set = rset(row);

					set('x1', app.getModel('x1'));
					set('y1', app.getModel('y1'));
					set('width', app.getModel('width'));
					set('size', app.getModel('size'));
					set('x2', get('x1') + get('width'));
					set('y2', get('y1') + get('size'));
					set('align', app.getModel('align'));

					window.history.pushState(state.form, null);
					return state;
				}
			};

			var onUpdateSelected2 = function(event, state) {
				if (state.selected !== void 0) {
					var row = state.rows[state.selected];
					var get = rget(row);
					var set = rset(row);

					set('x2', app.getModel('x2'));
					set('y2', app.getModel('y2'));
					set('width', get('x2') - get('x1'));
					set('size', get('y2') - get('y1'));

					window.history.pushState(state.form, null);
					return state;
				}
			};

			var onChangeForm = function(event, state) {
				var formId = app.getModel('formId');

				select(state);
				localStorage.setItem(state.formId, JSON.stringify(state.form));

				return getForm(formId).then(function(form) {
					state.formId = formId;
					state.form = form;
					state.page = 0;
					return state;
				});
			};

			var onChangePage = function(event, state) {
				select(state);
				state.page = app.getModel('page') - 1;
				return state;
			};

			var onChangeZoom = function(event, state) {
				state.zoom = app.getModel('zoom') / 100;
				return state;
			};

			var onForceUpdate = function(event, state) {
				event.preventDefault();
				var formId = app.getModel('formId');
				select(state);
				return getForm(formId, true).then(function(form) {
					state.form = form;
					window.history.pushState(state.form, null);
					return state;
				});
			};

			var onExport = function(event, state) {
				event.preventDefault();

				var clone = JSON.parse(JSON.stringify(state.form));
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
				download.setAttribute('download', 'form-' + state.formId + '.json');

				download.style.display = 'none';
				document.body.appendChild(download);
				download.click();
				document.body.removeChild(download);
			};

			// main
			var app = createApp(function(state) {
				if (state.form) {
					state.rows = state.form.rows.filter(function(row) {
						if (!row.skip) {
							row.rendered = row.rendered || markdown.render(row.appended);
						}

						return row.page === state.page;
					});
				} else {
					state.rows = void 0;
					state.selected = void 0;
				}
				state.bg = '../static/forms/' + state.formId + '/bg-' + state.page + '.svg';
				state.zoom = state.zoom || 1;

				return Mustache.render(template, state);
			}, function(state) {
				app.setModel('formId', state.formId);
				app.setModel('page', state.page + 1);
				app.setModel('zoom', Math.round(state.zoom * 100));

				if (state.selected !== void 0) {
					var row = state.rows[state.selected];
					var get = rget(row);

					app.setModel('x1', get('x1'));
					app.setModel('x2', get('x2'));
					app.setModel('y1', get('y1'));
					app.setModel('y2', get('y2'));
					app.setModel('width', get('width'));
					app.setModel('size', get('size'));
					app.setModel('align', get('align'));
				}

				localStorage.setItem('formId', state.formId);
				localStorage.setItem('page', state.page);
				localStorage.setItem('selected', state.selected);
				localStorage.setItem(state.formId, JSON.stringify(state.form));
			});

			app.bindEvent('[data-onclick="select-row"]', 'click', onSelectRow);
			app.bindEvent('[data-onclick="unselect-row"]', 'click', onUnselectRow);
			app.bindEvent('[data-onclick="canvas-click"]', 'click', onCanvasClick);
			app.bindEvent('[data-onchange="update-selected"]', 'change', onUpdateSelected);
			app.bindEvent('[data-onchange="update-selected-2"]', 'change', onUpdateSelected2);
			app.bindEvent('[data-onchange="change-form"]', 'change', onChangeForm);
			app.bindEvent('[data-onchange="change-page"]', 'change', onChangePage);
			app.bindEvent('[data-onchange="change-page"]', 'change', onChangePage);
			app.bindEvent('[data-onchange="change-zoom"]', 'change', onChangeZoom);
			app.bindEvent('[data-onclick="force-update"]', 'click', onForceUpdate);
			app.bindEvent('[data-onclick="export"]', 'click', onExport);

			var initial = {};
			initial.formId = localStorage.getItem('formId');
			if (initial.formId === "null") {
				initial.formId = null;
			}
			initial.page = parseInt(localStorage.getItem('page'), 10);
			initial.selected = localStorage.getItem('selected');
			if (initial.selected === "undefined" || initial.selected === null) {
				initial.selected = void 0;
			}

			getForm(initial.formId).catch(function() {
				return null;
			}).then(function(form) {
				initial.form = form;
				app.init(initial, document.body);
			});

			app.bindEvent(window, 'popstate', function(event, state) {
				state.form = event.state;
				state.form.rows.forEach(function(row, key) {
					row.selected = key === state.selected;
				});
				return state;
			});
	});
