// Colors
var green = '#74AB58';
var orange = '#FF9836';
var red = '#D3343A';
var blue = '#21BDCD';
var grayBG = '#2A2A2A';
var grayText = '#828282';
var darkGray = '#232323';
var whiteText = '#D4D4D4';

// Width and height and other variables
var w = 450;
var h = 350;
var legW = 120;
var topPadding = 5;
var padding = 40;
var bottomPadding = 30;
var sidePadding = 10;
var legPadding = 17;
var cbDim = 15;
var hoverDim = 120;
var smallRadius = 3;
var bigRadius = 5;
var opacity = 0.6;

// Have to set the colspan of the nav link to 2 for this page
d3.select('#nav-container-td')
	.attr('colspan', 2);


// Funciton to move selection to front
d3.selection.prototype.moveToFront = function() {
	return this.each(function(){
		this.parentNode.appendChild(this);
	});
};


// Determine scale based on position
// TODO: figure out what we want to show for D/ST and K
var orangeMap = {'QB':'passYds', 'RB':'rushYds', 'WR':'recYds', 
'TE':'recYds'}; 
var redMap = {'QB':'rushTDs', 'RB':'rush', 'WR':'rec', 
'TE':'rec'};
var greenMap = {'QB':'passTDs', 'RB':'rushTDs', 'WR':'recTDs', 
'TE':'recTDs', 'D/ST':'miscTDs'};

var orangeTextMap = {'QB':'Passing Yards', 'RB':'Rushing Yards', 'WR':'Receiving Yards', 
'TE':'Receiving Yards', 'D/ST':'null', 'K':'null'};
var redTextMap = {'QB':'Rushing TDs', 'RB':'Rushing Attempts', 'WR':'Total Receptions', 
'TE':'Total Receptions', 'D/ST':'null', 'K':'null'};
var greenTextMap = {'QB':'Passing TDs', 'RB':'Touchdowns', 'WR':'Touchdowns', 
'TE':'Touchdowns', 'D/ST':'Touchdowns', 'K':'null'};

var yAxisLTextMap = {'QB':'Fantasy Points, Rush TDs, Pass TDs', 'RB':'Fantasy Points, Rush, TDs', 
'WR':'Fantasy Points, Rec, TDs', 'TE':'Fantasy Points, Rec, TDs', 'D/ST':'Points', 'K':'Points'};
var yAxisRTextMap = {'QB':'Passing yards', 'RB':'Rushing Yards', 'WR':'Receiving Yards', 
'TE':'Receiving Yards', 'D/ST':'null', 'K':'null'};

// Scales for axes
var xScale = d3.scale.linear()
	.domain([1, 17])
	.range([padding, w-padding]);
var minYScale = Math.min(d3.min(dataset, function(d) {return d['data'][redMap[pos]];}), 
						  d3.min(dataset, function(d) {return d['data'][orangeMap[pos]] / 10.0;}),
						  d3.min(dataset, function(d) {return d['data']['points'];}),
						  d3.min(dataset, function(d) {return d['data'][greenMap[pos]];}));
var maxYScale = Math.max(d3.max(dataset, function(d) {return d['data'][redMap[pos]];}), 
						  d3.max(dataset, function(d) {return d['data'][orangeMap[pos]] / 10.0;}),
						  d3.max(dataset, function(d) {return d['data']['points'];})) + 1;
var yScaleL = d3.scale.linear()
	.domain([minYScale, maxYScale])
	.range([h-bottomPadding, topPadding])
var yScaleR = d3.scale.linear()
	.domain([minYScale*10, maxYScale*10])
	.range([h-bottomPadding, topPadding])

// Functions for drawing connector lines
var blueLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['matchup']['week_number']);})
	.y(function(d) {return yScaleL(d['data']['points']);})
	.interpolate('linear');
var orangeLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['matchup']['week_number']);})
	.y(function(d) {return yScaleR(d['data'][orangeMap[pos]]);})
	.interpolate('linear');
var redLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['matchup']['week_number']);})
	.y(function(d) {return yScaleL(d['data'][redMap[pos]]);})
	.interpolate('linear');
var greenLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['matchup']['week_number']);})
	.y(function(d) {return yScaleL(d['data'][greenMap[pos]]);})
	.interpolate('linear');

// Create SVG element
var svg = d3.select('#player-graph-container')
	.append('svg')
	.attr('id', 'player-graph-svg')
	.attr('width', w)
	.attr('height', h);

// Define X axis
var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient('bottom')
	.tickValues(dataset.map(function(d) {return d['matchup']['week_number'];}));

// Define Y axes
var yAxisL = d3.svg.axis()
	.scale(yScaleL)
	.orient('left')
	.ticks(10);
var yAxisR = d3.svg.axis()
	.scale(yScaleR)
	.orient('right')
	.ticks(10);

// Draw axes
var xTranslate = yScaleL(0);
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(0,' + xTranslate + ')')
	.call(xAxis)
	.selectAll('text')  
	.style('text-anchor', 'end');
svg.append('g')
	.attr('class', 'axis')
	.attr('id', 'yAxisLG')
	.attr('transform', 'translate(' + padding + ',0)')
	.call(yAxisL);
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(' + (w-padding) + ',0)')
	.call(yAxisR);

// X and Y axis labels
svg.append('text')
	.attr('class', 'axis-label')
    .attr('x', w/2)
    .attr('y', h)
    .style('text-anchor', 'middle')
    .text('Week Number');
svg.append('text')
	.attr('class', 'axis-label')
    .attr('x', 0-(h/2))
    .attr('y', sidePadding)
    .attr('transform', 'rotate(-90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisLTextMap[pos]);
svg.append('text')
	.attr('class', 'axis-label')
    .attr('x', (h/2))
    .attr('y', 10-w)
    .attr('transform', 'rotate(90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisRTextMap[pos]);

// Draw circles
svg.selectAll('.blue-circle')
	.data(dataset, function(d) { return d['matchup']['week_number']; })
	.enter()
	.append('circle')
	.attr('class', 'circle blue-circle')
	.attr('id', function(d) { return 'circle'+d['matchup']['week_number']; })
	.attr('cx', function(d) {
		return xScale(d['matchup']['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data']['points']);
	})
	.attr('r', smallRadius)
	.attr('opacity', opacity);
svg.selectAll('.orange-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'circle orange-circle')
	.attr('id', function(d) { return 'circle'+d['matchup']['week_number']; })
	.attr('cx', function(d) {
		return xScale(d['matchup']['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleR(d['data'][orangeMap[pos]]);
	})
	.attr('r', smallRadius)
	.attr('opacity', opacity);
svg.selectAll('.red-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'circle red-circle')
	.attr('id', function(d) { return 'circle'+d['matchup']['week_number']; })
	.attr('cx', function(d) {
		return xScale(d['matchup']['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data'][redMap[pos]]);
	})
	.attr('r', smallRadius)
	.attr('opacity', opacity);
svg.selectAll('.green-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'circle green-circle')
	.attr('id', function(d) { return 'circle'+d['matchup']['week_number']; })
	.attr('cx', function(d) {
		return xScale(d['matchup']['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data'][greenMap[pos]]);
	})
	.attr('r', smallRadius)
	.attr('opacity', opacity);

// Draw connecting lines
svg.append('path')
	.attr('d', blueLineFunc(dataset))
	.attr('class', 'line blue-line');
svg.append('path')
	.attr('d', orangeLineFunc(dataset))
	.attr('class', 'line orange-line');
svg.append('path')
	.attr('d', redLineFunc(dataset))
	.attr('class', 'line red-line');
svg.append('path')
	.attr('d', greenLineFunc(dataset))
	.attr('class', 'line green-line');

// Create legend SVG element
var legSvg = d3.select('#player-legend-container')
	.append('svg')
	.attr('id', 'leg-svg')
	.attr('width', legW)
	.attr('height', h)
	.attr('x', w+legPadding)
	.attr('y', h-bottomPadding);

// Add 'tooltip' stuff
var curY = 30;
var numX = 90;
legSvg.append('text')
	.attr('id', 'hover-box-header')
	.attr('class', 'hover-box-content span-header graytext')
	.attr('x', legW/2)
	.attr('y', curY)
	.attr('text-anchor', 'middle');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-date')
	.attr('class', 'hover-box-content graytext')
	.attr('x', legW/2)
	.attr('y', curY)
	.attr('text-anchor', 'middle')
	.text('Hover over the graph');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-result')
	.attr('class', 'hover-box-content graytext')
	.attr('x', legW/2)
	.attr('y', curY)
	.attr('text-anchor', 'middle')
	.text('to see details.');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-bluetext-header')
	.attr('class', 'hover-box-content whitetext')
	.attr('x', 0)
	.attr('y', curY)
	.attr('text-anchor', 'left');
legSvg.append('text')
	.attr('id', 'hover-box-bluetext')
	.attr('class', 'hover-box-content bluetext')
	.attr('x', numX)
	.attr('y', curY)
	.attr('text-anchor', 'left');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-redtext-header')
	.attr('class', 'hover-box-content whitetext')
	.attr('x', 0)
	.attr('y', curY)
	.attr('text-anchor', 'left');
legSvg.append('text')
	.attr('id', 'hover-box-redtext')
	.attr('class', 'hover-box-content redtext')
	.attr('x', numX)
	.attr('y', curY)
	.attr('text-anchor', 'left');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-orangetext-header')
	.attr('class', 'hover-box-content whitetext')
	.attr('x', 0)
	.attr('y', curY)
	.attr('text-anchor', 'left');
legSvg.append('text')
	.attr('id', 'hover-box-orangetext')
	.attr('class', 'hover-box-content orangetext')
	.attr('x', numX)
	.attr('y', curY)
	.attr('text-anchor', 'left');
curY += 20;
legSvg.append('text')
	.attr('id', 'hover-box-greentext-header')
	.attr('class', 'hover-box-content whitetext')
	.attr('x', 0)
	.attr('y', curY)
	.attr('text-anchor', 'left');
legSvg.append('text')
	.attr('id', 'hover-box-greentext')
	.attr('class', 'hover-box-content greentext')
	.attr('x', numX)
	.attr('y', curY)
	.attr('text-anchor', 'left');
curY += 15;


var curX = 1;
curY += 60;
legSvg.append('text')
	.attr('class', 'legend-header')
	.attr('text-anchor', 'middle')
	.attr('x', legW/2)
	.attr('y', curY)
	.text('Legend');
curY += 10;

// Add checkboxes for legend
var blueBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'blue-box')
	.attr('transform', 'translate('+curX+','+curY+')');
blueBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
blueBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
blueBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', blue)
	.text('Fantasy Points');
curY += cbDim + 10;
var redBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'red-box')
	.attr('transform', 'translate('+curX+','+curY+')');
redBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
redBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
redBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', red)
	.text(redTextMap[pos]);
curY += cbDim + 10;
var orangeBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'orange-box')
	.attr('transform', 'translate('+curX+','+curY+')');
orangeBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
orangeBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
orangeBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', orange)
	.text(orangeTextMap[pos]);
curY += cbDim + 10;
var greenBox = legSvg.append('g')
	.attr('class', 'checkbox-container')
	.attr('id', 'green-box')
	.attr('transform', 'translate('+curX+','+curY+')');
greenBox.append('rect')
	.attr('class', 'checkbox')
	.attr('width', cbDim)
	.attr('height', cbDim);
greenBox.append('rect')
	.attr('class', 'checkbox-inner')
	.attr('width', cbDim-6)
	.attr('height', cbDim-6)
	.attr('transform', 'translate(3,3)')
	.attr('visibility', 'visible');
greenBox.append('text')
	.attr('class', 'legend-text')
	.attr('text-anchor', 'left')
	.attr('transform', 'translate('+(cbDim+5)+','+13+')')
	.attr('fill', green)
	.text(greenTextMap[pos]);


// Add functionality to checkboxes
d3.selectAll('.checkbox-container').on('click', function(d) {
	// Get corresponding circles / lines
	var className = d3.select(this).attr('id');
	var prefix = className.substring(0, className.indexOf('-'));
	var circleClass = prefix + '-circle';
	var lineClass = prefix + '-line';

	// Toggle visibility
	var inner = d3.select(this).select('.checkbox-inner');
	if (inner.attr('visibility') == 'hidden') {
		inner.attr('visibility', 'visible');
		d3.selectAll('.'+circleClass).attr('visibility', 'visible');
		d3.selectAll('.'+lineClass).attr('visibility', 'visible');
	} else {
		inner.attr('visibility', 'hidden');
		d3.selectAll('.'+circleClass).attr('visibility', 'hidden');
		d3.selectAll('.'+lineClass).attr('visibility', 'hidden');
	}
});

// Show week data when hovering over graph
var curSelection;
svg.on('mousemove', function() {
	// Find datapoint with nearest week number
	var i = Math.min(17, Math.max(1, Math.round(xScale.invert(d3.mouse(this)[0]))));
	var d;
	for (var t = 0; t < dataset.length; t++) {
		if (dataset[t]['matchup']['week_number'] == i) {
			d = dataset[t];
			break;
		}
	}
	if (d == null) return;

	// Highlight all circles with this week number
	if (curSelection != null) {
		d3.selectAll('#circle'+curSelection)
			.attr('r', smallRadius)
			.attr('opacity', opacity);
	}
	curSelection = d['matchup']['week_number'];
	d3.selectAll('#circle'+d['matchup']['week_number'])
		.attr('r', bigRadius)
		.attr('opacity', 1)
		.moveToFront();

	var home = (playerTeamAbbr == d['matchup']['home_team']['abbr']);
	var loc = home ? ' vs. ' : ' @ ';
	var win = ((home && d['matchup']['win']) || (!home && !d['matchup']['win'])) ? 'W' : 'L';
	var oppTeamAbbr = home ? d['matchup']['away_team']['abbr'] : d['matchup']['home_team']['abbr']

	legSvg.select('#hover-box-header').text(playerTeamAbbr + loc + oppTeamAbbr);
	legSvg.select('#hover-box-date').text(d['matchup']['date']);
	legSvg.select('#hover-box-result').text(win + ' ' + d['matchup']['home_team_points'] + '-' + d['matchup']['away_team_points']);
	legSvg.select('#hover-box-bluetext-header').text('Fantasy Points: ');
	legSvg.select('#hover-box-bluetext').text(d['data']['points']); 
	legSvg.select('#hover-box-orangetext-header').text(orangeTextMap[pos] + ': ');
	legSvg.select('#hover-box-orangetext').text(d['data'][orangeMap[pos]]);
	legSvg.select('#hover-box-redtext-header').text(redTextMap[pos] + ': ');
	legSvg.select('#hover-box-redtext').text(d['data'][redMap[pos]]);
	legSvg.select('#hover-box-greentext-header').text(greenTextMap[pos] + ': ');
	legSvg.select('#hover-box-greentext').text(d['data'][greenMap[pos]]);

})
.on('mouseout', function() {
	if (curSelection != null) {
		d3.selectAll('#circle'+curSelection)
			.attr('r', smallRadius)
			.attr('opacity', 0.6);
	}

	legSvg.select('#hover-box-header').text('');
	legSvg.select('#hover-box-date').text('Hover over the graph');
	legSvg.select('#hover-box-result').text('to see details.');
	legSvg.select('#hover-box-bluetext-header').text('');
	legSvg.select('#hover-box-bluetext').text(''); 
	legSvg.select('#hover-box-orangetext-header').text('');
	legSvg.select('#hover-box-orangetext').text('');
	legSvg.select('#hover-box-redtext-header').text('');
	legSvg.select('#hover-box-redtext').text('');
	legSvg.select('#hover-box-greentext-header').text('');
	legSvg.select('#hover-box-greentext').text('');
});




