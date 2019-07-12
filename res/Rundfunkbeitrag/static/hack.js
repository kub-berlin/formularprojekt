window.ZBS = {};
window.ZBS.panel = {};
window.ZBS.panel.wechselPanel = function(oldID, newID) {
	document.getElementById(oldID).className = 'hide';
	document.getElementById(newID).className = '';
};

window.schonAngemeldet = function(input) {
	var rowYes = document.getElementById('befreiungsform:bnr-row');
	var rowNo = document.getElementById('befreiungsform:anmeldeDatum-row');
	if (input.value === 'true') {
		rowYes.classList.remove('hide');
		rowNo.classList.add('hide');
	} else {
		rowYes.classList.add('hide');
		rowNo.classList.remove('hide');
	}
};

var createTooltip = function(html) {
	var tooltip = document.createElement('div');
	tooltip.className = 'tooltip fade bottom in';
	tooltip.style.display = 'block';
	tooltip.innerHTML = '<div class="tooltip-arrow" style="left: 48.85%"></div>';

	var inner = document.createElement('div');
	inner.className = 'tooltip-inner';
	inner.innerHTML = html;
	tooltip.appendChild(inner);

	return tooltip;
};

var initTooltip = function(el) {
	var trigger = el.parentElement.querySelector('a');
	var tooltip = createTooltip(el.dataset.originalTitle);
	var container = document.body;

	trigger.addEventListener('mouseenter', function() {
		container.appendChild(tooltip);
		var rect = el.getBoundingClientRect();
		var tooltipRect = tooltip.getBoundingClientRect();
		tooltip.style.top = rect.top + rect.height + 'px';
		tooltip.style.left = Math.max(rect.left + (rect.width - tooltipRect.width) / 2, 0) + 'px';
	});

	trigger.addEventListener('mouseleave', function() {
		container.removeChild(tooltip);
	});
};

document.addEventListener('DOMContentLoaded', function() {
	var elements = document.querySelectorAll('[data-original-title]');
	for (var i = 0; i < elements.length; i++) {
		initTooltip(elements[i]);
	}
});
