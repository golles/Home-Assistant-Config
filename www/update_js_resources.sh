#!/usr/bin/env bash

RESOURCES=$(cat <<'EOF'
auto-entities.js                https://raw.githubusercontent.com/thomasloven/lovelace-auto-entities/master/auto-entities.js
battery-state-card.js           https://github.com/maxwroc/battery-state-card/releases/latest/download/battery-state-card.js
button-card.js                  https://github.com/custom-cards/button-card/releases/latest/download/button-card.js
elapsed-time-entity-row.js      https://github.com/golles/lovelace-elapsed-time-entity-row/releases/latest/download/elapsed-time-entity-row.js
fold-entity-row.js              https://raw.githubusercontent.com/thomasloven/lovelace-fold-entity-row/master/fold-entity-row.js
mini-graph-card-bundle.js       https://github.com/kalkih/mini-graph-card/releases/latest/download/mini-graph-card-bundle.js
mini-media-player-bundle.js     https://github.com/kalkih/mini-media-player/releases/latest/download/mini-media-player-bundle.js
multiple-entity-row.js          https://github.com/benct/lovelace-multiple-entity-row/releases/latest/download/multiple-entity-row.js
simple-thermostat.js            https://github.com/nervetattoo/simple-thermostat/releases/latest/download/simple-thermostat.js
swipe-navigation.js             https://raw.githubusercontent.com/maykar/lovelace-swipe-navigation/master/swipe-navigation.js
template-entity-row.js          https://raw.githubusercontent.com/thomasloven/lovelace-template-entity-row/master/template-entity-row.js
EOF
)

echo "$RESOURCES" | while IFS= read -r line ; do 
    JS_FILE=${line% *}
    REMOTE_FILE=${line#* }
    # rm $JS_FILE
    curl -sL $REMOTE_FILE --output $JS_FILE
done

git status .
