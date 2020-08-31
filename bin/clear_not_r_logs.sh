#!/usr/bin/env bash
#Check nginxs logs for accessibly by zabbix

not_r_log_list=`sudo -u zabbix find /var/log/nginx/ -type f -name "*.log" ! -readable 2>/dev/null`

for i in ${not_r_log_list}
    do
        rm -v ${i}
        systemctl restart nginx
    done