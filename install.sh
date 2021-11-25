#!/usr/bin/env bash

install_param=$1
if [[ -n $install_param ]]; then
  if [[ $install_param != "install" && $install_param != "update" ]]; then
    exit 1
  fi
else
  exit 1
fi

if [[ $install_param == "install" ]]; then
  mkdir /usr/local/thscripts/
  useradd -s /bin/bash -d /usr/local/thscripts/ -m thscripts
  if [[ -d /etc/nginx/ ]]; then
    cp confs/nginx_thscripts.conf /etc/nginx/conf.d/thscripts.conf
  fi
  cp confs/th-api.service /usr/lib/systemd/system/
fi

dir_list="bin etc web"

for i in $dir_list; do
  mkdir /usr/local/thscripts/"${i}"
  rsync -aq --delete --exclude=/usr/local/thscripts/etc/global.config "${i}"/ /usr/local/thscripts/"${i}"/
done

if [[ $install_param == "install" ]]; then
  VIRT_ENV="/usr/local/thscripts/.venv/"; sed -i "s|VIRT_ENV|${VIRT_ENV}|g" /usr/lib/systemd/system/th-api.service
  sed -i "s|SYS_PATH|${PATH}|g" /usr/lib/systemd/system/th-api.service

  cp requirements.txt /usr/local/thscripts/
  su - thscripts -c "\
  virtualenv --no-site-packages /usr/local/thscripts/.venv/ && \
  source /usr/local/thscripts/.venv/bin/activate && \
  pip install -r requirements.txt && \
  deactivate"
  rm /usr/local/thscripts/requirements.txt

  systemctl daemon-reload
  systemctl enable th-api.service
  systemctl start th-api.service
fi

systemctl is-active --quiet th-api.service && systemctl restart th-api.service

if [[ -d /etc/nginx/ ]]
then
    systemctl is-active --quiet nginx && systemctl reload nginx
fi
