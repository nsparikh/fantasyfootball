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
var opacity = 0.8;

// Global variables
var w = 800;
var legW = 110;
var totalW = 910;
var h = 500;
var paddingL = 50;
var paddingTop = 10;
var midPadding = 13;
var halfH = h/2;
var cbDim = 13;
var duration = 300;

// Text changes
var yAxisTopTotalTotalText = 'Total Fantasy Points Scored';
var yAxisBottomTotalTotalText = 'Total Fantasy Points Allowed (WR/TE/RB)';
var yAxisTopTotalAvgText = 'Average Fantasy Points Per Game';
var yAxisBottomTotalAvgText = 'Average Fantasy Points Allowed Per Game';

var svg = d3.select('#dst-graph-container')
	.append('svg')
	.attr('width', totalW)
	.attr('height', h)
	.attr('id', 'dst-svg');

// Scales for axes
var xScale = d3.scale.ordinal()
	.domain(d3.range(dataset.length))
	.rangeRoundBands([paddingL, w], 0.05);
var minYTopTotal = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][0]); })-1);
var maxYTopTotal = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][0]); });
var yScaleTopTotal = d3.scale.linear()
	.domain([minYTopTotal, maxYTopTotal])
	.range([halfH-midPadding, paddingTop]);
var minYTopAvg = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][1]); })-1);
var maxYTopAvg = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][1]); });
var yScaleTopAvg = d3.scale.linear()
	.domain([minYTopAvg, maxYTopAvg])
	.range([halfH-midPadding, paddingTop]);

var minYBottomTotal = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][2])+parseFloat(d['players'][0][1][3]); })-1);
var maxYBottomTotal = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][2])+parseFloat(d['players'][0][1][3]); });
var yScaleBottomTotal = d3.scale.linear()
	.domain([minYBottomTotal, maxYBottomTotal])
	.range([midPadding, halfH-paddingTop]);
var minYBottomAvg = Math.min(0, d3.min(dataset, function(d) { return parseFloat(d['players'][0][1][4]); })-1);
var maxYBottomAvg = d3.max(dataset, function(d) { return parseFloat(d['players'][0][1][4]); });
var yScaleBottomAvg = d3.scale.linear()
	.domain([minYBottomAvg, maxYBottomAvg])
	.range([midPadding, halfH-paddingTop]);

// Color scales
var greenScaleTotal = d3.scale.linear()
	.domain([minYTopTotal, maxYTopTotal])
	.range([white, green]);
var redScaleTotal = d3.scale.linear()
	.domain([minYBottomTotal, maxYBottomTotal])
	.range([white, red]);
var greenScaleAvg = d3.scale.linear()
	.domain([minYTopAvg, maxYTopAvg])
	.range([white, green]);
var redScaleAvg = d3.scale.linear()
	.domain([minYBottomAvg, maxYBottomAvg])
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
var yAxisTopTotal = d3.svg.axis()
	.scale(yScaleTopTotal)
	.orient('left')
	.ticks(5);
var yAxisTopAvg = d3.svg.axis()
	.scale(yScaleTopAvg)
	.orient('left')
	.ticks(5);
svg.append('g')
	.attr('class', 'axis')
	.attr('id', 'y-axis-top')
	.attr('transform', 'translate(' + paddingL + ',0)')
	.call(yAxisTopTotal);
var yAxisBottomTotal = d3.svg.axis()
	.scale(yScaleBottomTotal)
	.orient('left')
	.ticks(5);
var yAxisBottomAvg = d3.svg.axis()
	.scale(yScaleBottomAvg)
	.orient('left')
	.ticks(5);
svg.append('g')
	.attr('class', 'axis')
	.attr('id', 'y-axis-bottom')
	.attr('transform', 'translate(' + paddingL + ',' + halfH + ')')
	.call(yAxisBottomTotal);

// Y Axis labels
svg.append('text')
	.attr('class', 'axis-label')
	.attr('id', 'y-axis-top-text')
    .attr('x', 0-halfH/2)
    .attr('y', 10)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisTopTotalTotalText);
svg.append('text')
	.attr('class', 'axis-label')
	.attr('id', 'y-axis-bottom-text')
    .attr('x', 0-3*halfH/2)
    .attr('y', 10)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisBottomTotalTotalText);


/****************************************************************************/
// RECTANGLES
/****************************************************************************/

// Draw rectangles
svg.selectAll('.top-rect')
	.data(dataset)
	.enter()
	.append('svg:a')
	.attr('xlink:href', function(d) { return player_url + d['players'][0][0]['id']; })
	.append('rect')
	.attr('class', 'top-rect')
	.attr('id', function(d, i) { return 'rect-'+i; })
	.attr('x', function(d, i) {
		return xScale(i);
	})
	.attr('y', function(d) {
		return yScaleTopTotal(d['players'][0][1][0]);
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return halfH - midPadding - yScaleTopTotal(d['players'][0][1][0]);
	})
	.attr('fill', function(d) {
		return greenScaleTotal(d['players'][0][1][0]);
	})
	.attr('opacity', opacity)
	.on('mouseover', function(d, i) {
		d3.selectAll('.bar-text-' + i).classed('hidden', false);
		d3.selectAll('#rect-'+i).attr('opacity', 1.0);
	})
	.on('mouseout', function(d, i) {
		d3.selectAll('.bar-text-' + i).classed('hidden', true);
		d3.selectAll('#rect-'+i).attr('opacity', opacity);
	});
svg.selectAll('.bottom-rect')
	.data(dataset)
	.enter()
	.append('svg:a')
	.attr('xlink:href', function(d) { return player_url + d['players'][0][0]['id']; })
	.append('rect')
	.attr('class', 'bottom-rect')
	.attr('id', function(d, i) { return 'rect-'+i; })
	.attr('x', function(d, i) {
		return xScale(i);
	})
	.attr('y', function(d) {
		return halfH + midPadding;
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return yScaleBottomTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - midPadding;
	})
	.attr('fill', function(d) {
		return redScaleTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]);
	})
	.attr('opacity', opacity)
	.on('mouseover', function(d, i) {
		d3.selectAll('.bar-text-' + i).classed('hidden', false);
		d3.selectAll('#rect-'+i).attr('opacity', 1.0);
	})
	.on('mouseout', function(d, i) {
		d3.selectAll('.bar-text-' + i).classed('hidden', true);
		d3.selectAll('#rect-'+i).attr('opacity', opacity);
	});

// Create text
svg.selectAll('.top-text')
	.data(dataset)
	.enter()
	.append('text')
	.attr('class', function(d, i) { return 'hidden top-text bar-text-' + i; })
	.text(function(d) {
		return d['players'][0][1][0];
	})
	.attr('text-anchor', 'middle')
	.attr('x', function(d, i) {
		return xScale(i) + xScale.rangeBand() / 2;
	})
	.attr('y', function(d) {
		return yScaleTopTotal(d['players'][0][1][0]) + paddingTop + 5;
	})
	.attr('fill', darkGray)
	.attr('font-size', '12px');
svg.selectAll('.bottom-text')
	.data(dataset)
	.enter()
	.append('text')
	.attr('class', function(d, i) { return 'hidden bottom-text bar-text-' + i; })
	.text(function(d) {
		return parseFloat(d['players'][0][1][2]) + d['players'][0][1][3];
	})
	.attr('text-anchor', 'middle')
	.attr('x', function(d, i) {
		return xScale(i) + xScale.rangeBand() / 2;
	})
	.attr('y', function(d) {
		return halfH + yScaleBottomTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - 5;
	})
	.attr('fill', darkGray)
	.attr('font-size', '12px');

/****************************************************************************/
// LEGEND
/****************************************************************************/

var curY = halfH-midPadding*2;
var legSvg = svg.append('svg')
	.attr('id', 'legend-container')
	.attr('width', legW)
	.attr('height', h)
	.attr('x', w)
	.attr('y', 0);
legSvg.append('text')
	.attr('x', legW/2)
	.attr('y', curY)
	.attr('class', 'span-header')
	.attr('text-anchor', 'middle')
	.attr('fill', grayText)
	.text('Display');
var curX = 15;
curY += 10;
var totalBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'total-box')
	.attr('transform', 'translate('+curX+','+curY+')');
totalBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
totalBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
totalBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Total Points');
curY += 20;
var avgBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'avg-box')
	.attr('transform', 'translate('+curX+','+curY+')');
avgBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
avgBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'hidden');
avgBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Average FPPG');

// Add functionality to checkboxes
d3.selectAll('.checkbox-container').on('click', function(d) {
	var curId = d3.select(this).attr('id');
	var otherId = curId == 'total-box' ? 'avg-box' : 'total-box';

	// Toggle visibility
	var inner = d3.select(this).select('.checkbox-inner');
	var otherInner = d3.select('#'+otherId).select('.checkbox-inner');
	if (inner.attr('visibility') == 'hidden') {
		inner.attr('visibility', 'visible');
		otherInner.attr('visibility', 'hidden');

		var total = curId == 'total-box';

		// Transition the scales 
		d3.select('#y-axis-top')
			.transition()
			.duration(duration)
			.call(total ? yAxisTopTotal : yAxisTopAvg);
		d3.select('#y-axis-bottom')
			.transition()
			.duration(duration)
			.call(total ? yAxisBottomTotal : yAxisBottomAvg);
		d3.select('#y-axis-top-text')
			.text(total ? yAxisTopTotalTotalText : yAxisTopTotalAvgText);
		d3.select('#y-axis-bottom-text')
			.text(total ? yAxisBottomTotalTotalText : yAxisBottomTotalAvgText);

		// Transition the rectangles
		d3.selectAll('.top-rect')
			.transition()
			.duration(duration)
			.attr('y', function(d) {
				return total ? yScaleTopTotal(d['players'][0][1][0]) : yScaleTopAvg(d['players'][0][1][1]);
			})
			.attr('height', function(d) {
				return total ? (halfH - midPadding - yScaleTopTotal(d['players'][0][1][0])) :
					(halfH - midPadding - yScaleTopAvg(d['players'][0][1][1]));
			})
			.attr('fill', function(d) {
				return total ? greenScaleTotal(d['players'][0][1][0]) : 
					greenScaleAvg(d['players'][0][1][1]);
			});
		d3.selectAll('.bottom-rect')
			.transition()
			.duration(duration)
			.attr('height', function(d) {
				return total ? (yScaleBottomTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - midPadding) : 
					(yScaleBottomAvg(d['players'][0][1][4]) - midPadding);
			})
			.attr('fill', function(d) {
				return total ? (redScaleTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3])) : 
					redScaleAvg(d['players'][0][1][4]);
			});

		// Change the hover text for the rectangles
		d3.selectAll('.top-text')
			.text(function(d) {
				return total ? d['players'][0][1][0] : d['players'][0][1][1];
			})
			.attr('y', function(d) {
				return total ? (yScaleTopTotal(d['players'][0][1][0]) + paddingTop + 5) :
					(yScaleTopAvg(d['players'][0][1][1]) + paddingTop + 5);
			});
		d3.selectAll('.bottom-text')
			.text(function(d) {
				return total ? (parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) :
					d['players'][0][1][4];
			})
			.attr('y', function(d) {
				return total ? (halfH + yScaleBottomTotal(parseFloat(d['players'][0][1][2]) + d['players'][0][1][3]) - 5) :
					(halfH + yScaleBottomAvg(d['players'][0][1][4]) - 5);
			});


	} 
});


