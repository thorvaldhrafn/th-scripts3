#!/usr/bin/env bash

install_param=$1
if [[ -n $install_param ]]; then
  if [[ $install_param != "install" && $install_param != "update" ]]; then
    exit 1
  fi
else
  exit 1
fi

if [[ $(virtualenv  --version >/dev/null 2>&1; echo $?) -ne 0 ]]; then
  exit 1
fi

mkdir /usr/local/thscripts/ 2>/dev/null
useradd -s /bin/bash -d /usr/local/thscripts/ -m thscripts 2>/dev/null

if [[ $install_param == "install" ]]; then
  if [[ -d /etc/nginx/ ]]; then
    cp confs/nginx_thscripts.conf /etc/nginx/conf.d/thscripts.conf
  fi
fi

dir_list="bin etc web"

for i in $dir_list; do
  mkdir /usr/local/thscripts/"${i}" 2>/dev/null
  rsync -aq --delete --exclude "global.conf" --exclude "th-api.conf" "${i}"/ /usr/local/thscripts/"${i}"/
done

dir_list_full="$dir_list .venv"

find /usr/local/thscripts/ -maxdepth 1 -mindepth 1 -type d | while read -r line; do
  echo "$line"
  checkr="delete"
  for j in $dir_list_full; do
    if [[ $line == "/usr/local/thscripts/${j}" ]]; then
      checkr="not_delete"
    fi
  done
  if [[ $checkr == "delete" ]]; then
    rm -r "$line"
  fi
done

if [[ ! -d /usr/local/thscripts/.venv/ ]]; then
    update_param="venv_update"
fi

cp confs/th-api.service /etc/systemd/system/
systemctl daemon-reload

if [[ $install_param == "install" || $update_param == "venv_update" ]]; then
  chown -R thscripts:thscripts /usr/local/thscripts/
  VIRT_ENV="/usr/local/thscripts/.venv/"; sed -i "s|VIRT_ENV|${VIRT_ENV}|g" /etc/systemd/system/th-api.service
  sed -i "s|SYS_PATH|${PATH}|g" /etc/systemd/system/th-api.service

  cp etc/th-api.conf /usr/local/thscripts/etc/

  cp requirements.txt /usr/local/thscripts/
  su - thscripts -c "\
  virtualenv /usr/local/thscripts/.venv/ && \
  source /usr/local/thscripts/.venv/bin/activate && \
  pip install -r requirements.txt && \
  deactivate"
  rm /usr/local/thscripts/requirements.txt

  systemctl enable th-api.service
fi

systemctl start th-api.service

cp confs/th-api.service /usr/lib/systemd/system/


if [[ $install_param == "update" && $update_param != "venv_update" ]]; then
  cp requirements.txt /usr/local/thscripts/
  su - thscripts -c "\
  source /usr/local/thscripts/.venv/bin/activate && \
  pip install -r requirements.txt && \
  deactivate"
  rm /usr/local/thscripts/requirements.txt
fi

systemctl is-active --quiet th-api.service && systemctl restart th-api.service

if [[ -d /etc/nginx/ ]]; then
    systemctl is-active --quiet nginx && systemctl reload nginx
fi
