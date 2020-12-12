### Udacity Project - Data Warehouse/AWS
#### Purpose
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

To support the business, we need to build an ETL pipeline that extracts the data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for the analytics team so they may find insights into what songs their users are listening to. 

### Warehouse Schema
#### Staging Tables
These tables will be used to as a stopover from the S3 source files so we can pull data into our Facts/Dimension tables.

#### Events Table
>artist varchar
>auth varchar
>firstName varchar
>gender varchar
>itemInSession int
>lastName varchar
>length float
>level varchar
>location varchar
>method varchar
>page varchar
>registration int
>sessionId int
>song varchar
>status int
>ts timestamp
>userAgent varchar
>user_id varchar

#### Songs Table
>artist_id varchar
>artist_location varchar
>artist_latitude float
>artist_longitude float
>artist_name varchar
>duration float
>num_songs int
>song_id varchar
>title varchar
>year int

#### Facts Table - Songplays
Assuming normal business use, I expect the songplays table to grow over time.  I would have chosen EVEN distribution but all the queries will be using dimension data against this table and likely will lead to lackluster query performance.  Given that, I've chosen a KEY distribution to help align those keys and reducing the shuffling needed to respond to queries.  

>songplay_id int PRIMARY KEY
>start_time TIMESTAMP SORTKEY
>user_id varchar NOT NULL  (foreign key to users table)
>level varchar
>song_id varchar DISTKEY (foreign key to songs table)
>artist_id varchar (foreign key to artists table)
>session_id int SORTKEY
>location varchar
>user_agent varchar

#### Dimensions Tables
#### Users
An ALL distribution would be good here as I expect the table won't grow at the same proportion as songplays, and copying this across slices would be help make queries a bit quicker.  However, I chose to use AUTO here.  The description of AUTO in the demo makes it seem to be the best option for novice's like me or where you're not sure the table really needs a specific distribution type.

>user_id varchar PRIMARY KEY
>first_name varchar
>last_name varchar
>gender varchar
>level varchar

#### Songs
I'm using a KEY distribution here because I used song_id as a distribution KEY so I wanted to match.

>song_id varchar PRIMARY KEY DISTKEY
>title varchar
>artist_id varchar NOT NULL (foreign key to artists table)
>year int SORTKEY
>duration float

#### Artists
I doubt this will grow at a significant pace given the limited number of songs produced each year.  I would set everything to AUTO typically, but here I want to try the ALL distribution just for variety.

>artist_id varchar PRIMARY KEY
>name varchar
>location varchar
>latitude float
>longitude float

#### Time
I get the inclination that this wouldn't be in the majority of queries, but I may be wrong.  I'll set to AUTO distribution.  Cites for timestamp source to figure out how to manage the time stamp and keep milliseconds.
>https://stackoverflow.com/questions/54637697/redshift-timestamp-conversion-that-retains millisecond-percision
>https://www.fernandomc.com/posts/redshift-epochs-and-timestamps/

>start_time TIMESTAMP PRIMARY KEY
>hour int
>day int
>week int
>month int
>year int
>weekday int

### ETL Pipeline
The ETL pipeline will use code to access the JSON source files from S3 and then populate our Facts/Dimenson tables to allow queries and data pulls which support analysis.