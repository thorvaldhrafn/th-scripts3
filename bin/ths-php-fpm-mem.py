import psutil
import re


def p_mem_rss_full(pname, p_mem_rss):
    global proc_mem_list
    try:
        p_mem_rss_old = proc_mem_list[pname]['rss']
        p_mem_rss_new = p_mem_rss_old + p_mem_rss
        proc_mem_list[pname]['rss'] = p_mem_rss_new
    except KeyError:
        rss_dict = dict(rss=p_mem_rss)
        try:
            p_dict = proc_mem_list[pname]
            p_dict = {**p_dict, **rss_dict}
            proc_mem_list[pname] = p_dict
        except KeyError:
            proc_mem_list[pname] = rss_dict

proc_mem_list = {}

for prinfo in psutil.process_iter():
    try:
        cmd_first = prinfo.cmdline()[0]
        if re.match('.*php-fpm: pool.+', cmd_first):
            p_data_list = []
            pool = cmd_first.split()[-1]
            p_mem_data = prinfo.memory_info()
            p_mem_rss = p_mem_data.rss
            p_mem_rss_full(pool, p_mem_rss)
    except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
        pass

for key in proc_mem_list.keys():
    print(key, proc_mem_list[key]['rss'])
