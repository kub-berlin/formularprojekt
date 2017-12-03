var setDOM = require('set-dom');

module.exports = function(template, afterUpdate) {
    var element;
    var state;
    var events = [];
    var self = {};

    var initEvent = function(element, fn) {
        if (!element.$init) {
            setTimeout(function() {
                fn({target: element});
            });
            element.$init = true;
        }
    };

    var attachEventListeners = function() {
        events.forEach(function(ev) {
            var selector = ev[0];
            var eventName = ev[1];
            var fn = ev[2];

            var elements = [selector];
            if (typeof selector === 'string') {
                elements = element.querySelectorAll(selector);
            }

            for (var i = 0; i < elements.length; i++) {
                if (eventName === 'init') {
                    initEvent(elements[i], fn);
                } else {
                    elements[i].addEventListener(eventName, fn);
                }
            }
        });
    };

    var update = function(newState) {
        var newTree = document.createElement('div');
        newTree.innerHTML = template(newState);
        setDOM(element, newTree);
        attachEventListeners();
        state = newState;

        if (afterUpdate) {
            afterUpdate(newState)
        }
    };

    var eventWrapper = function(fn) {
        return function(event) {
            var val = fn(event, Object.assign({}, state), self);
            Promise.resolve(val).then(function(newState) {
                if (newState != null) {
                    update(newState);
                }
            });
        };
    };

    self.init = function(newState, wrapper) {
        element = document.createElement('div');
        wrapper.innerHTML = '';
        wrapper.appendChild(element);
        update(newState);
    };

    self.bindEvent = function(selector, eventName, fn) {
        events.push([selector, eventName, eventWrapper(fn)]);
    };

    self.getModel = function(name) {
        var el = element.querySelector('[name=' + name + ']');
        if (el) {
            if (el.getAttribute('type') === 'number') {
                return parseFloat(el.value);
            } else {
                return el.value;
            }
        }
    };

    self.setModel = function(name, value) {
        var el = element.querySelector('[name=' + name + ']');
        el.value = value;
    };

    return self;
};
