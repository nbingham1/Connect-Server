<?php
error_reporting(-1);
ini_set('display_errors', 'On');

if (isset($_GET['code'])) {
	$url = 'https://api.moves-app.com/oauth/v1/access_token';
        $data = array('grant_type' => 'authorization_code', 'code' => $_GET['code'], 'client_id' => 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1', 'client_secret' => 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch', 'redirect_uri' => 'http://connect.sol-union.com/auth.php');

	$ch = curl_init();

	curl_setopt($ch, CURLOPT_URL,$url);
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));

	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

	$result = curl_exec ($ch);

	curl_close ($ch);
	
	print $result;
}

if (isset($_GET['refresh_token'])) {
	$url = 'https://api.moves-app.com/oauth/v1/access_token';
        $data = array('grant_type' => 'refresh_token', 'refresh_token' => $_GET['refresh_token'], 'client_id' => 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1', 'client_secret' => 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch');

        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL,$url);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        $result = curl_exec ($ch);

        curl_close ($ch);

        print $result;
}
?>
