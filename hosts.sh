#!/usr/bin/env bash

# add local  hostnames for easy access to local services

grep -q 'ds-zeepelin' /etc/hosts || \
    echo 'ds-zeepelin 172.30.10.100' | sudo tee -a /etc/hosts > /dev/null
grep -q 'spark-master' /etc/hosts || \
    echo 'spark-master 172.30.10.101' | sudo tee -a /etc/hosts > /dev/null
grep -q 'spark-worker' /etc/hosts || \
    echo 'spark-worker 172.30.10.102' | sudo tee -a /etc/hosts > /dev/null
grep -q 'ds-hive' /etc/hosts || \
    echo 'ds-hive 172.30.10.103' | sudo tee -a /etc/hosts > /dev/null
grep -q 'ds-livy' /etc/hosts || \
    echo 'ds-livy 172.30.10.104' | sudo tee -a /etc/hosts > /dev/null
grep -q 'ds-postgres' /etc/hosts || \
    echo 'ds-postgres 172.30.10.105' | sudo tee -a /etc/hosts > /dev/null
