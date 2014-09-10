// Colors
var green = '#74AB58';
var orange = '#FF9836';
var red = '#D3343A';
var blue = '#21BDCD';
var grayBG = '#2A2A2A';
var grayText = '#828282';
var darkGray = '#232323';
var whiteText = '#D4D4D4';

// Width and height
var w = 400;
var h = 275;
var totalH = 350;
var legH = 100;
var topPadding = 5;
var padding = 40;
var bottomPadding = 30;
var sidePadding = 10;
var cbDim = 15;
var hoverDim = 120;


// Determine scale based on position
// TODO: figure out what we want to show for D/ST and K
var orangeMap = {'QB':'passYds', 'RB':'rushYds', 'WR':'recYds', 
'TE':'recYds', 'D/ST':'points', 'K':'points'}; 
var redMap = {'QB':'rushTDs', 'RB':'rush', 'WR':'rec', 
'TE':'rec', 'D/ST':'points', 'K':'points'};
var blueMap = {'QB':'passTDs', 'RB':'rushTDs', 'WR':'recTDs', 
'TE':'recTDs', 'D/ST':'points', 'K':'points'};

var orangeTextMap = {'QB':'Passing Yards', 'RB':'Rushing Yards', 'WR':'Receiving Yards', 
'TE':'Receiving Yards', 'D/ST':'Points', 'K':'Points'};
var redTextMap = {'QB':'Rushing TDs', 'RB':'Rushing Attempts', 'WR':'Total Receptions', 
'TE':'Total Receptions', 'D/ST':'Points', 'K':'Points'};
var blueTextMap = {'QB':'Passing TDs', 'RB':'Touchdowns', 'WR':'Touchdowns', 
'TE':'Touchdowns', 'D/ST':'Touchdowns', 'K':'Touchdowns'};

var yAxisLTextMap = {'QB':'Fantasy Points, Rush TDs, Pass TDs', 'RB':'Fantasy Points, Rush, TDs', 
'WR':'Fantasy Points, Rec, TDs', 'TE':'Fantasy Points, Rec, TDs', 'D/ST':'Points', 'K':'Points'};
var yAxisRTextMap = {'QB':'Passing yards', 'RB':'Rushing Yards', 'WR':'Receiving Yards', 
'TE':'Receiving Yards', 'D/ST':'Points', 'K':'Points'};

// Scales for axes
/*var minDate = getDate(dataset[0]),
    maxDate = getDate(dataset[dataset.length-1]);
var bisectDate = d3.bisector(function(d) { return getDate(d); }).right;
var xScale = d3.time.scale()
	.domain([minDate, maxDate])
	.range([padding, w-padding]);*/
var xScale = d3.scale.linear()
	.domain([1, 17])
	.range([padding, w-padding]);
var minYScale = Math.min(d3.min(dataset, function(d) {return d['data'][redMap[pos]];}), 
						  d3.min(dataset, function(d) {return d['data'][orangeMap[pos]] / 10.0;}),
						  d3.min(dataset, function(d) {return d['data']['points'];})) - 1;
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
var fpLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['week_number']);})
	.y(function(d) {return yScaleL(d['data']['points']);})
	.interpolate('linear');
var orangeLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['week_number']);})
	.y(function(d) {return yScaleR(d['data'][orangeMap[pos]]);})
	.interpolate('linear');
var redLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['week_number']);})
	.y(function(d) {return yScaleL(d['data'][redMap[pos]]);})
	.interpolate('linear');
var blueLineFunc = d3.svg.line()
	.x(function(d) {return xScale(d['week_number']);})
	.y(function(d) {return yScaleL(d['data'][blueMap[pos]]);})
	.interpolate('linear');

// Create SVG element
var svg = d3.select('#player-graph-container')
	.append('svg')
	.attr('width', w)
	.attr('height', totalH);

// Define X axis
var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient('bottom')
	.tickValues(dataset.map(function(d) {return d['week_number'];}))
	.tickFormat(function(d) { return 'W'+d; });

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
	.style('text-anchor', 'end')
	.attr('dx', '-.8em')
	.attr('dy', '.15em')
	.attr('transform', function(d) {
	    return 'rotate(-65)' 
	});
svg.append('g')
	.attr('class', 'axis')
	.attr('id', 'yAxisLG')
	.attr('transform', 'translate(' + padding + ',0)')
	.call(yAxisL);
svg.append('g')
	.attr('class', 'axis')
	.attr('transform', 'translate(' + (w-padding) + ',0)')
	.call(yAxisR);

// Y axis labels
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
    .attr('y', sidePadding-w)
    .attr('transform', 'rotate(90) translate(0, 0)')
    .style('text-anchor', 'middle')
    .text(yAxisRTextMap[pos]);

// Draw circles
svg.selectAll('.green-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'green-circle')
	.attr('cx', function(d) {
		return xScale(d['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data']['points']);
	})
	.attr('r', 3);
svg.selectAll('.orange-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'orange-circle')
	.attr('cx', function(d) {
		return xScale(d['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleR(d['data'][orangeMap[pos]]);
	})
	.attr('r', 3);
svg.selectAll('.red-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'red-circle')
	.attr('cx', function(d) {
		return xScale(d['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data'][redMap[pos]]);
	})
	.attr('r', 3);
svg.selectAll('.blue-circle')
	.data(dataset)
	.enter()
	.append('circle')
	.attr('class', 'blue-circle')
	.attr('cx', function(d) {
		return xScale(d['week_number']);
	})
	.attr('cy', function(d) {
		return yScaleL(d['data'][blueMap[pos]]);
	})
	.attr('r', 3);

// Draw connecting lines
svg.append('path')
	.attr('d', fpLineFunc(dataset))
	.attr('class', 'line green-line');
svg.append('path')
	.attr('d', orangeLineFunc(dataset))
	.attr('class', 'line orange-line');
svg.append('path')
	.attr('d', redLineFunc(dataset))
	.attr('class', 'line red-line');
svg.append('path')
	.attr('d', blueLineFunc(dataset))
	.attr('class', 'line blue-line');

// Create legend SVG element
var legSvg = svg.append('svg')
	.attr('class', 'leg-svg')
	.attr('w', w)
	.attr('h', legH)
	.attr('y', h+sidePadding);
legSvg.append('text')
	.attr('class', 'legend-header')
	.attr('text-anchor', 'left')
	.attr('x', sidePadding)
	.attr('y', sidePadding)
	.text('Legend')

// Add checkboxes for legend
var curX = sidePadding;
var curY = 20;
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
	.text('Fantasy Points');
curX += w/2;
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
curX -= (w/2);
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
curX += w/2;
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
	.text(blueTextMap[pos]);


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


// Add overlay for hover
var focus = svg.append('g')
	.attr('class', 'focus')
	.style('display', 'none');

focus.append('rect')
	.attr('id', 'hover-line')
	.attr('width', 2)
	.attr('height', h-bottomPadding)
	.attr('stroke-width', 0)
	.attr('fill', grayText);

focus.append('rect')
	.attr('id', 'hover-box')
	.attr('class', 'hover-box-content')
	.attr('width', hoverDim)
	.attr('height', hoverDim+10)
	.attr('fill', darkGray)
	.attr('stroke', grayText)
	.attr('stroke-width', 2);

curY = 20;
focus.append('text')
	.attr('id', 'hover-box-header')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('fill', grayText);
curY += 15;
focus.append('text')
	.attr('id', 'hover-box-date')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('fill', grayText);
curY += 15;
focus.append('text')
	.attr('id', 'hover-box-result')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('fill', grayText);
curY += 7;
focus.append('rect')
	.attr('class', 'hover-box-content')
	.attr('width', hoverDim-sidePadding)
	.attr('height', 1)
	.attr('stroke-width', 0)
	.attr('fill', grayText)
	.attr('x', sidePadding / 2)
	.attr('y', curY);
curY += 17;
focus.append('text')
	.attr('id', 'hover-box-greentext')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('text-anchor', 'left')
	.attr('fill', whiteText);
curY += 15;
focus.append('text')
	.attr('id', 'hover-box-orangetext')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('text-anchor', 'left')
	.attr('fill', whiteText);
curY += 15;
focus.append('text')
	.attr('id', 'hover-box-redtext')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('text-anchor', 'left')
	.attr('fill', whiteText);
curY += 15;
focus.append('text')
	.attr('id', 'hover-box-bluetext')
	.attr('class', 'hover-box-content')
	.attr('x', 60)
	.attr('y', curY)
	.attr('text-anchor', 'left')
	.attr('fill', whiteText);

svg.append('rect')
	.attr('class', 'overlay')
	.attr('width', w)
	.attr('height', h)
	.on('mouseover', function() { focus.style('display', null); })
  	.on('mouseout', function() { focus.style('display', 'none'); })
  	.on('mousemove', mousemove);

function mousemove() {
	var i = Math.min(17, Math.max(1, Math.round(xScale.invert(d3.mouse(this)[0]))));
	var d;
	for (var t = Math.max(0,i-2); t < dataset.length; t++) {
		if (dataset[t]['week_number'] == i) {
			d = dataset[t];
			break;
		}
	}
	if (d == null) return;
	
	var hoverTrans = -60;
	hoverTrans += (dataset.length/2 - i) * 3.5;

	focus.attr('transform', 'translate(' + xScale(d['week_number']) + ',' + padding + ')');
	focus.select('#hover-line').attr('transform', 'translate(0,' + (-1*padding) + ')');
	focus.selectAll('.hover-box-content').attr('transform', 'translate(' + hoverTrans + ',0)');

	var loc = d['home_game'] ? ' vs. ' : ' @ ';
	var win = d['win'] ? 'W' : 'L';
	focus.select('#hover-box-header').text(playerTeam + loc + d['opponent']['abbr']);
	focus.select('#hover-box-date').text(d['date']);
	focus.select('#hover-box-result').text(win + ' ' + d['pointsFor'] + '-' + d['pointsAgainst']);
	focus.select('#hover-box-greentext').text('Fantasy Points: ' + d['data']['points']); 
	focus.select('#hover-box-orangetext').text(orangeTextMap[pos] + ': ' + d['data'][orangeMap[pos]]);
	focus.select('#hover-box-redtext').text(redTextMap[pos] + ': ' + d['data'][redMap[pos]]);
	focus.select('#hover-box-bluetext').text(blueTextMap[pos] + ': ' + d['data'][blueMap[pos]]);
}

