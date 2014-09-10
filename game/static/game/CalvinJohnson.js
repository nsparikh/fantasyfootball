// Load data
var dataset = [
	{"date":"9/8/13", "opp":"MIN", "res":"W 34-24", "rec":4, "yds":37, "td":0, "fp":3.7},
	{"date":"9/15/13", "opp":"ARI", "res":"L 21-25", "rec":6, "yds":116, "td":12, "fp":23.6},
	{"date":"9/22/13", "opp":"WSH", "res":"W 27-20", "rec":7, "yds":115, "td":6, "fp":17.5},
	{"date":"9/29/13", "opp":"CHI", "res":"W 40-32", "rec":4, "yds":44, "td":6, "fp":12.4},
	{"date":"10/13/13", "opp":"CLE", "res":"W 31-17", "rec":3, "yds":25, "td":0, "fp":2.5},
	{"date":"10/20/13", "opp":"CIN", "res":"L 24-27", "rec":9, "yds":155, "td":12, "fp":27.5},
	{"date":"10/27/13", "opp":"DAL", "res":"W 31-30", "rec":14, "yds":329, "td":6, "fp":36.9},
	{"date":"11/10/13", "opp":"CHI", "res":"W 21-19", "rec":6, "yds":83, "td":12, "fp":20.3},
	{"date":"11/17/13", "opp":"PIT", "res":"L 27-37", "rec":6, "yds":179, "td":12, "fp":29.9},
	{"date":"11/24/13", "opp":"TB", "res":"L 21-24", "rec":7, "yds":115, "td":0, "fp":11.5},
	{"date":"11/28/13", "opp":"GB", "res":"W 40-10", "rec":6, "yds":101, "td":6, "fp":16.1},
	{"date":"12/8/13", "opp":"PHI", "res":"L 20-34", "rec":3, "yds":52, "td":0, "fp":5.2},
	{"date":"12/16/13", "opp":"BAL", "res":"L 16-18", "rec":6, "yds":98, "td":0, "fp":10.8},
	{"date":"12/22/13", "opp":"NYG", "res":"L 20-23 (OT)", "rec":3, "yds":43, "td":0, "fp":4.3}
];

// Colors
var green = "#74AB58";
var orange = "#FF9836";
var red = "#D3343A";
var blue = "#21BDCD";
var grayBG = "#2A2A2A";
var grayText = "#828282";
var darkGray = "#232323";
var whiteText = "#D4D4D4";

// Width and height
var w = 400;
var h = 275;
var totalH = 350;
var legH = 100;
var padding = 40;
var bottomPadding = 30;
var sidePadding = 10;
var cbDim = 15;
var hoverDim = 120;

// Helper method
function getDate(d) {
	return new Date(d.date);
}

// Scales for axes
var minDate = getDate(dataset[0]),
    maxDate = getDate(dataset[dataset.length-1]);
var bisectDate = d3.bisector(function(d) { return getDate(d); }).left;
var xScale = d3.time.scale()
	.domain([minDate, maxDate])
	.range([padding, w-padding]);
var maxYScaleL = Math.max(d3.max(dataset, function(d) {return d.fp;}), 
						  d3.max(dataset, function(d) {return d.yds / 10.0;})) + 1;
var yScaleL = d3.scale.linear()
	.domain([0, maxYScaleL])
	.range([h-bottomPadding, 0])
var yScaleR = d3.scale.linear()
	.domain([0, maxYScaleL*10])
	.range([h-bottomPadding, 0])

// Functions for drawing connector lines
var fpLineFunc = d3.svg.line()
	.x(function(d) {return xScale(getDate(d));})
	.y(function(d) {return yScaleL(d.fp);})
	.interpolate("linear");
var ydsLineFunc = d3.svg.line()
	.x(function(d) {return xScale(getDate(d));})
	.y(function(d) {return yScaleR(d.yds);})
	.interpolate("linear");
var recLineFunc = d3.svg.line()
	.x(function(d) {return xScale(getDate(d));})
	.y(function(d) {return yScaleL(d.rec);})
	.interpolate("linear");
var tdLineFunc = d3.svg.line()
	.x(function(d) {return xScale(getDate(d));})
	.y(function(d) {return yScaleL(d.td);})
	.interpolate("linear");

// Create SVG element
var svg = d3.select("#CalvinJohnson-graph-container")
	.append("svg")
	.attr("width", w)
	.attr("height", totalH);

// Define X axis
var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient("bottom")
	.tickValues(dataset.map(function(d) {return getDate(d);}))
	.tickFormat(d3.time.format("%m/%d"));

// Define Y axes
var yAxisL = d3.svg.axis()
	.scale(yScaleL)
	.orient("left")
	.ticks(10);
var yAxisR = d3.svg.axis()
	.scale(yScaleR)
	.orient("right")
	.ticks(10);

// Draw axes
svg.append("g")
	.attr("class", "axis")
	.attr("transform", "translate(0," + (h - bottomPadding) + ")")
	.call(xAxis)
	.selectAll("text")  
	.style("text-anchor", "end")
	.attr("dx", "-.8em")
	.attr("dy", ".15em")
	.attr("transform", function(d) {
	    return "rotate(-65)" 
	});

svg.append("g")
	.attr("class", "axis")
	.attr("transform", "translate(" + padding + ",0)")
	.call(yAxisL);

svg.append("g")
	.attr("class", "axis")
	.attr("transform", "translate(" + (w-padding) + ",0)")
	.call(yAxisR);

// Y axis labels
svg.append("text")
	.attr("class", "axis-label")
    .attr("x", 0-(h/2))
    .attr("y", sidePadding)
    .attr("transform", "rotate(-90) translate(0, 0)")
    .style("text-anchor", "middle")
    .text("Receptions, Fantasy Points, TDs");

svg.append("text")
	.attr("class", "axis-label")
    .attr("x", (h/2))
    .attr("y", sidePadding-w)
    .attr("transform", "rotate(90) translate(0, 0)")
    .style("text-anchor", "middle")
    .text("Receiving Yards");

// Draw circles
svg.selectAll(".fp-circle")
	.data(dataset)
	.enter()
	.append("circle")
	.attr("class", "fp-circle")
	.attr("cx", function(d) {
		return xScale(getDate(d));
	})
	.attr("cy", function(d) {
		return yScaleL(d.fp);
	})
	.attr("r", 3);
svg.selectAll(".yds-circle")
	.data(dataset)
	.enter()
	.append("circle")
	.attr("class", "yds-circle")
	.attr("cx", function(d) {
		return xScale(getDate(d));
	})
	.attr("cy", function(d) {
		return yScaleR(d.yds);
	})
	.attr("r", 3);
svg.selectAll(".rec-circle")
	.data(dataset)
	.enter()
	.append("circle")
	.attr("class", "rec-circle")
	.attr("cx", function(d) {
		return xScale(getDate(d));
	})
	.attr("cy", function(d) {
		return yScaleL(d.rec);
	})
	.attr("r", 3);
svg.selectAll(".td-circle")
	.data(dataset)
	.enter()
	.append("circle")
	.attr("class", "td-circle")
	.attr("cx", function(d) {
		return xScale(getDate(d));
	})
	.attr("cy", function(d) {
		return yScaleL(d.td);
	})
	.attr("r", 3);

// Draw connecting lines
svg.append("path")
	.attr("d", fpLineFunc(dataset))
	.attr("class", "line fp-line");
svg.append("path")
	.attr("d", ydsLineFunc(dataset))
	.attr("class", "line yds-line");
svg.append("path")
	.attr("d", recLineFunc(dataset))
	.attr("class", "line rec-line");
svg.append("path")
	.attr("d", tdLineFunc(dataset))
	.attr("class", "line td-line");

// Create legend SVG element
var legSvg = svg.append("svg")
	.attr("class", "leg-svg")
	.attr("w", w)
	.attr("h", legH)
	.attr("y", h+sidePadding);
legSvg.append("text")
	.attr("class", "legend-header")
	.attr("text-anchor", "left")
	.attr("x", sidePadding)
	.attr("y", sidePadding)
	.text("Legend")

// Add checkboxes for legend
var curX = sidePadding;
var curY = 20;
var fpBox = legSvg.append("g")
	.attr("class", "checkbox-container")
	.attr("id", "fp-box")
	.attr("transform", "translate("+curX+","+curY+")");
fpBox.append("rect")
	.attr("class", "checkbox")
	.attr("width", cbDim)
	.attr("height", cbDim);
fpBox.append("rect")
	.attr("class", "checkbox-inner")
	.attr("width", cbDim-6)
	.attr("height", cbDim-6)
	.attr("transform", "translate(3,3)")
	.attr("visibility", "visible");
fpBox.append("text")
	.attr("class", "legend-text")
	.attr("text-anchor", "left")
	.attr("transform", "translate("+(cbDim+5)+","+13+")")
	.attr("fill", green)
	.text("Fantasy Points");
curX += w/2;
var recBox = legSvg.append("g")
	.attr("class", "checkbox-container")
	.attr("id", "rec-box")
	.attr("transform", "translate("+curX+","+curY+")");
recBox.append("rect")
	.attr("class", "checkbox")
	.attr("width", cbDim)
	.attr("height", cbDim);
recBox.append("rect")
	.attr("class", "checkbox-inner")
	.attr("width", cbDim-6)
	.attr("height", cbDim-6)
	.attr("transform", "translate(3,3)")
	.attr("visibility", "visible");
recBox.append("text")
	.attr("class", "legend-text")
	.attr("text-anchor", "left")
	.attr("transform", "translate("+(cbDim+5)+","+13+")")
	.attr("fill", red)
	.text("Total Receptions");
curX -= (w/2);
curY += cbDim + 10;
var ydsBox = legSvg.append("g")
	.attr("class", "checkbox-container")
	.attr("id", "yds-box")
	.attr("transform", "translate("+curX+","+curY+")");
ydsBox.append("rect")
	.attr("class", "checkbox")
	.attr("width", cbDim)
	.attr("height", cbDim);
ydsBox.append("rect")
	.attr("class", "checkbox-inner")
	.attr("width", cbDim-6)
	.attr("height", cbDim-6)
	.attr("transform", "translate(3,3)")
	.attr("visibility", "visible");
ydsBox.append("text")
	.attr("class", "legend-text")
	.attr("text-anchor", "left")
	.attr("transform", "translate("+(cbDim+5)+","+13+")")
	.attr("fill", orange)
	.text("Receiving Yards");
curX += w/2;
var tdBox = legSvg.append("g")
	.attr("class", "checkbox-container")
	.attr("id", "td-box")
	.attr("transform", "translate("+curX+","+curY+")");
tdBox.append("rect")
	.attr("class", "checkbox")
	.attr("width", cbDim)
	.attr("height", cbDim);
tdBox.append("rect")
	.attr("class", "checkbox-inner")
	.attr("width", cbDim-6)
	.attr("height", cbDim-6)
	.attr("transform", "translate(3,3)")
	.attr("visibility", "visible");
tdBox.append("text")
	.attr("class", "legend-text")
	.attr("text-anchor", "left")
	.attr("transform", "translate("+(cbDim+5)+","+13+")")
	.attr("fill", blue)
	.text("Touchdown Points");


// Add functionality to checkboxes
d3.selectAll(".checkbox-container").on("click", function(d) {
	// Get corresponding circles / lines
	var className = d3.select(this).attr("id");
	var prefix = className.substring(0, className.indexOf("-"));
	var circleClass = prefix + "-circle";
	var lineClass = prefix + "-line";

	// Toggle visibility
	var inner = d3.select(this).select(".checkbox-inner");
	if (inner.attr("visibility") == "hidden") {
		inner.attr("visibility", "visible");
		d3.selectAll("."+circleClass).attr("visibility", "visible");
		d3.selectAll("."+lineClass).attr("visibility", "visible");
	} else {
		inner.attr("visibility", "hidden");
		d3.selectAll("."+circleClass).attr("visibility", "hidden");
		d3.selectAll("."+lineClass).attr("visibility", "hidden");
	}
});


// Add overlay for hover
var focus = svg.append("g")
	.attr("class", "focus")
	.style("display", "none");

focus.append("rect")
	.attr("id", "hover-line")
	.attr("width", 1)
	.attr("height", h-bottomPadding)
	.attr("stroke-width", 0)
	.attr("fill", grayText);

focus.append("rect")
	.attr("id", "hover-box")
	.attr("class", "hover-box-content")
	.attr("width", hoverDim)
	.attr("height", hoverDim+10)
	.attr("fill", darkGray)
	.attr("stroke", grayText)
	.attr("stroke-width", 2);

curY = 20;
focus.append("text")
	.attr("id", "hover-box-header")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("fill", grayText);
curY += 15;
focus.append("text")
	.attr("id", "hover-box-date")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("fill", grayText);
curY += 15;
focus.append("text")
	.attr("id", "hover-box-result")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("fill", grayText);
curY += 7;
focus.append("rect")
	.attr("class", "hover-box-content")
	.attr("width", hoverDim-sidePadding)
	.attr("height", 1)
	.attr("stroke-width", 0)
	.attr("fill", grayText)
	.attr("x", sidePadding / 2)
	.attr("y", curY);
curY += 17;
focus.append("text")
	.attr("id", "hover-box-fp")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("text-anchor", "left")
	.attr("fill", whiteText);
curY += 15;
focus.append("text")
	.attr("id", "hover-box-yds")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("text-anchor", "left")
	.attr("fill", whiteText);
curY += 15;
focus.append("text")
	.attr("id", "hover-box-rec")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("text-anchor", "left")
	.attr("fill", whiteText);
curY += 15;
focus.append("text")
	.attr("id", "hover-box-td")
	.attr("class", "hover-box-content")
	.attr("x", 60)
	.attr("y", curY)
	.attr("text-anchor", "left")
	.attr("fill", whiteText);

svg.append("rect")
	.attr("class", "overlay")
	.attr("width", w)
	.attr("height", h)
	.on("mouseover", function() { focus.style("display", null); })
  	.on("mouseout", function() { focus.style("display", "none"); })
  	.on("mousemove", mousemove);

function mousemove() {
	var x0 = xScale.invert(d3.mouse(this)[0]);
	var i = bisectDate(dataset, x0, 1, dataset.length);
	var d;
	if (i == dataset.length) {
		d = dataset[dataset.length-1]; 
	} else {
		var d0 = dataset[i - 1];
		var d1 = dataset[i];
		d = x0 - d0.date > d1.date - x0 ? d1 : d0;
	}
	
	var hoverTrans = -60;
	hoverTrans += (dataset.length/2 - i) * 3.5;

	focus.attr("transform", "translate(" + xScale(getDate(d)) + "," + padding + ")");
	focus.select("#hover-line").attr("transform", "translate(0," + (-1*padding) + ")");
	focus.selectAll(".hover-box-content").attr("transform", "translate(" + hoverTrans + ",0)");

	focus.select("#hover-box-header").text("DET vs. " + d.opp)
	focus.select("#hover-box-date").text(d.date);
	focus.select("#hover-box-result").text(d.res);
	focus.select("#hover-box-fp").text("Fantasy Points: " + d.fp);
	focus.select("#hover-box-yds").text("Receiving Yards: " + d.yds);
	focus.select("#hover-box-rec").text("Total Receptions: " + d.rec);
	focus.select("#hover-box-td").text("TD Points: " + d.td);
}

