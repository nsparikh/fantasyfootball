<?php

// Open file to save results
$outfile = fopen('GameDataPoints2013_Yahoo.json', 'w');
fwrite($outfile, "[\n");

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
    'misc2pc' => 16,
    'miscFuml' => 18,
    'miscTDs' => 15
];

$bonus_stat_categories = [
    '40YdPassTDs' => 60,
    '40YdRushTDs' => 62,
    '40YdRecTDs' => 64
];

// Initialize OAuth for Yahoo API
$consumer_key = 'dj0yJmk9M1dNVnJvODNJYzhRJmQ9WVdrOWMyWnhkbVV3Tm0wbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD0wMg--';
$consumer_secret = '5f20e6490769986958f3d7ad64656982fd86a822';
$o = new OAuth($consumer_key, $consumer_secret, 
                OAUTH_SIG_METHOD_HMACSHA1,
                OAUTH_AUTH_TYPE_URI);

$yahoo_url_prefix = 'http://fantasysports.yahooapis.com/fantasy/v2/players;player_keys=314.p.';
$yahoo_url_suffix = '/stats;type=week;week=';

// Load 2013 game data from JSON fixture file
$gamedata_string = file_get_contents('../data/fixtures/GameDataPoints2013.json');
$gamedata_json = json_decode($gamedata_string, true);

// Load Player data from JSON fixture file
$players_string = file_get_contents('../game/fixtures/Player2014.json');
$players_json = json_decode($players_string, true);

// Go through each player
foreach ($players_json as $player_index=>$player) {
    //if ($player_index < 1331) continue;

    // Get player's Yahoo ID and open the API URL
    $yahoo_id = $player['fields']['yahoo_id'];

    // Loop through each week in the season
    foreach (range(1, 17) as $week_num) {
        print $player_index.'/1486 '.$player['pk'].' '.$player['fields']['name'] . ' W' . $week_num . ' ';
        // Get the corresponding data point
        $dp = getPointById($player['pk'].'13'.sprintf('%02s', $week_num), $gamedata_json);
        if (is_null($dp)) {
            print 'NULL DP' . "\n";
            continue;
        } else if (is_null($yahoo_id)) {
            print 'NULL YAHOO_ID' . "\n";
            $dp['fields']['bonus40YdPassTDs'] = 0;
            $dp['fields']['bonus40YdRushTDs'] = 0;
            $dp['fields']['bonus40YdRecTDs'] = 0;
            fwrite($outfile, dpFixtureString($dp));
            continue;
        }

        // Fetch the data from the Yahoo API
        $player_url = $yahoo_url_prefix . $yahoo_id . $yahoo_url_suffix . $week_num;
        try {
            if ($o->fetch($player_url)) {
                $xmlResponse = simplexml_load_string($o->getLastResponse());
                $statArray = $xmlResponse->players->player->player_stats->stats;
                fwrite($outfile, dpFixtureString(getStats(
                    $statArray, $player, $week_num, $dp, $stat_categories, $bonus_stat_categories)));
            } else {
                print "Couldn't fetch\n";
            }
        } catch (OAuthException $e) {
            print 'Error: ' . $e->getMessage() . "\n";
        }
    }
}

fclose($outfile);


///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// HELPER METHODS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Gets the relevant stats from the stat array and compares to the player's stats
function getStats($statArray, $player, $week_num, $dp, $stat_categories, $bonus_stat_categories) {
    $new_dp = $dp;

    // First compare Yahoo's stats to what we have
    foreach ($stat_categories as $stat_name=>$stat_cat_num) {
        foreach ($statArray->children() as $s) {
            $cur_stat_cat_num = (int) $s->stat_id;
            if ($cur_stat_cat_num == $stat_cat_num) {
                $stat_val = (int) $s->value;
                if ($stat_val != $dp['fields'][$stat_name]) {
                    print $stat_name . ': ' . $dp['fields'][$stat_name] . ', yahoo: ' . $stat_val . '; ';
                    $new_dp['fields'][$stat_name] = $stat_val;
                    //fwrite($outfile, $player['pk'].' '.$player['fields']['name'].' W'.$week_num.' '.
                    //    $stat_name.': '.$dp['fields'][$stat_name].', yahoo: '.$stat_val."\n");
                } 
            }
        }
    }

    // Get bonus points stats
    $bonus_pts = 0;
    foreach ($bonus_stat_categories as $bonus_stat_name=>$bonus_stat_cat_num) {
        foreach ($statArray->children() as $s) {
            $cur_stat_cat_num = (int) $s->stat_id;
            if ($cur_stat_cat_num == $bonus_stat_cat_num) {
                $bonus_stat_val = (int) $s->value;
                $new_dp['fields']['bonus'.$bonus_stat_name] = $bonus_stat_val;
            }
        }
    }

    $new_dp['fields']['points'] = computeFantasyPoints($new_dp);
    print_r($new_dp);
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

// Computes the number of (offensive) fantasy points from the given data point
function computeFantasyPoints($dp) {
    $pts = ( ($dp['fields']['rushTDs']*6) + ($dp['fields']['recTDs']*6) + 
        ($dp['fields']['miscTDs']*6) + ($dp['fields']['passTDs']*4) + 
        ($dp['fields']['misc2pc']*2) + floor($dp['fields']['rushYds']/10) + 
        floor($dp['fields']['recYds']/10) + floor($dp['fields']['passYds']/25) );
    $pts = $pts - ($dp['fields']['passInt']*2) - ($dp['fields']['miscFuml']*2);
    $pts = $pts + (($dp['fields']['bonus40YdPassTDs']*2) + 
        ($dp['fields']['bonus40YdRushTDs']*2) + ($dp['fields']['bonus40YdRecTDs']*2));
    return $pts;
}

// Retrieves the point from the GameDataPoint dataset with the given ID
function getPointById($id, $dataset) {
    foreach ($dataset as $dp) {
        if ($dp['pk'] == $id) {
            return $dp;
        }
    }
    return NULL;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SEASON CODES
///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 2001-2012 at https://developer.yahoo.com/fantasysports/guide/game-resource.html#game-resource-key_format
// 2013 is 314
// 2014 is 331

?>
        