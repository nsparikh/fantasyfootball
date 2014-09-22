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
/*var colorScale = d3.scale.linear()
	.domain([d3.min(dataset, function(d) {return Math.min(dataset[d]);}),
			 0, 
			 d3.max(dataset, function(d) {return Math.max(dataset[d]);})])
	.range([red, white, green]);*/

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
	.on('mouseover', function(d, i) {
		if (i > 1 && d != null) {
			d3.select('#detail-filler').classed('hidden', true);
			d3.select('#depth-detail').classed('hidden', false);

			d3.select('#detail-header').text(d['name']);
			d3.select('#detail-subheader').text('#' + d['number'] + ' ' + d['position']['abbr'] + ' | ' + d['team']['name']);
			d3.select('#detail-image').attr('src', image_url_prefix + d['espn_id'] + '.png');
			d3.select('#detail-score').text('Performance Score: 0.00');

			d3.select('#depth-detail').style('top', (Math.min(getAlphIndexByTeamId(d['team']['id']),23)*23)+'px');
		}
		
	})
	.on('mouseout', function(d) {
		d3.select('#detail-filler').classed('hidden', false);
		d3.select('#depth-detail').classed('hidden', true);
	})
	.append('a')
	.attr('class', 'white-link')
	.attr('href', function(d, i) {
		if (d == null || d == '') return '#';

		if (i < 2) return team_url + d;
		else return player_url + d['id'];
	})
	.text(function(d, i) { 
		if (d == null || d == '') return '';
		
		if (i < 2) return teams[d-1]['abbr'].toUpperCase(); 
		else {
			var nameArr = d['name'].split(' ');
			return nameArr[0][0] + '. ' + nameArr[1];
			// TODO: What if a player has middle name?
		}
	})




