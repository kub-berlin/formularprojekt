/*
Often, translated strings are longer than the source strings. This means that
strings can overlap. This file is supposed to "shake" the strings a bit to
avoid overlaps.

It uses 4 different operations:

-	reducing line-height
-	increasing width
-	reducing font-size
-	reducing top position

Each operations is assigned a cost. The combination of operations with the
minimum cost is used.

Only bottom overlap is removed. This fits well because the width is fixed in
the annotation process. So rows can only grow to the bottom.

Note that overlap with structures from the background image can not be
prevented with this approach.
*/

(function() {
	const getRect = function(el) {
		var r = el.getBoundingClientRect();
		return {
			x1: r.x,
			x2: r.x + r.width,
			y1: r.y,
			y2: r.y + r.height,
		};
	};

	window.getContext = function(rowEl) {
		let pageEl = rowEl.closest('.page');
		let rows = pageEl.querySelectorAll('.row');

		let row = getRect(rowEl);
		let top, bottom, left, right;
		let topEl, bottomEl, leftEl, rightEl;

		for (let otherEl of rows) {
			if (otherEl !== rowEl) {
				let other = getRect(otherEl);

				if (other.x1 < row.x2 && other.x2 > row.x1) {
					if (other.y1 < row.y1 && (!top || other.y2 > top.y2)) {
						top = other;
						topEl = otherEl;
					} else if (other.y1 > row.y1 && (!bottom || other.y1 < bottom.y1)) {
						bottom = other;
						bottomEl = otherEl;
					}
				}
				// left and right are not overlapping
				if (other.y1 < row.y2 && other.y2 > row.y1) {
					if (other.x2 < row.x1 && (!left || other.x2 > left.x2)) {
						left = other;
						leftEl = otherEl;
					} else if (other.x1 > row.x2 && (!right || other.x1 < right.x1)) {
						right = other;
						rightEl = otherEl;
					}
				}
			}
		}

		return {
			top: topEl,
			bottom: bottomEl,
			left: leftEl,
			right: rightEl,
		};
	};

	const getTop = function(rowEl, ctx) {
		let pageEl = rowEl.closest('.page');
		var row = getRect(rowEl);
		var page = getRect(pageEl);
		var top = {y2: page.y1};
		if (ctx.top) {
			top = getRect(ctx.top);
		}
		return row.y1 - top.y2;
	};

	const getBottom = function(rowEl, ctx) {
		let pageEl = rowEl.closest('.page');
		var row = getRect(rowEl);
		var page = getRect(pageEl);
		var bottom = {y1: page.y2};
		if (ctx.bottom) {
			bottom = getRect(ctx.bottom);
		}
		return bottom.y1 - row.y2;
	};

	const getLeft = function(rowEl, ctx) {
		let pageEl = rowEl.closest('.page');
		var row = getRect(rowEl);
		var page = getRect(pageEl);
		var left = {x2: page.x1};
		if (ctx.left) {
			left = getRect(ctx.left);
		}
		return row.x1 - left.x2;
	};

	const getRight = function(rowEl, ctx) {
		let pageEl = rowEl.closest('.page');
		var row = getRect(rowEl);
		var page = getRect(pageEl);
		var right = {x1: page.x2};
		if (ctx.right) {
			right = getRect(ctx.right);
		}
		return right.x1 - row.x2;
	};

	for (let pageEl of document.querySelectorAll('.page')) {
		let rows = pageEl.querySelectorAll('.row');
		for (let rowEl of rows) {
			let ctx = getContext(rowEl, rows);

			let _top = getTop(rowEl, ctx);
			let _right = getRight(rowEl, ctx);
			let bottom = () => getBottom(rowEl, ctx);

			let baseWidth = parseInt(getComputedStyle(rowEl).width, 10);
			let baseFontSize = parseInt(getComputedStyle(rowEl).fontSize, 10);
			let baseTop = parseInt(getComputedStyle(rowEl).top, 10);

			const moveUp = function(max) {
				var top = baseTop;
				rowEl.style.top = top + 'px';
				if (max !== 0 && bottom() < 0 && _top > 0) {
					top -= Math.min(-bottom(), _top, (max || Infinity));
					rowEl.style.top = top + 'px';
				}
			};

			const widen = function(factor) {
				var width = baseWidth;
				if (factor !== 0) {
					width += _right * (factor || 1);
				}
				rowEl.style.width = width + 'px';
			};

			if (bottom() < 0) {
				let solution = [];
				let minCost = 10000;

				let cost = [0];
				for (let lineHeight = 1.2; lineHeight >= 0.9; lineHeight -= 0.1) {
					cost[0] += 1;
					if (cost[0] >= minCost) break;
					rowEl.style.lineHeight = lineHeight;

					cost.unshift(cost[0]);
					for (let widenFactor = 0; widenFactor < 1; widenFactor += 0.1) {
						cost[0] += 5;
						if (cost[0] >= minCost) break;
						widen(widenFactor);

						cost.unshift(cost[0]);
						for (let fontSize = baseFontSize; fontSize >= 6; fontSize--) {
							cost[0] += Math.pow(baseFontSize - fontSize + 1, 2) * 5;
							if (cost[0] >= minCost) break;
							rowEl.style.fontSize = fontSize + 'px';

							cost.unshift(cost[0]);
							for (let maxUp of [0, 2, 5, Infinity]) {
								cost[0] += 0.5;
								moveUp(maxUp);
								if (cost[0] >= minCost) break;

								if (bottom() >= 0) {
									solution = [lineHeight, widenFactor, fontSize, maxUp];
									minCost = cost[0];
									break;
								}
							}
							cost.shift();
						}
						cost.shift();
					}
					cost.shift();
				}

				rowEl.style.lineHeight = solution[0];
				widen(solution[1]);
				rowEl.style.fontSize = solution[2] + 'px';
				moveUp(solution[3]);
				// console.log(baseFontSize, solution, minCost);
				// rowEl.style.backgroundColor = 'red';
			};
		}
	}
})();
