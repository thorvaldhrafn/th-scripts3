#!/usr/bin/env 

import re
import os
import fnmatch
import subprocess
import dns.resolver


def nginx_inc_grep(chk_conf, dname="", list_confs=list()):
    tmp_file_list = list()
    chk_conf_list = list()
    if os.path.isfile(chk_conf):
        chk_conf_list.append(chk_conf)
    elif os.path.isdir(chk_conf):
        folder = os.path.dirname(chk_conf) + "/"
        folder_list = list()
        for i in os.walk(folder):
            folder_list.append(i)
        for j in folder_list[0][2]:
            chk_conf_list.append(folder + j)
    elif os.path.isdir(os.path.dirname(chk_conf)):
        folder = os.path.dirname(chk_conf) + "/"
        folder_list = list()
        pattrn = os.path.basename(chk_conf)
        for i in os.walk(folder):
            folder_list.append(i)
        for j in fnmatch.filter(folder_list[0][2], pattrn):
            chk_conf_list.append(folder + j)
    else:
        chk_conf_list.append(dname + "/" + chk_conf)
    for cfile in chk_conf_list:
        if not list_confs.count(cfile):
            list_confs.append(cfile)
            with open(cfile, 'r') as ngnx_file:
                for line in ngnx_file:
                    if re.match('(\s*|\t*)include.*', line):
                        file_mask = re.sub('(\s*|\t*)include(\s+|\t+)', '', line, count=1)
                        file_mask = re.sub(';\n', '', file_mask, count=1)
                        tmp_file_list.append(file_mask)
                        for f in tmp_file_list:
                            nginx_inc_grep(f, "/etc/nginx", list_confs)
    return list_confs


def vhost_list(nginxconf_path):
    host_list = list()
    for fconf in nginx_inc_grep(nginxconf_path):
        tmp_host_list = list()
        with open(fconf, 'r') as fconf_file:
            for line in fconf_file:
                if re.match('(\s*|\t*)server_name(\s+|\t+)', line):
                    host_string = re.sub('(\s*|\t*)server_name(\s+|\t+)', '', line, count=1)
                    host_string = re.sub(';\n', '', host_string, count=1)
                    tmp_host_list.append(host_string)
                    for i in tmp_host_list:
                        host_list = host_list + i.split(" ")
    host_list = list(set(host_list))
    host_list = filter(None, host_list)
    return host_list


def serv_ip_list():
    output = subprocess.Popen("hostname --all-ip-addresses", shell=True, stdout=subprocess.PIPE)
    ips = output.communicate()[0].rstrip()
    ips_list = ips.strip(' \n').split(" ")
    return ips_list


def check_vhost(host_list, param):
    aliases = dict()
    wrong_aliases = list()
    domains = dict()
    ip_list = serv_ip_list()
    for vhost in host_list:
        try:
            for rdata in dns.resolver.query(vhost, "A"):
                host_ip = str(rdata)
                if ip_list.count(host_ip):
                    domains[vhost] = host_ip
        except dns.resolver.NXDOMAIN:
            pass
            # print "No such domain %s" % vhost
        except dns.resolver.Timeout:
            pass
            # print "Timed out while resolving %s" % vhost
        except dns.exception.DNSException:
            pass
            # print "Unhandled exception"
    for vhost in domains.keys():
        try:
            for rdata in dns.resolver.query(vhost, "CNAME"):
                hname = str(rdata).strip('.')
                if host_list.count(hname):
                    if aliases.keys().count(hname):
                        tmp_lst = aliases.get(hname)
                        tmp_lst.append(vhost)
                    else:
                        tmp_lst = list()
                        tmp_lst.append(vhost)
                    aliases[hname] = tmp_lst
                else:
                    wrong_aliases.append(vhost)
            domains.pop(vhost, None)
        except dns.resolver.NoAnswer:
            pass
    if param == "all":
        full_data = dict(domains=domains, wrong_aliases=wrong_aliases, aliases=aliases)
        return full_data
    elif param == "domains":
        return domains
    elif param == "wrong_aliases":
        return wrong_aliases
    elif param == "aliases":
        return aliases


def result_list(type_list="all", conf_path="/etc/nginx/nginx.conf"):
    host_list = vhost_list(conf_path)
    if os.path.exists(conf_path):
        return check_vhost(host_list, type_list)
    else:
        return "Nginx not installed"
