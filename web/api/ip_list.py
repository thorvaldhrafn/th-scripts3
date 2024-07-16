import socket
import psutil
import requests
import ipaddress


def get_ip_list():
    ip_addresses = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                ip_addresses.append(snic.address)
    return ip_addresses


def get_external_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        ip_data = response.json()
        return ip_data['origin']
    except requests.RequestException as e:
        print(f"Error fetching IP address: {e}")
        return None


def full_ip_list():
    ip_lst = get_ip_list()
    ext_ip = get_external_ip()
    if ext_ip:
        ip_lst.append(ext_ip)
    return ip_lst


def ip_loc_check(ip_f_check):
    ip_f_check = ipaddress.ip_address(ip_f_check)

    local_networks = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),
        ipaddress.ip_network('169.254.0.0/16'),
        ipaddress.ip_network('fc00::/7'),
        ipaddress.ip_network('fe80::/10'),
        ipaddress.ip_network('::1/128')
    ]

    for network in local_networks:
        if ip_f_check in network:
            return True
    return False


def ip_seprt(ip_type="all"):
    full_ip_lst = full_ip_list()
    if ip_type == "all":
        return full_ip_lst
    local_ip_lst = []
    extr_ip_lst = []
    for ip_addr in full_ip_lst:
        if ip_loc_check(ip_addr):
            local_ip_lst.append(ip_addr)
        else:
            extr_ip_lst.append(ip_addr)
    if ip_type == "local":
        return local_ip_lst
    if ip_type == "external":
        return extr_ip_lst


if __name__ == "__main__":
    full_ip_list = ip_seprt("external")
    print("IP Addresses:", full_ip_list)
