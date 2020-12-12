import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries

## This function loops through the drop table queries and makes sure we start clean
def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()

## This function loops through the create table queries to create all the tables needed
def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()

## This function connects to the DB using the info from dwh.cfg, drops existing tables, and creates new tables
def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()