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

CONF_LIST=`nginx_conf_paths /etc/nginx/nginx.conf`

for n in ${CONF_LIST}
	do
		domain_list=`egrep "^[[:blank:]]*server_name.+" ${n} | grep -v localhost | awk '{ print $1=""; print $0 }' | sed 's/;//'`
		for m in `echo ${domain_list} | sed '/^$/d' | sed 's/\ /\n/' | sort | uniq`
			do
			host ${m} | grep ${SERVER_IP} &> /dev/null
			if [[ $? -eq 0 ]]
				then
				root_path=`egrep "^[[:blank:]]*root[[:blank:]]*.+" ${n} | awk '{ print $1=""; print $0 }' | sed 's/;//'`
				result_root_path="$result_root_path $root_path"
				break
			fi
		done
done
echo $(echo ${result_root_path} | tr ' ' '\n' | egrep -v "^www\." | sort -u)
exit 0