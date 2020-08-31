#!/bin/bash

process=`ps aux | grep -E '*php-fpm' | awk '{print $6}' | wc -l`
all_mem=0
avrg_mem=0

for i in `ps aux | grep -E '*php-fpm' | awk '{print $6}'`
        do
                let "all_mem=$all_mem + $i"
        done
let "avrg_mem=$all_mem / $process"
echo ${process} ${all_mem} ${avrg_mem}

exit 0
