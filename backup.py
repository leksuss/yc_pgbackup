from os import walk
from random import choice
import subprocess
import time
import json
import os


def sh(cmd, input="", env=my_env):
    rst = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input.encode("utf-8"),
        env=my_env
    )
    assert rst.returncode == 0, rst.stderr.decode("utf-8")
    return rst.stdout.decode("utf-8").strip()


def cluster_hostname(cluster_id):
    cmd = [
        'yc',
        'postgres',
        'hosts',
        '--format=json',
        f'--cluster-id={cluster_id}',
        'list'
    ]
    return json.loads(sh(cmd))[0]['name']


def get_pg_databases(cluster_id):
    cmd = [
        'yc',
        'postgres',
        'database',
        '--format=json',
        f'--cluster-id={cluster_id}',
        'list'
    ]
    return json.loads(sh(cmd))


hostname = cluster_hostname(cluster_id)


for db in get_pg_databases(cluster_id):
    cmd = [
        'pg_dump',
        '-h', hostname,
        '-p', '6432',
        '-U', db['owner'],
        db['name'], '>', db['name'] + '.sql'
    ]
    sh(cmd)
    # print(cmd)
