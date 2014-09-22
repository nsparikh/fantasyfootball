// Data
// dataset is in alphabetical order by team name
// teams is in order by team ID

// Helper method to find a team's alphabetical index by team ID
function getAlphIndexByTeamId(teamId) {
	for (var i = 0; i < dataset.length; i++) {
		if (dataset[i]['team_id'] == teamId) return i+1;
	}
	return 0;
}

// Colors
var green = '#74AB58';
var red = '#D3343A';
var white = '#D4D4D4'
var grayText = '#828282';
var darkGray = '#232323';

// Scale for background colors of table cells
var minScore = d3.min(dataset, function(d) { 
	return d3.min(d['players'], function(d2) {
		return d2 == null ? null : parseFloat(d2[1]);
	}); 
});
var maxScore = d3.max(dataset, function(d) { 
	return d3.max(d['players'], function(d2) {
		return d2 == null ? null : parseFloat(d2[1]);
	}); 
});
var colorScale = d3.scale.linear()
	.domain([minScore, 0, maxScore])
	.range([red, white, green]);

// Add rows to table (one for each team)
var table = d3.select('#depth-table');
var tbody = table.append('tbody');
var rows = tbody.selectAll('tr')
	.data(dataset)
	.enter()
	.append('tr');

// Add cells to each row
rows.selectAll('td')
	.data(function(row) {
		return [row['team_id'], row['opponent']].concat(row['players']);
	})
	.enter()
	.append('td')
	.attr('class', 'td-wide')
	.style('background-color', function(d, i) {
		if (i < 2 || d == null || d == '') return darkGray;
		else return colorScale(d[1]);
	})
	.on('mouseover', function(d, i) {
		if (i > 1 && d != null) {
			d3.select('#detail-filler').classed('hidden', true);
			d3.select('#depth-detail').classed('hidden', false);

			d3.select('#detail-header').text(d[0]['name']);
			d3.select('#detail-subheader').text('#' + d[0]['number'] + ' ' + d[0]['position']['abbr'] + ' | ' + d[0]['team']['name']);
			d3.select('#detail-image').attr('src', image_url_prefix + d[0]['espn_id'] + '.png');
			d3.select('#detail-score').text('Performance Score: ' + d[1]);

			d3.select('#depth-detail').style('top', (Math.min(getAlphIndexByTeamId(d[0]['team']['id']),23)*23)+'px');
		}
		
	})
	.on('mouseout', function(d) {
		d3.select('#detail-filler').classed('hidden', false);
		d3.select('#depth-detail').classed('hidden', true);
	})
	.append('a')
	.attr('class', function(d, i) {
		if (i < 2 || d == null || d == '') return 'white-link';
		else return 'gray-link';
	})
	.attr('href', function(d, i) {
		if (d == null || d == '') return '#';

		if (i < 2) return team_url + d;
		else return player_url + d[0]['id'];
	})
	.text(function(d, i) { 
		if (d == null || d == '') return '';
		
		if (i < 2) return teams[d-1]['abbr'].toUpperCase(); 
		else {
			var nameArr = d[0]['name'].split(' ');
			return nameArr[0][0] + '. ' + nameArr[1];
			// TODO: What if a player has middle name?
		}
	});




