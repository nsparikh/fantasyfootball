<?php

$consumer_key = 'dj0yJmk9M1dNVnJvODNJYzhRJmQ9WVdrOWMyWnhkbVV3Tm0wbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD0wMg--';
$consumer_secret = '5f20e6490769986958f3d7ad64656982fd86a822';

$o = new OAuth($consumer_key, $consumer_secret, 
                OAUTH_SIG_METHOD_HMACSHA1,
                OAUTH_AUTH_TYPE_URI);

$url = 'http://fantasysports.yahooapis.com/fantasy/v2/players;player_keys=314.p.25711/stats;type=week;week=1';
// Season codes:
// 2001-2012 at https://developer.yahoo.com/fantasysports/guide/game-resource.html#game-resource-key_format
// 2013 is 314
// 2014 is 331
try {
    if ($o->fetch($url)) {
        print $o->getLastResponse();
        print "Successful fetch\n";
    } else {
        print "Couldn't fetch\n";
    }
} catch (OAuthException $e) {
    print 'Error: ' . $e->getMessage() . "\n";
    print 'Response: ' . $e->lastResponse . "\n";
}

?>
        