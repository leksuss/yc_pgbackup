# yc_pgbackup

This short script helps you to backup databases from Yandex Managed Service for PostgreSQL on Yandex.Cloud platform to Yandex.Disk (or any other destination you want).

### Requirements
 - python 3.6+
 - active account on Yandex.Cloud with at least one enabled PostgreSQL cluster
 - active account on Yandex.Disk (optionally)


### Installation

1. install CLI for [Yandex.Cloud](https://cloud.yandex.com/en/docs/cli/operations/install-cli)
2. install [Yandex.Disk for linux](https://yandex.com/support/disk-desktop-linux/)
3. rename example credentials file from `.yc_pg_credentials_example` to `.yc_pg_credentials` and fill your credentials data
4. run `backup.py` script like `python3 backup.py`


### Some notes

Due to impossibility access to PostgreSQL cluster with `postgres` user you should place plain text credentials in file `.yc_pg_credentials`. There is no other way to access to databases. And unfortunally Yandex Managed Service for PostgreSQL does not provide any user permissions, for example just readonly user suitable for backup proccedure.

User - database relationship defined automatically, so you don't need to modify credentials file when add or delete database at the psql cluster. Only if new user with associated new database was added.

No any additional python packages needed, so you don't need create virtual environments.