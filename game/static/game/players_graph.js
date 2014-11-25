// Colors
var green = '#74AB58';
var orange = '#FF9836';
var red = '#D3343A';
var blue = '#21BDCD';
var grayBG = '#2A2A2A';
var grayText = '#828282';
var darkGray = '#232323';
var whiteText = '#D4D4D4';
var opacity = 0.3;

// Global variables
var w = 725;
var h = 500;
var legW = 175;
var legH = 450;
var padding = 30;
var paddingL = 65;
var paddingT = 10;
var radius = 8;
var bigRadius = 10;
var cbDim = 15;
var transDuration = 300;
var norm = true;

var yAxisLabel = 'Point Difference';
var helperText = "This displays the difference between a player's number of fantasy points and the league average number of points for that position.";

// Function to move selection to front of view
d3.selection.prototype.moveToFront = function() {
	return this.each(function() {
		this.parentNode.appendChild(this);
	});
};

// Filtered datasets
var posList = ['QB', 'RB', 'WR', 'TE', 'D/ST', 'K'];
//var posDatasets = [];
var normDataset = [];
for (var i = 0; i < posList.length; i++) {
	var current = dataset.filter(function(element) {
		return element['player']['position']['abbr'] == posList[i] && 
			!isNaN(parseFloat(element['data']['points']));
	});
	//posDatasets.push(current);

	// Compute average and normalized dataset
	var average = 0;
	var count = 0;
	for (var j = 0; j < current.length; j++) {
		var curPts = current[j]['data']['points']
		average += curPts;
		if (curPts != 0) count += 1;
	}
	average = average / (count + 1.0);
	var norm = current.map(function(element) {
		var newPts = element['data']['points'] - average;
		return {
			'name':element['player']['name'], 
			'id':element['player']['id'],
			'pos':element['player']['position']['abbr'], 
			'pts':element['data']['points'],
			'normPts':newPts
		};
	});
	normDataset = normDataset.concat(norm);
}

var minNorm = d3.min(normDataset, function(d) { return d['normPts']; }) - bigRadius*2;
var maxNorm = d3.max(normDataset, function(d) { return d['normPts']; }) + bigRadius*2;
var minRaw = d3.min(normDataset, function(d) { return d['pts']; }) - bigRadius*2;
var maxRaw = d3.max(normDataset, function(d) { return d['pts']; }) + bigRadius*2;

// Create SVG element
var svg = d3.select('#players-graph-container')
	.append('svg')
	.attr('width', w)
	.attr('height', h)
	.attr('id', 'players-svg');

// Create scales and axes
var xScale = d3.scale.ordinal()
	.domain(d3.range(posList.length))
	.rangeRoundBands([paddingL, w-padding], 0.05);
var yScaleNorm = d3.scale.pow().exponent(0.6)
	.domain([minNorm, maxNorm])
	.range([h-padding, paddingT]);
var yScaleRaw = d3.scale.linear()
	.domain([minRaw, maxRaw])
	.range([h-padding, paddingT]);

var colorScale = d3.scale.linear()
	.domain([minNorm, 0, maxNorm])
	.range([red, whiteText, green]);

var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient('bottom')
	.tickValues(posList);
var yAxisNorm = d3.svg.axis()
	.scale(yScaleNorm)
	.orient('left')
	.ticks(5);
var yAxisRaw = d3.svg.axis()
	.scale(yScaleRaw)
	.orient('left')
	.ticks(5);

// Draw axes
svg.append('g')
	.attr('class', 'axis xAxis')
	.attr('transform', 'translate(0,' + (h - padding) + ')')
	.call(xAxis);
svg.append('g')
	.attr('class', 'axis yAxis')
	.attr('transform', 'translate(' + paddingL + ',0)')
	.call(yAxisNorm);

// Y axis label
svg.append('text')
	.attr('class', 'axis-label')
	.attr('id', 'y-axis-label')
    .attr('x', 0-(h/2))
    .attr('y', padding)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisLabel);

/*********************************************************************/
/* CIRCLES */
/*********************************************************************/

// Draw circles!
svg.selectAll('circle')
	.data(normDataset, function(d) { return d['name']+d['pos']; })
	.enter()
	.append('svg:a')
	.attr('class', 'circle-link')
	.attr('xlink:href', function(d) { return d['id']; })
	.append('circle')
	.attr('cx', function(d) {
		return xScale(posList.indexOf(d['pos'])) + (xScale.rangeBand() / 2.0);
	})
	.attr('cy', function(d) {
		return yScaleNorm(d['normPts']);
	})
	.attr('r', radius)
	.attr('fill', function(d) {
		return colorScale(d['normPts']);
	})
	.attr('opacity', opacity)
	.on('mouseover', function(d) {
			var curCircle = d3.select(this);
			curCircle.attr('opacity', 1.0);
			curCircle.attr('r', bigRadius);
			curCircle.moveToFront();

			// Show hover tooltip
			d3.select('#player-name').text(d['name']);
			d3.select('#player-pts')
				.text(norm ? parseFloat(d['normPts']).toFixed(2) : d['pts'])
				.style('color', colorScale(d['normPts']));

			// Get position for tooltip
			var matrix = this.getScreenCTM()
                .translate(+curCircle.attr('cx'),
                           +curCircle.attr('cy'));
			var xPosition = window.pageXOffset + matrix.e;
			var yPosition = window.pageYOffset + matrix.f;

			d3.select('#player-tooltip')
				.style('left', xPosition + 'px')
				.style('top', yPosition + 'px')
				.classed('hidden', false);
		})
		.on('mouseout', function(d) {
			// Hide the tooltip
			d3.select('#player-tooltip').classed('hidden', true);

			// Restore color
			d3.select(this).attr('opacity', opacity);
			d3.select(this).attr('r', radius);
		});

/*********************************************************************/
/* LEGEND */
/*********************************************************************/

// Draw legend
var curY = legH - 150;
var legSvg = d3.select('#players-legend-container')
	.append('svg')
	.attr('width', legW)
	.attr('height', legH)
	.attr('id', 'players-legend');
legSvg.append('text')
	.attr('class', 'span-header')
	.attr('text-anchor', 'middle')
	.attr('x', legW / 2)
	.attr('y', curY)
	.attr('fill', grayText)
	.text('Legend')

// Draw checkbox
curY += 20;
var checkbox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'data-checkbox')
	.attr('transform', 'translate(2,'+curY+')');
checkbox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
checkbox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
checkbox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+10)+','+13+')')
	.text('Show normalized data');

// Add helper text
curY += 35;
var helperTextArr = helperText.split(' ');
var helperText = legSvg.append('text')
	.attr('class', 'legend-text-small')
	.attr('width', legW)
	.attr('x', 2)
	.attr('y', curY)
	.text(helperTextArr.slice(0,6).join(' '));
helperText.append('tspan')
	.attr('x', 2)
	.attr('dy', '1em')
	.text(helperTextArr.slice(6,12).join(' '));
helperText.append('tspan')
	.attr('x', 2)
	.attr('dy', '1em')
	.text(helperTextArr.slice(12,18).join(' '));
helperText.append('tspan')
	.attr('x', 2)
	.attr('dy', '1em')
	.text(helperTextArr.slice(18,helperTextArr.length).join(' '));

// Draw color scale
curY += 60;
var gradient = legSvg.append('svg:defs')
  	.append('svg:linearGradient')
    .attr('id', 'gradient')
    .attr('x1', '0%')
    .attr('y1', '50%')
    .attr('x2', '100%')
    .attr('y2', '50%')
    .attr('spreadMethod', 'pad');
gradient.append('svg:stop')
    .attr('offset', '0%')
    .attr('stop-color', red)
    .attr('stop-opacity', 1);
gradient.append('svg:stop')
    .attr('offset', '50%')
    .attr('stop-color', whiteText)
    .attr('stop-opacity', 1);
gradient.append('svg:stop')
    .attr('offset', '100%')
    .attr('stop-color', green)
    .attr('stop-opacity', 1);

legSvg.append('rect')
	.attr('width', legW)
	.attr('height', 10)
	.attr('x', 0)
	.attr('y', curY)
	.style('fill', 'url(#gradient)');
curY += 30;
legSvg.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate(0,' + curY + ')')
	.text('Below');
legSvg.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'middle')
	.attr('transform', 'translate(' + (legW/2) + ',' + curY + ')')
	.text('Average');
legSvg.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'right')
	.attr('transform', 'translate(' + (legW-padding-2) + ',' + curY + ')')
	.text('Above');

// Add functionality to checkbox
d3.select('.checkbox-container').on('click', function() {

	// Toggle visibility of checkbox
	var inner = d3.select(this).select('.checkbox-inner');
	if (inner.attr('visibility') == 'hidden') {
		inner.attr('visibility', 'visible');
		norm = true;
		
		// Change scale
		svg.select('.yAxis')
			.transition()
			.duration(transDuration)
			.call(yAxisNorm);

	} else {
		inner.attr('visibility', 'hidden');
		norm = false;

		// Change scale
		svg.select('.yAxis')
			.transition()
			.duration(transDuration)
			.call(yAxisRaw);
	}

	// Change dataset accordingly
	svg.selectAll('circle')
		.transition()
		.duration(transDuration)
		.attr('cy', function(d) {
			return norm ? yScaleNorm(d['normPts']) : yScaleRaw(d['pts']);
		});

	// Change axis text
	svg.select('#y-axis-label')
		.text(norm ? yAxisLabel : 'Fantasy Points');

	// Change hover tooltip text
	d3.select('#player-pts-header')
		.text(norm ? (yAxisLabel+': ') : 'Fantasy Points: ');

});
