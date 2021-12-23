# yc_pgbackup

This short script helps you to backup databases from Yandex Managed Service for PostgreSQL on Yandex.Cloud platform to Yandex.Disk.

### Requirements
 - python 3.6+
 - active account on Yandex.Cloud with at least one enabled PostgreSQL cluster
 - active account on Yandex.Disk

No any additional python packages needed, so you don't need create virtual environments.

### Installation

1. install [CLI for Yandex.Cloud](https://cloud.yandex.com/en/docs/cli/operations/install-cli)
2. install [Yandex.Disk for linux](https://yandex.com/support/disk-desktop-linux/)
3. rename example credentials file from `.yc_pg_credentials_example` to `.yc_pg_credentials` and fill your credentials data
4. rename example config file from `config.cfg_example` to `config.cfg` and fill it according example
5. run `backup.py` script like `python3 backup.py`, check if it works fine
6. add to cron like this:
```
# run every day at 3:41 AM
41 3 * * * /usr/bin/python3 /home/username/yc_pgbackup/backup.py >> ~/backup.log 2>&1
```

### Config script

Config file and credentials file are JSON files, so don't forget to follow the JSON format.

You can exclude certain databases from backup proccedure, just enter value for key `exclude_dbs` in config file. It is a list type, so you can enter any count of databases you need. If you wish to backup all databases, just leave this list blank like this: `[]`.


### Some notes with Yandex PostgreSQL Cluster

Due to impossibility access to PostgreSQL cluster with `postgres` user you should place plain text credentials in file `.yc_pg_credentials`. There is no other way to access to databases. And unfortunally Yandex Managed Service for PostgreSQL does not provide any user permissions, for example just readonly user suitable for backup proccedure.

User - database relationship defined automatically, so you don't need to modify credentials file when add or delete database at the psql cluster. Only if new user with associated new database was added.


### Yandex.Disk Clean Trash issue

Using Ya.Disk you can't delete files permanently, it goes to trash first and also take up space in your Disk. Along with this Yandex [deny working over API when no free space on the Disk](https://yandex.com/support/disk/enlarge/disk-space.html#no-more-space). So, you might face this situation: after delete old backup files you can't clean trash via API because Disk are full. To prevent it we should clean trash after deleting every old backup file instead of delete all files in one command like `rm *.sql.gz`