#!/bin/bash

THS_PATH="/usr/local/thscripts"

. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

if [[ ! -e /etc/nginx/nginx.conf ]]
    then
        echo "Nginx is not installed"
        exit 0
fi

SERVER_IP=`get_publ_ip`

nginx_conf_paths /etc/nginx/nginx.conf

for n in ${CONF_LIST}
	do
		domain_list=`egrep "^[[:blank:]]*server_name.+" ${n} | grep -v localhost | awk '{ print $1=""; print $0 }' | sed 's/;//'`
		for m in `echo ${domain_list} | sed '/^$/d' | sed 's/\ /\n/' | sort | uniq`
			do
				host ${m} | grep ${SERVER_IP} &> /dev/null
				if [[ $? -eq 0 ]]
					then
					result_domain_list="$result_domain_list $m"
				fi
	done
done
echo $(echo ${result_domain_list} | tr ' ' '\n' | egrep -v "^www\." | sort -u)
exit 0
