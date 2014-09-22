// Dataset: list of dictionaries
// d['players'][0][0] = player object
// d['players'][0][1] = list of numbers
//		0 = totalPtsEarned
//		1 = avg FFPG
//		2 = total WR/TE points allowed
//		3 = total RB points allowed
//		4 = average WR/TE/RB points allowed per game

// Colors
var green = '#74AB58';
var orange = '#FF9836';
var red = '#D3343A';
var blue = '#21BDCD';
var grayBG = '#2A2A2A';
var grayText = '#828282';
var darkGray = '#232323';
var white = '#D4D4D4';

// Global variables
var w = 800;
var h = 500;
var paddingL = 50;
var paddingTop = 10;
var midPadding = 13;
var halfH = h/2;

var svg = d3.select('#dst-graph-container')
	.append('svg')
	.attr('width', w)
	.attr('height', h)
	.attr('id', 'dst-svg');

// Scales for axes
var xScale = d3.scale.ordinal()
	.domain(d3.range(dataset.length))
	.rangeRoundBands([paddingL, w], 0.1);
var minYTop = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][0]); })-1);
var maxYTop = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][0]); });
var yScaleTop = d3.scale.linear()
	.domain([minYTop, maxYTop])
	.range([halfH-midPadding, paddingTop]);

var minYBottom = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][2])+parseFloat(d['players'][0][1][3]); })-1);
var maxYBottom = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][2])+parseFloat(d['players'][0][1][3]); });
var yScaleBottom = d3.scale.linear()
	.domain([minYBottom, maxYBottom])
	.range([midPadding, halfH-paddingTop]);

// Color scales
var greenScale = d3.scale.linear()
	.domain([minYTop, maxYTop])
	.range([white, green]);
var redScale = d3.scale.linear()
	.domain([minYBottom, maxYBottom])
	.range([white, red]);

// Draw axes
var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient('bottom')
	.tickValues(dataset.map(function(d) { return d['players'][0][0]['team']['abbr'].toUpperCase(); }));
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(0,'+(halfH-midPadding)+')')
	.call(xAxis);
svg.append('g')
	.attr('class', 'axis no-text')
	.attr('transform', 'translate(0,'+(halfH+midPadding)+')')
	.call(xAxis);
var yAxisTop = d3.svg.axis()
	.scale(yScaleTop)
	.orient('left')
	.ticks(5);
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(' + paddingL + ',0)')
	.call(yAxisTop);
var yAxisBottom = d3.svg.axis()
	.scale(yScaleBottom)
	.orient('left')
	.ticks(5);
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(' + paddingL + ',' + halfH + ')')
	.call(yAxisBottom);

// Y Axis labels
svg.append('text')
	.attr('class', 'axis-label')
    .attr('x', 0-halfH/2)
    .attr('y', 10)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text('Total Fantasy Points Scored');
svg.append('text')
	.attr('class', 'axis-label')
    .attr('x', 0-3*halfH/2)
    .attr('y', 10)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text('Total Fantasy Points Allowed (WR/TE/RB)');



// Draw rectangles
svg.selectAll('.top-rect')
	.data(dataset)
	.enter()
	.append('svg:a')
	.attr('xlink:href', function(d) { return player_url + d['players'][0][0]['id']; })
	.append('rect')
	.attr('class', 'top-rect')
	.attr('x', function(d, i) {
		return xScale(i);
	})
	.attr('y', function(d) {
		return yScaleTop(d['players'][0][1][0]);
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return halfH - midPadding - yScaleTop(d['players'][0][1][0]);
	})
	.attr('fill', function(d) {
		return greenScale(d['players'][0][1][0]);
	})
	.on('mouseover', function(d, i) {
		d3.select('#green-text-' + i).classed('hidden', false);
	})
	.on('mouseout', function(d, i) {
		d3.select('#green-text-' + i).classed('hidden', true);
	});
svg.selectAll('.bottom-rect')
	.data(dataset)
	.enter()
	.append('svg:a')
	.attr('xlink:href', function(d) { return player_url + d['players'][0][0]['id']; })
	.append('rect')
	.attr('class', 'bottom-rect')
	.attr('x', function(d, i) {
		return xScale(i);
	})
	.attr('y', function(d) {
		return halfH + midPadding;
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return yScaleBottom(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - midPadding;
	})
	.attr('fill', function(d) {
		return redScale(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]);
	})
	.on('mouseover', function(d, i) {
		d3.select('#red-text-' + i).classed('hidden', false);
	})
	.on('mouseout', function(d, i) {
		d3.select('#red-text-' + i).classed('hidden', true);
	});

// Create text
svg.selectAll('.green-text')
	.data(dataset)
	.enter()
	.append('text')
	.attr('class', 'green-text hidden')
	.attr('id', function(d, i) { return 'green-text-' + i; })
	.text(function(d) {
		return d['players'][0][1][0];
	})
	.attr('text-anchor', 'middle')
	.attr('x', function(d, i) {
		return xScale(i) + xScale.rangeBand() / 2;
	})
	.attr('y', function(d) {
		return yScaleTop(d['players'][0][1][0]) + paddingTop + 5;
	})
	.attr('fill', darkGray)
	.attr('font-size', '12px');
svg.selectAll('.red-text')
	.data(dataset)
	.enter()
	.append('text')
	.attr('class', 'red-text hidden')
	.attr('id', function(d, i) { return 'red-text-' + i; })
	.text(function(d) {
		return parseFloat(d['players'][0][1][2]) + d['players'][0][1][3];
	})
	.attr('text-anchor', 'middle')
	.attr('x', function(d, i) {
		return xScale(i) + xScale.rangeBand() / 2;
	})
	.attr('y', function(d) {
		return halfH + yScaleBottom(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - 5;
	})
	.attr('fill', darkGray)
	.attr('font-size', '12px');

