#!/usr/bin/env bash

# Simple bash script that manages the Awtrix clock resources.

set -e

ICONS=$(cat <<'EOF'
# Weather
clear-night         52163
cloudy              52159
exceptional         52172
fog                 52167
hail                52158
lightning           52170
lightning-rainy     52171
partlycloudy        52173
pouring             52161
rainy               52160
snowy               52168
snowy-rainy         52166
sunny               52156
windy               52169
windy-variant       52169

# Climate
temp-inside         2355
# temp-outside        53084
humidity            53495

# Garbage
bio_afval           14764
restafval           14765
papier              42817

# Appliances
washing_machine     53358
dishwasher          53366
EOF
)

upload_icons () {
    local IP="$1"

    rm -rf .tmp
    mkdir -p .tmp

    echo "$ICONS" | while IFS= read -r line ; do
        if [[ -n "$line" && "$line" != \#* ]]; then
            name=${line%% *}
            icon=${line##* }
            content_type=$(curl -sL "https://developer.lametric.com/content/apps/icon_thumbs/$icon" --output ".tmp/$icon" -w "%{content_type}")

            # Files don't have an extension, add extension and convert files to supported formats.
            case "$content_type" in
                "image/jpeg")
                    # Add extension.
                    filename="$name.jpg"
                    mv ".tmp/$icon" ".tmp/$filename"
                    ;;
                "image/gif")
                    # Add extension.
                    filename="$name.gif"
                    mv ".tmp/$icon" ".tmp/$filename"
                    ;;
                "image/png")
                    # Convert png to jpg.
                    filename="$name.jpg"
                    convert ".tmp/$icon" ".tmp/$filename" ;
                    rm ".tmp/$icon"
                    ;;
                *)
                    echo "unsupported image type: $content_type"
                    exit 1
                    ;;
            esac

            curl -X POST -F "file=@.tmp/$filename;filename=/ICONS/$filename" "http://$IP/edit"
        fi
    done

    rm -rf .tmp
}

check_programs () {
    for program in convert curl; do
        if ! hash "$program" 2>/dev/null
        then
            info "$program is not installed"
            exit 2
        fi
    done
}

usage () {
    echo "This program requires the following arguments, eg."
    echo "  upload_icons <ip> - Update all icons to a give device"
}


# Make the script dir, the working directory.
cd "$(dirname "$0")"

check_programs

# $1 = User input, what to do.
case $1 in
    upload_icons)   upload_icons "$2" ;;
    *)              echo "Bad input"; usage; exit 1 ;;
esac
