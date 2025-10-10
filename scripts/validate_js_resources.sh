#!/usr/bin/env bash


set -e

JSON_FILE="$(dirname "$0")/resources/javascript.json"
YAML_FILE="$(dirname "$0")/../lovelace/resources.yaml"

# Get all filenames from JSON
json_files=$(jq -r '.[].file' "$JSON_FILE")

# Get all /local/ URLs from YAML
yaml_local_urls=$(grep -E '^\s*- url: /local/' "$YAML_FILE" | awk '{print $3}')


# Check for missing in JSON (stale in YAML)
missing_json=()
for url in $yaml_local_urls; do
	fname=$(basename "$url")
	if ! echo "$json_files" | grep -qx "$fname"; then
		missing_json+=("$fname")
	fi
done

# Check for missing in YAML (stale in JSON)
yaml_filenames=$(for url in $yaml_local_urls; do basename "$url"; done)
missing_yaml=()
for fname in $json_files; do
	if ! echo "$yaml_filenames" | grep -qx "$fname"; then
		missing_yaml+=("$fname")
	fi
done

if [ ${#missing_json[@]} -gt 0 ]; then
	echo "Stale in YAML (not referenced in JSON):"
	for f in "${missing_json[@]}"; do
		echo "  $f"
	done
fi

if [ ${#missing_yaml[@]} -gt 0 ]; then
	echo "Stale in JSON (not referenced in YAML):"
	for f in "${missing_yaml[@]}"; do
		echo "  $f"
	done
fi

if [ ${#missing_json[@]} -eq 0 ] && [ ${#missing_yaml[@]} -eq 0 ]; then
	echo "All resources are in sync."
	exit 0
else
	exit 1
fi


