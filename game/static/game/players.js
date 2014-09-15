var columns = [
	'name', 'team', 'position', 
	'passC/passA', 'passYds', 'passTDs', 'passInt',
	'rush', 'rushYds', 'rushTDs',
	'rec', 'recYds', 'recTDs', 'recTar',
	'misc2pc', 'miscFuml', 'miscTDs', 'points'
];

// Colors
var blue = '#21BDCD';
var white = '#D4D4D4'
var darkGray = '#232323';

var table = d3.select('#scoring-leaders-table');

// Add rows to table
var tbody = table.append('tbody');
var rows = tbody.selectAll('tr')
	.data(dataset)
	.enter()
	.append('tr')
	.attr('class', 'table-small visible');
var rowData = rows.selectAll('td')
	.data(function(row) {
		return columns.map(function(column) {
			var value;
			if (column == 'name') {
				value = row['player']['name']; 
			} else if (column == 'team' || column == 'position') {
				value = row['player'][column]['abbr'].toUpperCase();
			} else if (column == 'passC/passA') {
				if (row['data']['passC'] == null) value = '-- / --';
				else value = row['data']['passC']+' / '+row['data']['passA'];
			} else value = row['data'][column]
			return {column: column, value: value, player: row['player']};
		});
	}).enter();

// Filter data to add links to the player names / teams / positions
rowData.append('td')
	.text(function(d) {
		if (d.column != 'name' && d.column != 'team' && d.column != 'position') {
			if (d.value == null) return '--';
			else return d.value;
		}
		return null;
	})
	.attr('class', 'td-wide')
	.filter(function(d) {
		return d.column == 'name' || d.column == 'team' || d.column == 'position';
	})
	.append('a')
	.attr('href', function(d) {
		if (d.column == 'name') return ''+d['player']['id'];
		else if (d.column == 'team') return team_url+d['player']['team']['id'];
		else if (d.column == 'position') return position_url+d['player']['position']['id'];
		return null;
	})
	.attr('class', 'white-link')
	.text(function(d) { return d.value; });
