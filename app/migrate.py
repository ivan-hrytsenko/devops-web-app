#!/usr/bin/env python3
import argparse
import sys
import db

parser = argparse.ArgumentParser()
parser.add_argument('--db-host', default='127.0.0.1')
parser.add_argument('--db-port', type=int, default=3306)
parser.add_argument('--db-user', required=True)
parser.add_argument('--db-password', required=True)
parser.add_argument('--db-name', required=True)
args = parser.parse_args()

try:
    conn = db.get_connection(
        args.db_host, args.db_port,
        args.db_user, args.db_password, args.db_name
    )
    db.run_migration(conn)
    conn.close()
    print('Migration completed successfully')
except Exception as e:
    print(f'Migration failed: {e}', file=sys.stderr)
    sys.exit(1)