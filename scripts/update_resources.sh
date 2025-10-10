#!/usr/bin/env bash


set -e


SCRIPT_DIR="$(cd -- "$(dirname "$0")" && pwd)"
HASS_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="$SCRIPT_DIR/resources"



##
# Update resources from a JSON file
#
# Arguments:
#   $1 - JSON file name (e.g. javascript.json)
#   $2 - Output folder (relative to parent of script)
##
update_resources_json () {
    OUTDIR="$HASS_DIR/$2"
    mkdir -p "$OUTDIR"
    jq -c '.[]' "$RESOURCES_DIR/$1" | while read -r item; do
        FILE=$(echo "$item" | jq -r '.file')
        URL=$(echo "$item" | jq -r '.url')
        echo "Updating $FILE..."
        curl -sL "$URL" --output "$OUTDIR/$FILE"
    done
    git status "$OUTDIR"
}


##
# Update all JavaScript resources
##
update_javascript () {
    update_resources_json "javascript.json" www
}


##
# Update all theme resources
##
update_themes () {
    update_resources_json "themes.json" themes
}


##
# Update all custom components
#
# For each component defined in custom_components.json:
#   - Clone if missing
#   - Checkout the specified ref (branch or tag)
#   - Pull if on a branch, skip if on a tag
##
update_custom_components () {
    mkdir -p "$HASS_DIR/external"
    mkdir -p "$HASS_DIR/custom_components"
    jq -c '.[]' "$RESOURCES_DIR/custom_components.json" | while read -r item; do
        NAME=$(echo "$item" | jq -r '.name')
        REPO=$(echo "$item" | jq -r '.repository')
        REF=$(echo "$item" | jq -r '.ref')
        FOLDER="$HASS_DIR/external/${NAME}"
        if [ ! -d "$FOLDER" ]; then
            echo "Downloading $NAME..."
            git clone "$REPO" "$FOLDER"
            cd "$FOLDER"
            echo "Checking out ref $REF..."
            git checkout "$REF"
            cd - >/dev/null
            ln -sf "../external/${NAME}/custom_components/${NAME}" "$HASS_DIR/custom_components/${NAME}"
        else
            cd "$FOLDER"
            CURRENT_REF=$(git rev-parse --abbrev-ref HEAD)
            if [ "$CURRENT_REF" != "$REF" ]; then
                echo "Switching $NAME from ref $CURRENT_REF to $REF..."
                git fetch --tags
                git checkout "$REF"
            fi
            echo "Updating $NAME on ref $REF..."
            BRANCH_NAME=$(git symbolic-ref --short -q HEAD || true)
            if [ -n "$BRANCH_NAME" ]; then
                git pull || true
            else
                echo "Ref $REF is a tag or detached HEAD, skipping git pull."
            fi
            cd - >/dev/null
        fi
    done
}


##
# Update all resources: JavaScript, themes, and custom components
##
update_all () {
    echo "Updating javascript"
    update_javascript
    echo -e "\nUpdating themes"
    update_themes
    echo -e "\nUpdating custom components"
    update_custom_components
}


##
# Print usage information for the script
##
usage () {
    echo "This program requires 1 argument, eg."
    echo "  all - Update all resources"
    echo "  custom_components - Update all custom components"
    echo "  javascript - Update all javascript resources"
    echo "  js - Update all javascript resources"
    echo "  themes - Update all theme resources"
}


##
# Main script logic
# Sets working directory and dispatches to the correct update function
##
cd "$HASS_DIR"

case $1 in
    all)                update_all ;;
    javascript|js)      update_javascript ;;
    themes)             update_themes ;;
    custom_components)  update_custom_components ;;
    *)                  echo "Bad input"; usage; exit 1 ;;
esac
