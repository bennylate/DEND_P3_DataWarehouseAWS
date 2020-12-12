import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries

## This function loops through the staging table queries and copies data from the S3 source 
def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()

## This function loops through the insert statements to populate the facts/dimension tables from the staging tables
def insert_tables(cur, conn):
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()

## This function connects to the DB using the info from dwh.cfg and grabs data from the S3 source for the staging tables.
def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()