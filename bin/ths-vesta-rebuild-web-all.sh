#!/usr/bin/env bash
#Example script for work with some tasks with VestaCP users

THS_PATH="/usr/local/thscripts"

. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

if [[ -d /usr/local/vesta ]]
    then
        for USER in `vesta_usr_list`
        do
            v-rebuild-web-domains ${USER}
        done
fi