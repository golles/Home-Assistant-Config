#!/usr/bin/env bash

set_day_night_mode () {
    # $1 = host
    # $2 = username
    # $3 = password
    # $4 = mode: day | night | auto

    # 0=Auto, 1=Manual, 2=Always Day Mode, 3=Always Night Mode, 4=Day Mode Schedule
    MODE=0
    case $4 in
      day)
        MODE=2
        ;;
      night)
        MODE=3
        ;;
    esac

    curl -s --user $2:$3 http://$1/setDayNightMode --referer http://$1 --data "DayNightMode=$MODE&ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&ConfigDayNightMode=Save" >/dev/null 2>&1
}

set_day_night_mode $1 $2 $3 $4
