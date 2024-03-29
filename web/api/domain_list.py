import re
import os
import dns.resolver
import socket
import psutil
import glob


def nginx_inc_grep(chk_conf, dname="", list_confs=None):
    if list_confs is None:
        list_confs = list()
    tmp_file_list = list()
    chk_conf_list = list()
    if not os.path.isabs(chk_conf):
        chk_conf = dname + "/" + chk_conf
    if os.path.isfile(chk_conf):
        chk_conf_list.append(chk_conf)
    else:
        chk_conf_list = chk_conf_list + glob.glob(chk_conf)
    for cfile in chk_conf_list:
        if not list_confs.count(cfile):
            if os.path.islink(cfile):
                cfile = os.readlink(cfile)
            list_confs.append(cfile)
            with open(cfile, 'r') as ngnx_file:
                for line in ngnx_file:
                    if re.match('(\\s*|\t*)include.*', line):
                        file_mask = re.sub('(\\s*|\t*)include(\\s+|\t+)', '', line, count=1)
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
                if re.match('(\\s*|\t*)server_name(\\s+|\t+)', line):
                    host_string = re.sub('(\\s*|\t*)server_name(\\s+|\t+)', '', line, count=1)
                    host_string = re.sub(';\n', '', host_string, count=1)
                    tmp_host_list.append(host_string)
                    for i in tmp_host_list:
                        host_list = host_list + i.split(" ")
    host_list = list(set(host_list))
    host_list = [_f for _f in host_list if _f]
    return host_list


def serv_ip_list():
    ips_list = list()
    ip_proto = socket.AF_INET
    for if_name, snic_addrs in psutil.net_if_addrs().items():
        for snic_addr in snic_addrs:
            if snic_addr.family == ip_proto:
                ips_list.append(snic_addr.address)
    return ips_list


def check_vhost(host_list, param):
    aliases = dict()
    wrong_aliases = list()
    domains = dict()
    wrong_domains = dict()
    ip_list = serv_ip_list()
    google_resolver = dns.resolver.Resolver()
    google_resolver.nameservers = ['8.8.8.8', '1.1.1.1']
    for vhost in host_list:
        try:
            for rdata in google_resolver.resolve(vhost, "A"):
                host_ip = str(rdata)
                if host_ip in ip_list:
                    domains[vhost] = host_ip
                else:
                    wrong_domains[vhost] = host_ip
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.Timeout:
            pass
        except dns.exception.DNSException:
            pass
    for vhost in list(domains.keys()):
        try:
            for rdata in google_resolver.resolve(vhost, "CNAME"):
                hname = str(rdata).strip('.')
                if host_list.count(hname):
                    if list(aliases.keys()).count(hname):
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
        full_data = dict(domains=domains, wrong_aliases=wrong_aliases, aliases=aliases, wrong_domains=wrong_domains)
        return full_data
    elif param == "domains":
        return domains
    elif param == "wrong_aliases":
        return wrong_aliases
    elif param == "aliases":
        return aliases
    elif param == "wrong_domains":
        return wrong_domains


def result_list(type_list="all", conf_path="/etc/nginx/nginx.conf"):
    host_list = vhost_list(conf_path)
    if os.path.exists(conf_path):
        return check_vhost(host_list, type_list)
    else:
        return "Nginx not installed"
