Title: Safe BigQuery Insert Migration
Date: 2025-03-13
Category: data engineering
Tags: bigquery, data-warehouse, data-governance, data-lifecycle-management
Slug: safe-bq-insert-migration


Quick reminder document on how we used to migrate event stream data between BigQuery datasets while ensuring:
- No duplicates were created
- No data was lost
- Each table's unique schema was respected

## Migration Process

We migrated three event types from source tables to their destination counterparts:

1. Design Creation Events
2. Design View Events
3. User Action Events

## Checking Table Schemas

Before migration, we compared the table schemas to understand field mappings:

```bash
# View full table information including schema
bq show --format=prettyjson project_name:source_dataset.source_table
bq show --format=prettyjson project_name:destination_dataset.destination_table
```

## Handling Schema Differences

We discovered significant schema differences between source and destination:
- Source tables had simpler schemas with fewer fields
- Destination tables included nested fields and additional tracking columns
- Destination tables used clustering and partitioning for performance

## Migration Queries

For each table pair, we crafted SQL queries that:
1. Selected only matching fields from source
2. Used partition filters to comply with table requirements
3. Implemented deduplication logic

### Example Migration Query

```sql
INSERT INTO `project_name.destination_dataset.event_table`
(user_id, event_id, workspace_id, team_id, published_at)
SELECT
  user_id,
  event_id,
  workspace_id,
  team_id,
  published_at
FROM `project_name.source_dataset.event_table_copy` source
WHERE NOT EXISTS (
  SELECT 1
  FROM `project_name.destination_dataset.event_table` dest
  WHERE
    dest.event_id = source.event_id
    AND dest.published_at = source.published_at
    AND dest.published_at BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND CURRENT_TIMESTAMP()
)
AND source.published_at BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND CURRENT_TIMESTAMP()
```

## Key Insights

1. **Partition Filters**: All queries required explicit time filters due to partition requirements
2. **Deduplication**: We used `NOT EXISTS` clauses to prevent duplicates
3. **Schema Compatibility**: Fields present in destination but not in source remained NULL
4. **Time Scoping**: Limited initial migration to last 90 days of data for manageability

## Next Steps

- Validate data accuracy with sample queries
- Extend migration to older data using appropriate time ranges
- Monitor destination table growth and query performance

This pattern can be adapted for similar migrations between tables with differing schemas while maintaining data integrity.
