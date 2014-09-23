// Dataset: list of dictionaries
// d['players'][0][0] = player object
// d['players'][0][1] = list of numbers
//		0 = totalPtsEarned
//		1 = num weeks played
//		2 = total QB points allowed
//		3 = total RB points allowed
//		4 = total WR points allowed
//		5 = total TE points allowed
//		6 = avg QB points
//		7 = avg RB points
//		8 = avg WR points
//		9 = avg TE points

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
var yAxisTopTotalText = 'Total Fantasy Points Scored';
var yAxisBottomTotalText = 'Total Fantasy Points Allowed';
var yAxisTopAvgText = 'Average Fantasy Points Per Game';
var yAxisBottomAvgText = 'Average Fantasy Points Allowed Per Game';

var svg = d3.select('#dst-graph-container')
	.append('svg')
	.attr('width', totalW)
	.attr('height', h)
	.attr('id', 'dst-svg');

// Functions to compute values for the graph
function topYTotal(d) { return d['players'][0][1][0]; }
function topYAverage(d) { return Math.round(topYTotal(d) / (1.0 * d['players'][0][1][1]) * 100) / 100; }
function bottomYTotal(d) { 
	return d['players'][0][1][2] + d['players'][0][1][3] + d['players'][0][1][4] + d['players'][0][1][5];  
}
function bottomYAvg(d) { 
	return d['players'][0][1][6] + d['players'][0][1][7] + d['players'][0][1][8] + d['players'][0][1][9]; 
}

// Scales for axes
var xScale = d3.scale.ordinal()
	.domain(d3.range(dataset.length))
	.rangeRoundBands([paddingL, w], 0.05);
var minYTopTotal = Math.min(0, d3.min(dataset, function(d) { return topYTotal(d); })-1);
var maxYTopTotal = d3.max(dataset, function(d) { return topYTotal(d); });
var yScaleTopTotal = d3.scale.linear()
	.domain([minYTopTotal, maxYTopTotal])
	.range([halfH-midPadding, paddingTop]);
var minYTopAvg = Math.min(0, d3.min(dataset, function(d) { return topYAverage(d); })-1);
var maxYTopAvg = d3.max(dataset, function(d) { return topYAverage(d); });
var yScaleTopAvg = d3.scale.linear()
	.domain([minYTopAvg, maxYTopAvg])
	.range([halfH-midPadding, paddingTop]);

var minYBottomTotal = Math.min(0, d3.min(dataset, function(d) { return bottomYTotal(d); })-1);
var maxYBottomTotal = d3.max(dataset, function(d) { return bottomYTotal(d); });
var yScaleBottomTotal = d3.scale.linear()
	.domain([minYBottomTotal, maxYBottomTotal])
	.range([midPadding, halfH-paddingTop]);
var minYBottomAvg = Math.min(0, d3.min(dataset, function(d) { return bottomYAvg(d); }));
var maxYBottomAvg = d3.max(dataset, function(d) { return bottomYAvg(d); });
var yScaleBottomAvg = d3.scale.linear()
	.domain([minYBottomAvg, maxYBottomAvg])
	.range([midPadding, halfH-paddingTop]);

// Color scales
var greenScaleTotal = d3.scale.linear()
	.domain([minYTopTotal, maxYTopTotal])
	.range([white, green]);
var greenScaleAvg = d3.scale.linear()
	.domain([minYTopAvg, maxYTopAvg])
	.range([white, green]);
var redScale = d3.scale.ordinal()
	.domain([2, 3, 4, 5])
	.range(['#d4c4c5', '#d49496', '#d36468', '#d3343a']);

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
    .text(yAxisTopTotalText);
svg.append('text')
	.attr('class', 'axis-label')
	.attr('id', 'y-axis-bottom-text')
    .attr('x', 0-3*halfH/2)
    .attr('y', 10)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisBottomTotalText);


/****************************************************************************/
// RECTANGLES
/****************************************************************************/

// Augment the dataset for the stacked bar graph
dataset.forEach(function(d, i) {
	var y0Total = 0;
	var y0Avg = 0;
	d.offPositions = redScale.domain().map(function(posIndex) {
		return { 
			posIndex: posIndex, teamIndex: i, 
			y0Total: y0Total, y1Total: y0Total += d['players'][0][1][posIndex],
			y0Avg: y0Avg, y1Avg: y0Avg += d['players'][0][1][posIndex+4]
		};
	});
});

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
		return yScaleTopTotal(topYTotal(d));
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return halfH - midPadding - yScaleTopTotal(topYTotal(d));
	})
	.attr('fill', function(d) {
		return green;
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
var bottomRect = svg.selectAll('.bottom-rect-g')
	.data(dataset)
	.enter()
	.append('g')
	.attr('class', 'bottom-rect-g')
	.attr('transform', function(d, i) { return 'translate(' + xScale(i) + ',0)'; })
	.append('svg:a')
	.attr('xlink:href', function(d) { return player_url + d['players'][0][0]['id']; });
bottomRect.selectAll('.bottom-rect')
	.data(function(d) { return d.offPositions; })
	.enter()
	.append('rect')
	.attr('class', 'bottom-rect')
	.attr('id', function(d) { return 'rect-' + d.teamIndex; })
	.attr('y', function(d) {
		return halfH + yScaleBottomTotal(d.y0Total);
	})
	.attr('width', xScale.rangeBand())
	.attr('height', function(d) {
		return yScaleBottomTotal(d.y1Total) - yScaleBottomTotal(d.y0Total);
	})
	.attr('fill', function(d) {
		return redScale(d.posIndex);
	})
	.attr('opacity', opacity)
	.on('mouseover', function(d) {
		d3.selectAll('.bar-text-' + d.teamIndex).classed('hidden', false);
		d3.selectAll('#rect-' + d.teamIndex).attr('opacity', 1.0);
	})
	.on('mouseout', function(d) {
		d3.selectAll('.bar-text-' + d.teamIndex).classed('hidden', true);
		d3.selectAll('#rect-' + d.teamIndex).attr('opacity', opacity);
	});

// Create text
svg.selectAll('.top-text')
	.data(dataset)
	.enter()
	.append('text')
	.attr('class', function(d, i) { return 'hidden top-text bar-text-' + i; })
	.text(function(d) { return topYTotal(d); })
	.attr('text-anchor', 'middle')
	.attr('x', function(d, i) {
		return xScale(i) + xScale.rangeBand() / 2;
	})
	.attr('y', function(d) {
		return yScaleTopTotal(topYTotal(d)) + paddingTop + 5;
	})
	.attr('fill', darkGray)
	.attr('font-size', '12px');
bottomRect.selectAll('.bottom-text')
	.data(function(d) { return d.offPositions; })
	.enter()
	.append('text')
	.attr('class', function(d) { return 'hidden bottom-text bar-text-' + d.teamIndex; })
	.attr('transform', 'translate(' + xScale.rangeBand() / 2 + ',0)')
	.text(function(d) {  
		return d.y1Total - d.y0Total;
	})
	.attr('text-anchor', 'middle')
	.attr('y', function(d) {
		return halfH + yScaleBottomTotal(d.y1Total) - 5;
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

curY += 50;
legSvg.append('text')
	.attr('x', legW/2)
	.attr('y', curY)
	.attr('class', 'span-header')
	.attr('text-anchor', 'middle')
	.attr('fill', grayText)
	.text('Legend');
curY += 10;
var legBox1 = legSvg.append('g')
	.attr('class', 'leg-item-container')
	.attr('transform', 'translate('+curX+','+curY+')');
legBox1.append('rect')
	.attr('width', cbDim)
	.attr('height', cbDim)
	.attr('fill', redScale(2));
legBox1.append('text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Quarterbacks');
curY += 20;
var legBox2 = legSvg.append('g')
	.attr('class', 'leg-item-container')
	.attr('transform', 'translate('+curX+','+curY+')');
legBox2.append('rect')
	.attr('width', cbDim)
	.attr('height', cbDim)
	.attr('fill', redScale(3));
legBox2.append('text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Runningbacks');
curY += 20;
var legBox3 = legSvg.append('g')
	.attr('class', 'leg-item-container')
	.attr('transform', 'translate('+curX+','+curY+')');
legBox3.append('rect')
	.attr('width', cbDim)
	.attr('height', cbDim)
	.attr('fill', redScale(4));
legBox3.append('text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Wide Receivers');
curY += 20;
var legBox4 = legSvg.append('g')
	.attr('class', 'leg-item-container')
	.attr('transform', 'translate('+curX+','+curY+')');
legBox4.append('rect')
	.attr('width', cbDim)
	.attr('height', cbDim)
	.attr('fill', redScale(5));
legBox4.append('text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', grayText)
	.text('Tight Ends');

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
		d3.select('#y-axis-top-text')
			.text(total ? yAxisTopTotalText : yAxisTopAvgText);
		d3.select('#y-axis-bottom')
			.transition()
			.duration(duration)
			.call(total ? yAxisBottomTotal : yAxisBottomAvg);
		d3.select('#y-axis-bottom-text')
			.text(total ? yAxisBottomTotalText : yAxisBottomAvgText);

		// Transition the rectangles
		d3.selectAll('.top-rect')
			.transition()
			.duration(duration)
			.attr('y', function(d) {
				return total ? yScaleTopTotal(topYTotal(d)) : yScaleTopAvg(topYAverage(d));
			})
			.attr('height', function(d) {
				return total ? (halfH - midPadding - yScaleTopTotal(topYTotal(d))) :
					(halfH - midPadding - yScaleTopAvg(topYAverage(d)));
			});
		d3.selectAll('.bottom-rect')
			.transition()
			.duration(duration)
			.attr('y', function(d) {
				return total ? (halfH + yScaleBottomTotal(d.y0Total)) : 
					(halfH + yScaleBottomAvg(d.y0Avg));
			})
			.attr('height', function(d) {
				return total ? (yScaleBottomTotal(d.y1Total) - yScaleBottomTotal(d.y0Total)) :
					(yScaleBottomAvg(d.y1Avg) - yScaleBottomAvg(d.y0Avg));
			});

		// Change the hover text for the rectangles
		d3.selectAll('.top-text')
			.text(function(d) {
				return total ? topYTotal(d) : topYAverage(d);
			})
			.attr('y', function(d) {
				return total ? (yScaleTopTotal(topYTotal(d)) + paddingTop + 5) :
					(yScaleTopAvg(topYAverage(d)) + paddingTop + 5);
			});
		d3.selectAll('.bottom-text')
			.text(function(d) {
				return total ? (d.y1Total - d.y0Total) : Math.round((d.y1Avg - d.y0Avg)*100)/100;
			})
			.attr('y', function(d) {
				return total ? (halfH + yScaleBottomTotal(d.y1Total) - 5) : 
					(halfH + yScaleBottomAvg(d.y1Avg) - 5);
			});


	} 
});


