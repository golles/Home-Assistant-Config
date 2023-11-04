#!/usr/bin/env bash

# Info about username password:
# You should use your own username
# For the password I strongly advise to create a 'Login Key' that has alowance for CMD_API_DNS_CONTROL.

if [[ "$#" -ne 6 ]]; then
    echo "Usage: $0 username password direct_admin_server domain subdomain ip"
    exit 1
fi

url_encode() {
    # $1 = string
    old_lc_collate=$LC_COLLATE
    LC_COLLATE=C

    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
    done

    LC_COLLATE=$old_lc_collate
}

url_decode() {
    # $1 = string
    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

remove_existing_record () {
    # $1 = username
    # $2 = password
    # $3 = direct_admin_server
    # $4 = domain
    # $5 = subdomain
    curl -s --user $1:$2 "${3}/CMD_API_DNS_CONTROL?domain=${4}&action=select&arecs0=name%3D${5}"
}

add_new_record() {
    # $1 = username
    # $2 = password
    # $3 = direct_admin_server
    # $4 = domain
    # $5 = subdomain
    # $6 = ip address
    curl -s --user $1:$2 "${3}/CMD_API_DNS_CONTROL?domain=${4}&action=add&type=A&name=${5}&value=${6}"
}

subdomain_encoded=$(url_encode $5)
#echo "Encoded subdomain: ${subdomain_encoded}"

remove_result=$(remove_existing_record $1 $2 $3 $4 $subdomain_encoded)
#echo "Delete result: ${remove_result}"

if [[ ${remove_result} = error=0* ]]; then
    echo "Successfully deleted previous record"
else
    echo "Failed deleting record: $(url_decode $remove_result)"
    exit 2
fi

add_result=$(add_new_record $1 $2 $3 $4 $subdomain_encoded $6)
#echo "Add result: ${add_result}"

if [[ ${add_result} = error=0* ]]; then
    echo "Successfully added updated record"
else
    echo "Failed adding record: $(url_decode $add_result)"
    exit 3
fi

exit 0

