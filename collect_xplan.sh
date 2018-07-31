#!/usr/bin/env bash

base=$(dirname $0)
exec=${base}/lib/collect_xplan.py

ds_config=${base}/config
store_path=${base}/xplans

function main() {
    while read line; do
        db_name=$(echo $line | awk '{print $1}')
        inst=$(echo $line | awk '{print $2}')
        ds=$(echo $line | awk '{print $3}')
        lf=${base}/logs/${db_name}_${inst} #log file
        python $exec -dn $db_name -i $inst -ds $ds -sp $store_path >/dev/null 2>${lf} &
    done < $ds_config
}

while true; do
main
sleep 60
find ${store_path} -type f -ctime +10 -delete
done