// Data
/*var dataset = [
	{'off':'ARI', 'def':'STL', 'WR1':57.89, 'WR2':-23.06, 'WR3':-29.08, 'TE':-66.58},
	{'off':'ATL', 'def':'GNB', 'WR1':78.69, 'WR2':-26.86, 'WR3':-19.78, 'TE':17.03},
	{'off':'BAL', 'def':'MIN', 'WR1':23.79, 'WR2':-7.46, 'WR3':10.83, 'TE':8.42},
	{'off':'BUF', 'def':'TAM', 'WR1':-45.21, 'WR2':-18.56, 'WR3':37.43, 'TE':-24.18},
	{'off':'CAR', 'def':'NOR', 'WR1':-75.21, 'WR2':1.54, 'WR3':-15.18, 'TE':-36.18},
	{'off':'CHI', 'def':'DAL', 'WR1':73.19, 'WR2':60.84, 'WR3':-46.68, 'TE':11.73},
	{'off':'CIN', 'def':'IND', 'WR1':78.79, 'WR2':21.74, 'WR3':-1.28, 'TE':-3.48},
	{'off':'CLE', 'def':'NWE', 'WR1':-31.81, 'WR2':-23.96, 'WR3':12.93, 'TE':20.13},
	{'off':'DAL', 'def':'CHI', 'WR1':58.39, 'WR2':-48.56, 'WR3':14.53, 'TE':31.93},
	{'off':'DEN', 'def':'TEN', 'WR1':-10.41, 'WR2':26.24, 'WR3':30.73, 'TE':69.13},
	{'off':'DET', 'def':'PHI', 'WR1':110.89, 'WR2':39.54, 'WR3':25.13, 'TE':-14.78},
	{'off':'GNB', 'def':'ATL', 'WR1':78.79, 'WR2':44.54, 'WR3':41.23, 'TE':-23.28},
	{'off':'HOU', 'def':'JAC', 'WR1':-5.51, 'WR2':25.24, 'WR3':-25.88, 'TE':64.13},
	{'off':'IND', 'def':'CIN', 'WR1':31.99, 'WR2':-34.86, 'WR3':-22.98, 'TE':-20.38},
	{'off':'JAC', 'def':'HOU', 'WR1':-42.51, 'WR2':-22.66, 'WR3':-37.08, 'TE':-37.78},
	{'off':'KAN', 'def':'WAS', 'WR1':-51.41, 'WR2':23.74, 'WR3':-11.08, 'TE':-23.48},
	{'off':'MIA', 'def':'PIT', 'WR1':-39.61, 'WR2':-20.26, 'WR3':34.63, 'TE':-7.18},
	{'off':'MIN', 'def':'BAL', 'WR1':-50.31, 'WR2':-6.16, 'WR3':4.92, 'TE':-2.38},
	{'off':'NWE', 'def':'CLE', 'WR1':-85.91, 'WR2':11.24, 'WR3':51.53, 'TE':-12.08},
	{'off':'NOR', 'def':'CAR', 'WR1':-81.31, 'WR2':-23.06, 'WR3':-28.38, 'TE':98.83},
	{'off':'NYG', 'def':'SDG', 'WR1':82.99, 'WR2':12.44, 'WR3':4.23, 'TE':-45.48},
	{'off':'NYJ', 'def':'OAK', 'WR1':-51.61, 'WR2':3.54, 'WR3':24.03, 'TE':-1.28},
	{'off':'OAK', 'def':'NYJ', 'WR1':-44.61, 'WR2':45.24, 'WR3':-31.38, 'TE':-21.38},
	{'off':'PHI', 'def':'DET', 'WR1':98.99, 'WR2':93.04, 'WR3':-25.78, 'TE':-23.48},
	{'off':'PIT', 'def':'MIA', 'WR1':0.49, 'WR2':-32.56, 'WR3':34.63, 'TE':-5.68},
	{'off':'SDG', 'def':'NYG', 'WR1':-63.31, 'WR2':11.04, 'WR3':14.83, 'TE':32.73},
	{'off':'SFO', 'def':'SEA', 'WR1':-77.61, 'WR2':-62.36, 'WR3':-56.18, 'TE':24.03},
	{'off':'SEA', 'def':'SFO', 'WR1':-31.61, 'WR2':6.04, 'WR3':-1.38, 'TE':-41.68},
	{'off':'STL', 'def':'ARI', 'WR1':-74.51, 'WR2':-49.76, 'WR3':31.53, 'TE':103.13},
	{'off':'TAM', 'def':'BUF', 'WR1':64.39, 'WR2':29.34, 'WR3':-21.68, 'TE':-48.38},
	{'off':'TEN', 'def':'DEN', 'WR1':-13.71, 'WR2':-17.76, 'WR3':4.02, 'TE':11.73},
	{'off':'WAS', 'def':'KAN', 'WR1':36.79, 'WR2':-37.36, 'WR3':-3.38, 'TE':-33.88}
];*/
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
var table = d3.select('#wr-depth-table');
var tbody = table.append('tbody');
var rows = tbody.selectAll('tr')
	.data(dataset)
	.enter()
	.append('tr');

// Add cells to each row
rows.selectAll('td')
	.data(function(row) {
		return [row['team_id'], row['team_id']].concat(row['wide_receivers']);
	})
	.enter()
	.append('td')
	.attr('class', 'td-wide')
	.on('mouseover', function(d, i) {
		if (i > 1 && d != null) {
			d3.select('#wr-detail-filler').classed('hidden', true);
			d3.select('#wr-depth-detail').classed('hidden', false);

			d3.select('#wr-detail-header').text(d['name']);
			d3.select('#wr-detail-subheader').text('#' + d['number'] + ' ' + d['position']['abbr'] + ' | ' + d['team']['name']);
			d3.select('#wr-detail-image').attr('src', image_url_prefix + d['espn_id'] + '.png');
			d3.select('#wr-detail-score').text('Performance Score: 0.00');


			d3.select('#wr-depth-detail').style('top', (Math.min(getAlphIndexByTeamId(d['team']['id']),23)*23)+'px');
		}
		
	})
	.on('mouseout', function(d) {
		d3.select('#wr-detail-filler').classed('hidden', false);
		d3.select('#wr-depth-detail').classed('hidden', true);
	})
	.append('a')
	.attr('class', 'white-link')
	.attr('href', function(d, i) {
		if (i < 2) return team_url + d;
		else if (d == null || d == '') return '#';
		else return player_url + d['id'];
	})
	.text(function(d, i) { 
		if (i < 2) return teams[d-1]['abbr'].toUpperCase(); 
		else if (d == null || d == '') return '';
		else {
			var nameArr = d['name'].split(' ');
			return nameArr[0][0] + '. ' + nameArr[1];
			// TODO: What if a player has middle name?
		}
	})




