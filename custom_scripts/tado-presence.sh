#!/bin/bash

CLIENT_SECRET="wZaRN7rpjn3FoNyF5IFuxg9uMzYJcvOoQ8QWiIqS3hfk6gLhVlG57j5YNoZL2Rtc"

if [[ "$#" -ne 3 ]]; then
    echo "Usage: $0 username password presence"
    exit 1
fi

tado_get_access_token () {
    # $1 = username
    # $2 = password
    curl -s "https://auth.tado.com/oauth/token" -d client_id=tado-web-app -d grant_type=password -d scope=home.user -d username="$1" -d password="$2" -d client_secret="$CLIENT_SECRET" | sed -n 's|.*"access_token":"\([^"]*\)".*|\1|p'
}

tado_get_home_id () {
    # $1 = access_token
    curl -s "https://my.tado.com/api/v1/me" -H "Authorization: Bearer $1" | sed -n 's|.*"homeId":\([^"]*\),.*|\1|p'
}

tado_set_presence () {
    # $1 = access_token
    # $2 = home_id
    # $3 = presence: HOME/AWAY
    curl -s -o /dev/null -w "%{http_code}" "https://my.tado.com/api/v2/homes/$2/presenceLock" -X PUT -H "Authorization: Bearer $1" -H "Content-Type: application/json;charset=utf-8" --data "{\"homePresence\":\"$3\"}"
}

access_token=$(tado_get_access_token $1 $2)
#echo "Token: ${access_token}"

home_id=$(tado_get_home_id ${access_token})
#echo "Home ID: ${home_id}"

response=$(tado_set_presence ${access_token} ${home_id} $3)
#echo "Response: ${response}"

if [[ ${response} -eq 204 ]]; then
    echo "Successfully updated presence"
    exit 0
else
    echo "Failed updating presence (http: $response)"
    exit 2
fi
