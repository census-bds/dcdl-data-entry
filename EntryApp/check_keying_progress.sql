--  ############################
-- QUERIES FOR THE DATABASE
--  ############################

-- number of reels per year
SELECT year, COUNT(*) AS reel_count 
    FROM "EntryApp_reel" 
    GROUP BY year;

-- number in progress by year 
SELECT year, COUNT(*) AS in_progress 
    FROM "EntryApp_reel" 
    WHERE keyer_count > 0 
        AND (NOT is_complete_keyer_one OR NOT is_complete_keyer_two)
    GROUP BY year;

-- number of completed reels by year 
SELECT year, COUNT(*) AS done 
    FROM "EntryApp_reel" 
    WHERE is_complete_keyer_one AND is_complete_keyer_two
    GROUP BY year;



-- IMAGES 

-- images completed per keyer per year
SELECT jbid, COUNT(*) as completed_images
    FROM "EntryApp_image"
    WHERE is_complete=True
    GROUP BY jbid
    ORDER BY completed_images DESC;


-- images completed per keyer per year
SELECT jbid, year, COUNT(*) as completed_images
    FROM "EntryApp_image"
    WHERE is_complete=True
    GROUP BY jbid, year
    ORDER BY year, completed_images DESC;


-- this is like... how long to get this far in the reel, by keyer and year
WITH timediff AS (
    SELECT year, jbid, (last_modified - create_date) AS delta 
    FROM "EntryApp_image"
    WHERE is_complete
    )
SELECT year, jbid, 
     COUNT(*) AS completed_images,
     AVG(delta) AS avg_complete_time
    FROM timediff
    GROUP BY jbid, year
    ORDER BY year, avg_complete_time DESC;




-- RECORD

-- average number of people per sheet
WITH person_count AS (
        SELECT COUNT(*) as person_ct
        FROM "EntryApp_record"
        GROUP BY sheet_id
    )
SELECT AVG(person_ct)
    FROM person_count;

-- average number of people per sheet by year
WITH person_count AS (
    SELECT * FROM
        (SELECT sheet_id, COUNT(*) as person_ct 
        FROM "EntryApp_record" 
        GROUP BY sheet_id) AS a
        LEFT JOIN
        (SELECT id, year 
        FROM "EntryApp_sheet") AS b
        ON a.sheet_id=b.id
    )
SELECT year, AVG(person_ct) as avg_person_ct
    FROM person_count
    GROUP BY year
    ORDER BY year;

-- how long is average time from first record entry to last on a sheet?
WITH timediff AS (
        SELECT id, create_date, sheet_id, col_no,
        create_date - LAG(create_date, 1) 
            OVER (PARTITION BY sheet_id ORDER BY sheet_id, id) AS delta
        FROM "EntryApp_record"
    ),completion_time AS (
        SELECT sheet_id, 
        COUNT(*) AS num_records,
        SUM(delta) AS completion_time
        FROM timediff
        WHERE delta < INTERVAL '1 hour'
        GROUP BY sheet_id
    )
SELECT AVG(completion_time) AS avg,
    AVG(completion_time / num_records) AS avg_per_record
    FROM completion_time;


-- how long is average time from first record entry to last on a sheet?
WITH timediff AS (
        SELECT id, create_date, sheet_id, col_no,
        create_date - LAG(create_date, 1) 
            OVER (PARTITION BY sheet_id ORDER BY sheet_id, id) AS delta
        FROM "EntryApp_record"
    ),completion_time AS (
        SELECT sheet_id, 
        COUNT(*) AS num_records,
        SUM(delta) AS completion_time
        FROM timediff
        WHERE delta < INTERVAL '1 hour'
        GROUP BY sheet_id
    )
SELECT AVG(completion_time) AS avg,
    AVG(completion_time / num_records) AS avg_per_record
    FROM completion_time;