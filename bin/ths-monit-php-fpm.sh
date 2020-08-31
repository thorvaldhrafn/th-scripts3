#!/bin/bash

THS_PATH="/usr/local/thscripts"

. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

if [[ -e /var/lock/monit-php-fpm.lock ]]
    then
        PID=`cat /var/lock/monit-php-fpm.lock`
        ps aux | awk '{ print $2 }' | grep ${PID} > /dev/null
        if [[ $? -eq 0 ]]
            then
                exit 0
        fi
    else
        echo $$ > /var/lock/monit-php-fpm.lock
fi

if [[ -n ${1} ]]
    then
        CHECK_URL=${1}
    else
        echo "You must set url for monitoring"
        exit 1
fi

http_code=`curl -I -s -S --connect-timeout 40 ${CHECK_URL} | grep "HTTP/" | awk '{ print $2 }' | cut -c -1`
counter=1
date=`date '+%F-%H:%M'`

while [[ ${http_code} -eq 5 && ${counter} -lt 5 ]]
    do
        /bin/systemctl stop php-fpm.service &> /dev/null
        sleep 10
        /bin/systemctl start php-fpm.service &> /dev/null
        http_code=`curl -I -s -S --connect-timeout 40 ${CHECK_URL} | grep "HTTP/" | awk '{ print $2 }' | cut -c -1`
        echo "service php-fpm has been restarted on $date at $counter time" >> /root/monit-php-fpm.log
        counter=$(($counter+1))
        sleep 20
    done

if [[ ${http_code} -eq 5 ]]
    then
        /bin/systemctl stop mariadb &> /dev/null
        sleep 10
        /bin/systemctl start mariadb &> /dev/null
        sleep 20
        http_code=`curl -I -s -S --connect-timeout 40 ${CHECK_URL} | grep "HTTP/" | awk '{ print $2 }' | cut -c -1`
        echo "service mariadb has been restarted on $date" >> /root/monit-php-fpm.log
fi

if [[ ${http_code} -eq 5 ]]
        then
                echo "service php-fpm can't work after $counter restart" | mail -s "PHP-fpm on ${CHECK_URL}" $MAIL
fi

rm /var/lock/monit-php-fpm.lock
exit 0
