#!/usr/bin/env bash

__nginx_conf_paths() {
  chck_path="$1"
  includes=$(grep -E "(\s*|\t*)include.*" "${chck_path}" | awk '{ print $2 }' | sed -r 's/;$//')
  for i in ${includes}; do
    dname=$(dirname "${i}" | head -n1)
    if [[ "${dname}" = "." ]]; then
      dname=$(dirname "${chck_path}")
    fi
    fname_tmp=$(basename "${i}")
    confs=$(find "${dname}" -type f -name "$fname_tmp" print0 | xargs)
    check=$(echo "$confs" | wc -w)
    if [[ ${check} -eq 1 ]]; then
      CONF_LIST="$CONF_LIST $confs"
      fname=$(basename "${i}")
      full_fname="${dname}/$fname"
      if grep -E "(\s*|\t*)include.*" "${full_fname}"; then
        __nginx_conf_paths "${full_fname}"
      fi
    else
      for j in ${confs}; do
        CONF_LIST="${CONF_LIST} ${confs}"
        fname=$(basename "${j}")
        full_fname="${dname}/$fname"
#        if [[ $? -eq 0 ]]; then
        __nginx_conf_paths "${full_fname}"
#        fi
      done
    fi
  done
}

nginx_conf_paths() {
  __nginx_conf_paths "${1}"
  for i in ${CONF_LIST}; do echo "${i}"; done | sort -u | xargs
}

vesta_usr_list() {
  for USER in $(VESTA=/usr/local/vesta /usr/local/vesta/bin/v-list-users plain | awk '{ print $1 }' | xargs); do
    if grep "${USER}" /etc/passwd; then
      vst_users="${vst_users} ${USER}"
    fi
  done
  echo "${vst_users}"
}

vesta_domain_list() {
  VESTA=/usr/local/vesta /usr/local/vesta/bin/v-list-web-domains "${1}" plain | awk '{ print $1 }' | xargs
}

get_publ_ip() {
  dig +short myip.opendns.com @resolver1.opendns.com
}

teleg_alert() {
  tg_url=$1
  tg_chat_id=$2
  shift 2
  send_messg="$*"
  curl -s -X POST "$tg_url" -d chat_id="$tg_chat_id" -d text="$send_messg"
}
