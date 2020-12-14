import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = " DROP TABLE IF EXISTS times;"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE IF NOT EXISTS staging_events(
        artist varchar(max),
        auth varchar(255),
        first_name varchar(255),
        gender varchar(255),
        itemInSession int,
        last_name varchar(255),
        length float,
        level varchar(255),
        location text,
        method varchar(255),
        page varchar(255),
        registration bigint,
        sessionId int,
        song varchar(255),
        status int,
        ts bigint,
        userAgent varchar(255),
        user_id varchar(255)
    );
""")

staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs(
        artist_id varchar(255),
        artist_location varchar(MAX),
        artist_latitude float,
        artist_longitude float,
        artist_name varchar(max),
        duration float,
        num_songs int,
        song_id text,
        title text,
        year int
    );
""")

## To try and reduce query execution time due to shuffling, I've sorted by the user play session and I'm using the song_id to distribute across slices

## Using Redshift AUTO distribution 
user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users(
        user_id varchar(255) PRIMARY KEY,
        first_name varchar,
        last_name varchar,
        gender varchar,
        level varchar
    )
    DISTSTYLE AUTO;
    
""")

## To be consistent, I'm using song_id here to distribute the songs.  I'm sorting by year to help keep albums together
song_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs(
        song_id varchar(255) PRIMARY KEY,
        title text,
        artist_id varchar(255) NOT NULL,
        year int,
        duration float
    )
    DISTSTYLE KEY
    DISTKEY (song_id)
    SORTKEY (year);
    
""")

artist_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists(
        artist_id varchar(255) PRIMARY KEY,
        name varchar(255),
        location text,
        latitude float,
        longitude float
    )
    DISTSTYLE ALL;
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS times(
        state_time timestamp PRIMARY KEY,
        hour int,
        day int,
        week int,
        month int,
        year int,
        weekday int
    )
    DISTSTYLE AUTO;
""")

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays(
        songplay_id int IDENTITY(0,1) PRIMARY KEY,
        start_time timestamp NOT NULL,
        user_id varchar(255) NOT NULL,
        level varchar(255),
        song_id varchar(255) NOT NULL,
        artist_id varchar(255) NOT NULL,
        session_id int,
        location text,
        user_agent varchar(255)
    )
    DISTSTYLE KEY
    DISTKEY (song_id)
    SORTKEY (start_time, session_id);

""")


# COPY TO STAGING TABLES

staging_events_copy = ("""
    DELETE FROM staging_events;
    COPY staging_events(
        artist,
        auth,
        first_name,
        gender,
        itemInSession,
        last_name,
        length,
        level,
        location,
        method,
        page,
        registration,
        sessionId,
        song,
        status,
        ts,
        userAgent,
        user_id
    )
    FROM {}
    FORMAT JSON AS {}
    iam_role '{}'
""").format(
    config.get ('S3', 'LOG_DATA'),
    config.get ('S3', 'LOG_JSONPATH'),
    config.get ('IAM_ROLE', 'ARN')
    )

staging_songs_copy = ("""
    DELETE FROM staging_songs;
    COPY staging_songs(
        artist_id,
        artist_location,
        artist_latitude,
        artist_longitude,
        artist_name, 
        duration,
        song_id,
        title,
        year
    )
    FROM {}
    FORMAT JSON AS 'auto'
    iam_role '{}'
""").format(
    config.get ('S3', 'SONG_DATA'),
    config.get ('IAM_ROLE', 'ARN')
    )

# FINAL TABLES

user_table_insert = ("""
    INSERT INTO users(user_id, first_name, last_name, gender, level)
    SELECT DISTINCT user_id, first_name, last_name, gender, level
    FROM staging_events
    WHERE page = 'NextSong'
    
""")

song_table_insert = ("""
    INSERT INTO songs(song_id, title, artist_id, year, duration)
    SELECT song_id, title, artist_id, year, duration 
    FROM staging_songs
    
""")

artist_table_insert = ("""
    INSERT INTO artists(artist_id, name, location, latitude, longitude)
    SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
    FROM staging_songs
    
""")

time_table_insert = ("""
    INSERT INTO times(start_time, hour, day, week, month, year, weekday)
    SELECT DISTINCT TIMESTAMP 'epoch' + staging_events.ts/1000 *INTERVAL '1 second' as start_time,
        extract(hour from start_time) as hour, 
        extract(day from start_time) as day,
        extract(week from start_time) as week,
        extract(month from start_time) as month,
        extract(year from start_time) as year,
        extract(weekday from start_time) as weekday
   FROM staging_events
""")

songplay_table_insert = ("""
    INSERT INTO songplays(
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent
        user_id,
        level,
        songs.song_id as song_id,
        artists.artist_id as artist_id,
        sessionId as session_id,
        staging_events.location as location,
        userAgent as user_agent
    FROM staging_events
    INNER JOIN artists on artists.name = staging_events.artist
    INNER JOIN songs on songs.title = staging_events.song
    WHERE page = 'NextSong'

""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [user_table_insert, song_table_insert, artist_table_insert, time_table_insert, songplay_table_insert]

