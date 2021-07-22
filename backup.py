import subprocess
import datetime
import json
import os
from pathlib import Path


my_env = os.environ.copy()
path = str(Path(__file__).parent.absolute())


def read_credentials(path=path):
    with open(path + '/.yc_pg_credentials', 'r') as f:
        creds = json.load(f)
    return creds


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


creds = read_credentials()
hostname = cluster_hostname(creds['cluster_id'])

# remove old backup files
cmd = f"rm -rf {creds['backup_path']}/*.sql.tar.gz"
sh(cmd, shell=True)

for db in get_pg_databases(creds['cluster_id']):

    if db['name'] != 'db1':
        continue
    dt = datetime.datetime.now()
    date = dt.strftime("%Y-%m-%d_%H:%M")
    filename_path = f"{creds['backup_path']}/{db['name']}_{date}.sql"

    cmd = [
        'pg_dump',
        '-h', hostname,
        '-p', '6432',
        '-U', db['owner'],
        '-f', filename_path,
        db['name']
    ]

    my_env['PGPASSWORD'] = creds['users'][db['owner']]

    print(f"Dumping DB {db['name']} ...")
    try:
        sh(cmd, env=my_env)
        print(f"DB {db['name']} dumped to file {filename_path}")
    except AssertionError as e:
        print(e)
        print(f"Backing up DB {db['name']} failed")

    print(f"Compress dumped DB {db['name']}...")
    filename_path_gz = f"{filename_path}.tar.gz"
    sh([
        "tar",
        "--remove-files",
        "-czf",
        filename_path_gz,
        filename_path
    ])
    print(f"DB {db['name']} file compressed to {filename_path_gz}")
