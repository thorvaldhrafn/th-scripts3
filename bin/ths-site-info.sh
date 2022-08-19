#!/usr/bin/env bash

THS_PATH="/usr/local/thscripts"

. ${THS_PATH}/etc/global.conf
. ${THS_PATH}/etc/functions.sh

if [[ -z $1 ]]; then
  echo "Set the domain name as an argument"
  exit 0
fi

domain_fi=$1

CONF_LIST=$(nginx_conf_paths /etc/nginx/nginx.conf)

for n in ${CONF_LIST}; do
  domain_list=$(grep -E "^[[:blank:]]*server_name.+" "${n}" | grep -v localhost | awk '{ print $1=""; print $0 }' | sed 's/;//')
  if echo "${domain_list}" | grep -E "[[:blank:]]*${domain_fi}[[:blank:]]"; then
    root_path=$(grep -E "^[[:blank:]]*root[[:blank:]]*.+" "${n}" | awk '{ print $2 }' | sed 's/;//')
    if [[ -n ${root_path} ]]; then
      conf_path=${n}
      break
    fi
  fi
done

site_user=$(stat -c "%U" "${root_path}")

if [[ -e ${root_path}/wp-config.php ]]; then
  site_dbs=$(grep DB_NAME "${root_path}"/wp-config.php | awk '{ print $2 }' | awk -F"'" '{ print $2 }')
fi

echo "site_user=${site_user} root_path=${root_path} site_dbs=${site_dbs} conf_path=${conf_path}"
