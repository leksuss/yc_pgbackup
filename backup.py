import datetime
import json
import subprocess
import os
import requests
import time

from pathlib import Path


my_env = os.environ.copy()
my_env['PATH'] += f":{my_env['HOME']}/yandex-cloud/bin"
path = str(Path(__file__).parent.absolute())


def read_credentials(path=path):
    with open(path + '/.yc_pg_credentials', 'r') as f:
        creds = json.load(f)
    return creds


def read_config(path=path):
    with open(path + '/config.cfg', 'r') as f:
        config = json.load(f)
    return config


def sh(cmd, input='', env=my_env, shell=False):
    rst = subprocess.run(
        cmd,
        env=env,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input.encode("utf-8"),
    )
    assert rst.returncode == 0, rst.stderr.decode("utf-8")
    return rst.stdout.decode("utf-8").strip()


def time_stamp():
    return str(datetime.datetime.now().replace(microsecond=0))


def tprint(*printed_val):
    print(time_stamp(), end=' ')
    print(*printed_val)


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


def clean_trash(token):
    headers = {
        "Accept": "application/json",
        'Authorization': 'OAuth ' + token
    }

    url = 'https://cloud-api.yandex.net/v1/disk/trash/resources'
    r = requests.delete(url=url, headers=headers)


creds = read_credentials()
config = read_config()

# remove old backup files
old_backup_files = os.listdir(config['backup_path'])
for file in old_backup_files:
    cmd = f"rm -f {config['backup_path']}/{file}"
    tprint("Deleting", file)
    sh(cmd, shell=True)
    time.sleep(5)
    tprint("Clean trash from file", file)
    clean_trash(creds['ya_disk_token'])


hostname = cluster_hostname(creds['cluster_id'])

for db in get_pg_databases(creds['cluster_id']):

    if db['name'] in config['exclude_dbs']:
        continue

    dt = datetime.datetime.now()
    date = dt.strftime("%Y-%m-%d_%H:%M")
    filename_path = f"{config['backup_path']}/{db['name']}_{date}.sql"

    cmd = [
        'pg_dump',
        '-h', hostname,
        '-p', '6432',
        '-U', db['owner'],
        '-f', filename_path,
        db['name']
    ]

    my_env['PGPASSWORD'] = creds['users'][db['owner']]

    tprint(f"Dumping DB {db['name']} ...")
    try:
        sh(cmd, env=my_env)
        tprint(f"DB {db['name']} dumped to file {filename_path}")
    except AssertionError as e:
        tprint(e)
        tprint(f"Backing up DB {db['name']} failed")

    tprint(f"Compress dumped DB {db['name']}...")
    filename_path_gz = f"{filename_path}.tar.gz"
    sh([
        "tar",
        "--remove-files",
        "-czf",
        filename_path_gz,
        filename_path
    ])
    tprint(f"DB {db['name']} file compressed to {filename_path_gz}")
