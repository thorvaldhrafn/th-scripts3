import re
import os
import glob
import socket
import dns.resolver
import dns.exception
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

def nginx_inc_grep(chk_conf, dname="", list_confs=None):
    if list_confs is None:
        list_confs = set()

    if not os.path.isabs(chk_conf):
        chk_conf = os.path.join(dname, chk_conf)

    chk_conf_list = []
    if os.path.isfile(chk_conf):
        chk_conf_list.append(chk_conf)
    else:
        chk_conf_list.extend(glob.glob(chk_conf))

    for cfile in chk_conf_list:
        if os.path.islink(cfile):
            cfile = os.readlink(cfile)
            if not os.path.isabs(cfile):
                cfile = os.path.join(dname, cfile)

        if cfile not in list_confs:
            list_confs.add(cfile)
            current_dir = os.path.dirname(cfile)
            try:
                with open(cfile, 'r', errors='ignore') as ngnx_file:
                    for line in ngnx_file:
                        line = line.strip()
                        if line.startswith('include ') or line.startswith('include\t'):
                            file_mask = re.sub(r'^include\s+', '', line).strip()
                            nginx_inc_grep(file_mask, current_dir, list_confs)
            except IOError:
                continue

    return list(list_confs)


def vhost_list(nginxconf_path):
    host_set = set()
    conf_files = nginx_inc_grep(nginxconf_path, os.path.dirname(nginxconf_path))

    for fconf in conf_files:
        try:
            with open(fconf, 'r', errors='ignore') as fconf_file:
                for line in fconf_file:
                    line = line.strip()
                    if line.startswith('server_name ') or line.startswith('server_name\t'):
                        host_string = re.sub(r'^server_name\s+', '', line)
                        host_string = host_string.rstrip(';').strip()

                        hosts = [h for h in host_string.split() if h]
                        host_set.update(hosts)
        except IOError:
            continue

    return list(host_set)


def serv_ip_list():
    ips_set = set()
    ip_proto = socket.AF_INET
    for _, snic_addrs in psutil.net_if_addrs().items():
        for snic_addr in snic_addrs:
            if snic_addr.family == ip_proto:
                ips_set.add(snic_addr.address)
    return ips_set


def _worker_check_dns(vhost, ip_list, host_set):
    """
    Worker function executed by individual threads.
    Processes a single vhost and returns its classification data.
    """
    # Skip catch-all blocks or wildcards early to save network time
    if vhost.startswith('_') or vhost.startswith('*') or not vhost:
        return None

    # Thread-local resolver initialization
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '1.1.1.1']
    resolver.timeout = 2.0
    resolver.lifetime = 2.0

    result = {
        "domains": {},
        "wrong_domains": {},
        "aliases": {},
        "wrong_aliases": []
    }

    try:
        # 1. Try resolving A Record
        a_records = resolver.resolve(vhost, "A")
        for rdata in a_records:
            host_ip = str(rdata)
            if host_ip in ip_list:
                result["domains"][vhost] = host_ip
            else:
                result["wrong_domains"][vhost] = host_ip
            break  # Evaluating the primary mapped IP is generally enough

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        # 2. Try resolving CNAME Record if A record is absent
        try:
            cname_records = resolver.resolve(vhost, "CNAME")
            for rdata in cname_records:
                hname = str(rdata).rstrip('.')
                if hname in host_set:
                    result["aliases"][hname] = vhost
                else:
                    result["wrong_aliases"].append(vhost)
                break
        except dns.exception.DNSException:
            pass
    except dns.exception.DNSException:
        pass

    return result


def check_vhost(host_list, param, max_workers=20):
    aliases = dict()
    wrong_aliases = list()
    domains = dict()
    wrong_domains = dict()

    ip_list = serv_ip_list()
    host_set = set(host_list)

    # Run DNS lookups in parallel using a ThreadPool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_worker_check_dns, vhost, ip_list, host_set): vhost for vhost in host_list}

        for future in as_completed(futures):
            res = future.result()
            if not res:
                continue

            # Safely merge thread results back into main collections
            domains.update(res["domains"])
            wrong_domains.update(res["wrong_domains"])
            wrong_aliases.extend(res["wrong_aliases"])

            for hname, vhost in res["aliases"].items():
                aliases.setdefault(hname, []).append(vhost)

    full_data = {
        "domains": domains,
        "wrong_aliases": wrong_aliases,
        "aliases": aliases,
        "wrong_domains": wrong_domains
    }

    if param == "all":
        return full_data
    return full_data.get(param, None)


def result_list(type_list="all", conf_path="/etc/nginx/nginx.conf"):
    if not os.path.exists(conf_path):
        return "Nginx not installed or config path invalid"

    host_list = vhost_list(conf_path)
    return check_vhost(host_list, type_list)
