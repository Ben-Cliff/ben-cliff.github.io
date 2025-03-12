Title: Mixpanel Incremental Processing: Conquering Extreme Data Volumes and Duplicate Events
Date: 2024-08-07
Category: Data Engineering
Tags: dbt, bigquery, analytics, incremental-loading, Mixpanel, event-tracking
Slug: mixpanel-incremental-loading

# Mixpanel Incremental Processing: Conquering Extreme Data Volumes and Duplicate Events

## Situation

Our Mixpanel implementation had reached an extreme scale, generating a massive volume of event data that made traditional processing methods completely unsustainable. Several critical challenges had emerged:

1. **The dataset had grown to an unmanageable size, with a year of historical data exceeding several terabytes**
2. **Recreating the entire table daily was causing processing times to exceed 8 hours, making daily refreshes impossible**
3. Mixpanel was consistently sending duplicate events (affecting approximately 0.11% of all events), making incremental processing impossible without deduplication
4. Historical data needed to be backfilled while ensuring data consistency
5. Reporting systems required timely data without the latency of full-refresh processing
6. **Computing costs had escalated dramatically, with daily processing consuming over 250 slot-hours**

These issues were affecting both the reliability of our analytics and the cost-effectiveness of our data infrastructure.

## Task

I needed to implement a robust incremental processing system for Mixpanel data that would:

1. **Handle the extreme data volume by processing only new data instead of the entire dataset**
2. **Reliably deduplicate Mixpanel events to make incremental processing possible**
3. Create a reliable historical baseline through proper backfilling of terabytes of historical data
4. Ensure data consistency and accuracy for reporting despite duplicate events
5. **Dramatically reduce processing time from 8+ hours to under 30 minutes**
6. **Reduce computing costs by at least 75% without compromising data quality**
7. Create a sustainable pattern that could scale with future data growth

## Action

I developed a comprehensive solution leveraging DBT's incremental processing and BigQuery's advanced features.

### 1. Duplicate Event Detection and Handling for Incremental Processing

For incremental processing to work correctly, duplicate records must be eliminated. I discovered that Mixpanel was sending duplicate events (approximately 0.11% of all data), which would break the incremental merge operations if not addressed. I implemented a robust deduplication system in the staging layer:

```sql
{{
  config(
    materialized='table',
    partition_by={
      "field": "partition_date",
      "data_type": "date"
    }
  )
}}

SELECT
  *,
  ROW_NUMBER() OVER (
    PARTITION BY mp_insert_id, time
    ORDER BY mp_insert_id
  ) AS row_num
FROM {{ source('mixpanel', 'mp_master_event') }}
```

This approach:
- Identifies duplicates using Mixpanel's native `mp_insert_id` and event timestamp
- Assigns a row number to each event, keeping only the first occurrence (`row_num = 1`)
- Creates a clean foundation for incremental processing by ensuring unique records
- Preserves rejected duplicates in a separate table for monitoring and analysis

### 2. Incremental Loading Implementation

I implemented an efficient incremental loading pattern in DBT:

```sql
{{
  config(
    materialized='incremental',
    unique_key=['mp_insert_id', 'time'],
    partition_by={
      "field": "partition_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=['customer_id', 'mp_insert_id'],
    incremental_strategy='merge',
    merge_update_columns=['all']
  )
}}

WITH source_data AS (
  SELECT * FROM {{ ref('stg_mp_dedup_events') }}
  WHERE row_num = 1  -- Only take first occurrence of any duplicate
)

SELECT * FROM source_data
{% if is_incremental() %}
  WHERE partition_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
  AND NOT EXISTS (
    SELECT 1 FROM {{ this }} t
    WHERE t.mp_insert_id = source_data.mp_insert_id
    AND t.time = source_data.time
  )
{% endif %}
```

This pattern:
- Only processes events from the last three days to catch late-arriving data
- Uses a compound key (`mp_insert_id` and `time`) to precisely identify duplicate events
- Leverages BigQuery's merge capabilities for efficient updates
- Optimizes query performance with partitioning and clustering

### 3. Historical Data Backfill

For the initial backfill of historical data, I created a specialized Python script that could process the entire dataset chronologically while maintaining incremental processing principles:

```python
def process_partition_date(partition_date):
    partition_date_str = partition_date.strftime('%Y-%m-%d')

    # Construct the query to insert deduplicated data
    query = f"""
    INSERT INTO `target_table`
    SELECT t.*
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY mp_insert_id, time ORDER BY mp_insert_id) AS rn
        FROM `source_table`
        WHERE DATE(_PARTITIONTIME) = '{partition_date_str}'
    ) t
    LEFT JOIN `processed_keys_table` pk
        ON t.mp_insert_id = pk.mp_insert_id AND t.time = pk.time
    WHERE t.rn = 1 AND pk.mp_insert_id IS NULL
    """

    # Run the query
    query_job = client.query(query)
    query_job.result()

    # Update processed keys to avoid reprocessing
    update_keys_query = f"""
    INSERT INTO `processed_keys_table` (mp_insert_id, time)
    SELECT DISTINCT mp_insert_id, time
    FROM `source_table`
    WHERE DATE(_PARTITIONTIME) = '{partition_date_str}'
    """
    update_keys_job = client.query(update_keys_query)
    update_keys_job.result()
```

This script:
- Processed one day at a time, allowing for manageable chunks
- Tracked which records had been processed using a separate tracking table
- Applied the same deduplication logic used in the ongoing incremental processing
- Ensured data consistency between historical and new data

### 4. Rejected Event Tracking

To monitor data quality, I implemented a system to track rejected events:

```sql
CREATE OR REPLACE TABLE `mp_rejected_events` AS
SELECT
  t.*,
  'Duplicate event' AS rejection_reason,
  CURRENT_TIMESTAMP() AS rejection_timestamp
FROM {{ source('mixpanel', 'mp_master_event') }} t
INNER JOIN {{ ref('stg_mp_dedup_events') }} d
  ON t.mp_insert_id = d.mp_insert_id
  AND t.time = d.time
WHERE d.row_num > 1
```

This approach:
- Captured all rejected duplicate events
- Provided visibility into the duplication rate (approximately 0.11%)
- Created an audit trail for data quality monitoring

## Results

The implementation delivered substantial improvements:

1. **Extreme volume handling**: Successfully processed and maintained multiple terabytes of event data without performance degradation

2. **Processing efficiency**: Processing time decreased from over 8 hours to approximately 15 minutes per day by only handling new data

3. **Cost reduction**: Computing costs decreased by 92% (from 250+ slot-hours to just 20 slot-hours daily) due to the reduced processing volume

4. **Data accuracy**: Eliminated all duplicate events through reliable deduplication, improving the accuracy of downstream analytics

5. **Historical data consistency**: Successfully backfilled over a year of historical data while maintaining data integrity

6. **Query performance**: Partitioning and clustering reduced query times by 65% for common analytical queries

7. **Scalable foundation**: Created a system that can handle 10x growth without significant changes to the architecture

This solution has created a robust, efficient pipeline for Mixpanel data that delivers high-quality data to our analytics systems while minimizing processing costs and time, even as data volumes continue to grow.
