#!/usr/bin/env bash

THS_PATH="/usr/local/thscripts"

. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

if [[ -d /usr/local/vesta ]]
    then
        for USER in `vesta_usr_list`
            do
                for DOMAIN in `vesta_domain_list ${USER}`
                    do
                        path="/home/${USER}/conf/web/php-fpm.${DOMAIN}.conf"
                            if [[ ! -f ${path} ]]
                                then
                                    echo /home/${USER}/conf/web/php-fpm.${DOMAIN}.conf
                                    touch /home/${USER}/conf/web/php-fpm.${DOMAIN}.conf
                                fi
                    done
            done
fi

exit 0
