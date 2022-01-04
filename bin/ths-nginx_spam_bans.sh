#!/bin/bash

USER=""
DOMAIN=""

act_f2b_bans=$(fail2ban-client get nginx-wp-loginxmlrpc banip)

for i in $act_f2b_bans; do
  grep "deny ${i};" /home/${USER}/conf/web/bans.${DOMAIN}.conf > /dev/null
  if [[ $? -eq 1 ]]; then
    echo "deny ${i};" >> /home/${USER}/conf/web/bans.${DOMAIN}.conf
  fi
done

/bin/systemctl reload nginx