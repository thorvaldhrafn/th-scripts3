#!/bin/bash

THS_PATH="/usr/local/thscripts"

# Config format for work with this script is CHECK_URL="url1;php-backend1 url2;php-backend2 ..."
# Also need add to config url of telegram bot TELEG_URL and chat id TELEG_CHAT_ID
. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

code_check() {
 if http_code=$(curl -s -o /dev/null -I -w "%{http_code}" --connect-timeout 40 "${1}"; true); then
   echo "$http_code"
 else
   echo 000
 fi
}

if [[ -e /var/lock/monit-php-fpm.lock ]]; then
  PID=$(cat /var/lock/monit-php-fpm.lock)
#  ps aux | awk '{ print $2 }' | grep "${PID}" >/dev/null
  if ps aux | awk '{ print $2 }' | grep "${PID}"; then
    exit 0
  fi
else
  echo $$ >/var/lock/monit-php-fpm.lock
fi

for i in $CHECK_URL; do
  url_f_check=${i//;*/}
  url_backnd=${i//*;/}
  counter=1
  date=$(date '+%F-%H:%M')
  while true; do
    return_code=$(code_check "$url_f_check")
    if [ "${return_code}" -eq 5 ]; then
      /bin/systemctl stop "${url_backnd}"-fpm.service &>/dev/null
      sleep 10
      /bin/systemctl start "${url_backnd}"-fpm.service &>/dev/null
      echo "service php-fpm has been restarted on $date at $counter time" >>/root/monit-php-fpm.log
    elif [ "${return_code}" -eq 000 ]; then
      /bin/systemctl stop "${url_backnd}"-fpm.service &>/dev/null
      sleep 10
      /bin/systemctl start "${url_backnd}"-fpm.service &>/dev/null
      echo "service php-fpm has been restarted on $date at $counter time" >>/root/monit-php-fpm.log
    else
      break
    fi
    if [ ${counter} -lt 5 ]; then
      counter=$((counter + 1))
    else
      publ_ip=$(get_publ_ip)
      teleg_alert "$TELEG_URL" "$TELEG_CHAT_ID" "Php backend problems on $publ_ip"
      break
    fi
  done
done

rm /var/lock/monit-php-fpm.lock
exit 0
