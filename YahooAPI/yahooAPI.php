<?php
date_default_timezone_set('America/New_York');

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// GLOBAL VARIABLES
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Array mapping Yahoo our stat names to yahoo stat_categories IDs
$stat_categories = [
    'passC' => 2,
    'passA' => 1,
    'passYds' => 4,
    'passTDs' => 5,
    'passInt' => 6,
    'rush' => 8,
    'rushYds' => 9,
    'rushTDs' => 10,
    'rec' => 11,
    'recYds' => 12,
    'recTDs' => 13,
    'recTar' => 78,
    'misc2pc' => 16,
    'miscFuml' => 18,
    'miscTDs' => 15,
    'bonus40YdPassTDs' => 60,
    'bonus40YdRushTDs' => 62,
    'bonus40YdRecTDs' => 64
];

$yahoo_year_codes = [
    2014 => 331,
    2013 => 314,
    2012 => 273,
    2011 => 257,
    2010 => 242,
    2009 => 222,
    2008 => 199,
    2007 => 175,
    2006 => 153,
    2005 => 124,
    2004 => 101,
    2003 => 79,
    2002 => 49,
    2001 => 57
];

// Initialize OAuth for Yahoo API
$consumer_key = 'dj0yJmk9M1dNVnJvODNJYzhRJmQ9WVdrOWMyWnhkbVV3Tm0wbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD0wMg--';
$consumer_secret = '5f20e6490769986958f3d7ad64656982fd86a822';
$oauth = new OAuth($consumer_key, $consumer_secret, 
                OAUTH_SIG_METHOD_HMACSHA1,
                OAUTH_AUTH_TYPE_URI);

// API URL
$yahoo_url = 'http://fantasysports.yahooapis.com/fantasy/v2/players;player_keys=year_code.p.player_code/stats;type=week;week=';

// Load Player and GameDataPoints from JSON fixture files
$players_json = json_decode(file_get_contents('../game/fixtures/Player2014.json'), true);
$gd_2014 = json_decode(file_get_contents('../data/fixtures/GameData2014.json'), true);

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// EXECUTION
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

writeGameData(2014);

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DEFINED METHODS FOR GETTING DATA
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

function writeGameData($year) {
    // Open output files
    $outfile_gd2014 = fopen('GameData2014_Yahoo.json', 'a');
    $outfile_gdpoints2014 = fopen('GameDataPoints2014_Yahoo.json', 'a');

    // Go through each player
    foreach ($GLOBALS['players_json'] as $player_index=>$player) {
        if ($player_index < 314) continue;

        // Loop through each week in the season
        foreach (range(1, 8) as $week_num) {
            print $player_index.'/1486 '.$player['pk'].' '.$player['fields']['name'] . ' W' . $week_num . ' ';

            // Get the corresponding GameData point 
            $gd = getPointById(getDataPk($player, $year, $week_num), $GLOBALS['gd_2014']);
            if (is_null($gd)) $gd = blankGameData($player, $year, $week_num);

            // Get the Yahoo game data for this player and week
            $result = getYahooPlayerGameData($player, $year, $week_num);
            if ($result == -1) { // We've hit the API limit
                print 'CURRENT TIME: ' . date('m/d/Y h:i:s a', time()) . "\n";
                return;
            } else if ($result == 100 or $result == 1) { // We got an all 0 or null data point
                $gd['fields']['data'] = $result;
                fwrite($outfile_gd2014, gdFixtureString($gd));
            } else { // Write both points to file
                $gd['fields']['data'] = $result['pk'];
                fwrite($outfile_gd2014, gdFixtureString($gd));
                fwrite($outfile_gdpoints2014, dpFixtureString($result));
            }
        }
    }
}

// Gets the given player's game data for the given week and year 
// Returns -1 if we hit the API limit
function getYahooPlayerGameData($player, $year, $week_num) {
    // Get player's Yahoo ID and corresponding GameData point
    $yahoo_id = $player['fields']['yahoo_id'];

    // Get the URL for this player, year, and week
    $year_code = $GLOBALS['yahoo_year_codes'][$year];
    $player_url = str_replace('player_code', $player['fields']['yahoo_id'], 
        str_replace('year_code', $year_code, $GLOBALS['yahoo_url'])) . $week_num;

    // Try to fetch the API response
    try {
        if ($GLOBALS['oauth'] -> fetch($player_url)) {
            $xmlResponse = simplexml_load_string($GLOBALS['oauth'] -> getLastResponse());
            $statArray = $xmlResponse->players->player->player_stats->stats;
            $new_dp = getStats($statArray, $player, $year, $week_num);

            // Check if the resulting data point has all 0's
            if (isAllZeroDataPoint($new_dp)) {
                print "ALL 0\n";
                return 100; // This is the PK for the all 0 DataPoint
            } else {
                print "SUCCESS\n";
                return $new_dp;
            }
        } else { 
            print "Couldn't fetch\n";
            return -1;
        }
    } catch (OAuthException $e) {
        print 'Error: ' . $e->getMessage() . "\n";
        if (strpos($e->getMessage(), '999') === false) { // Record as null DataPoint
            return 1;
        } else { // We've hit the API limit
            return -1;
        }
    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// HELPER METHODS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Gets the relevant stats from the stat array and returns a DataPoint array
function getStats($statArray, $player, $year, $week_num) {
    $new_dp = [];
    $new_dp['pk'] = getDataPk($player, $year, $week_num);

    // Get stats for each of the categories
    foreach ($GLOBALS['stat_categories'] as $stat_name=>$stat_cat_num) {
        foreach ($statArray->children() as $s) {
            $cur_stat_cat_num = (int) $s->stat_id;
            if ($cur_stat_cat_num == $stat_cat_num) {
                $stat_val = (int) $s->value;
                $new_dp['fields'][$stat_name] = $stat_val;
            }
        }
    }

    $new_dp['fields']['points'] = computeFantasyPoints($new_dp);
    return $new_dp;
}

// Returns the fixture string for the given data point
function dpFixtureString($dp) {
    return ('{ "model":"data.DataPoint", "pk":' . $dp['pk'] .
        ', "fields":{"passC":' . $dp['fields']['passC'] .
        ', "passA":' . $dp['fields']['passA'] .
        ', "passYds":' . $dp['fields']['passYds'] .
        ', "passTDs":' . $dp['fields']['passTDs'] .
        ', "passInt":' . $dp['fields']['passInt'] .
        ', "rush":' . $dp['fields']['rush'] .
        ', "rushYds":' . $dp['fields']['rushYds'] .
        ', "rushTDs":' . $dp['fields']['rushTDs'] .
        ', "rec":' . $dp['fields']['rec'] .
        ', "recYds":' . $dp['fields']['recYds'] .
        ', "recTDs":' . $dp['fields']['recTDs'] .
        ', "recTar":' . $dp['fields']['recTar'] .
        ', "misc2pc":' . $dp['fields']['misc2pc'] .
        ', "miscFuml":' . $dp['fields']['miscFuml'] .
        ', "miscTDs":' . $dp['fields']['miscTDs'] .
        ', "bonus40YdPassTDs":' . $dp['fields']['bonus40YdPassTDs'] .
        ', "bonus40YdRushTDs":' . $dp['fields']['bonus40YdRushTDs'] .
        ', "bonus40YdRecTDs":' . $dp['fields']['bonus40YdRecTDs'] .
        ', "points":' . $dp['fields']['points'] . '} },' . "\n");
}

// Returns the fixture string for the given GameData point
function gdFixtureString($gd) {
    return ('{ ' . '"model":"data.GameData", "pk":' . $gd['pk'] . 
        ', "fields":{"player":' . $gd['fields']['player'] .
        ', "matchup":' . (is_null($gd['fields']['matchup']) ? 'null' : $gd['fields']['matchup']) .
        ', "projection":' . (is_null($gd['fields']['projection']) ? 'null' : $gd['fields']['projection']) .  
        ', "espn_projection":' . (is_null($gd['fields']['espn_projection']) ? 'null' : $gd['fields']['espn_projection']) . 
        ', "yahoo_projection":' . (is_null($gd['fields']['yahoo_projection']) ? 'null' : $gd['fields']['yahoo_projection']) .
        ', "cbs_projection":' . (is_null($gd['fields']['cbs_projection']) ? 'null' : $gd['fields']['cbs_projection']) . 
        ', "performance_score":' . (is_null($gd['fields']['performance_score']) ? 'null' : $gd['fields']['performance_score']) . 
        ', "data":' . $gd['fields']['data'] . '} },' . "\n");
}

// Returns a "blank" GameData point for the given player, year, and week
function blankGameData($player, $year, $week_num) {
    $blank_gd = [];
    $blank_gd['pk'] = getDataPk($player, $year, $week_num);
    $blank_gd['fields']['player'] = $player['pk'];
    $blank_gd['fields']['matchup'] = 'null';
    $blank_gd['fields']['projection'] = 'null';
    $blank_gd['fields']['espn_projection'] = 'null';
    $blank_gd['fields']['yahoo_projection'] = 'null';
    $blank_gd['fields']['cbs_projection'] = 'null';
    $blank_gd['fields']['performance_score'] = 'null';
    $blank_gd['fields']['data'] = 1;
    return $blank_gd;
}

// Checks whether the given data point has all 0 fields
function isAllZeroDataPoint($dp) {
    foreach ($GLOBALS['stat_categories'] as $stat_name=>$stat_cat_num) {
        if ($dp['fields'][$stat_name] != 0) return false;
    }
    if ($dp['fields']['points'] != 0) return false;

    return true;
}

// Computes the number of (offensive) fantasy points from the given data point
function computeFantasyPoints($dp) {
    $passYdPts = ($dp['fields']['passYds']>=0 ? 
        floor($dp['fields']['passYds']/25) : ceil($dp['fields']['passYds']/25));
    $rushYdPts = ($dp['fields']['rushYds']>=0 ? 
        floor($dp['fields']['rushYds']/10) : ceil($dp['fields']['rushYds']/10));
    $recYdPts = ($dp['fields']['recYds']>=0 ? 
        floor($dp['fields']['recYds']/10) : ceil($dp['fields']['recYds']/10));

    $pts = ( ($dp['fields']['rushTDs']*6) + ($dp['fields']['recTDs']*6) + 
        ($dp['fields']['miscTDs']*6) + ($dp['fields']['passTDs']*4) + 
        ($dp['fields']['misc2pc']*2) + $rushYdPts + $recYdPts + $passYdPts );
    $pts = $pts - ($dp['fields']['passInt']*2) - ($dp['fields']['miscFuml']*2);
    $pts = $pts + (($dp['fields']['bonus40YdPassTDs']*2) + 
        ($dp['fields']['bonus40YdRushTDs']*2) + ($dp['fields']['bonus40YdRecTDs']*2));
    return $pts;
}

// Retrieves the point from the GameDataPoint dataset with the given ID (PK)
function getPointById($id, $dataset) {
    foreach ($dataset as $dp) {
        if ($dp['pk'] == $id) {
            return $dp;
        }
    }
    return NULL;
}

// Returns the GameData / DataPoint pk that matches the given player, year, and week
function getDataPk($player, $year, $week_num) {
    return $player['pk'] . substr($year, 2) . sprintf('%02s', $week_num);
}

?>
        