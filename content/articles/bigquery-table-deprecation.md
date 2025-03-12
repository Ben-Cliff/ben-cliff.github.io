Title: Reclaiming Bigquery: A DWH Table Deprecation Strategy
Date: 2024-03-20
Category: Data Engineering
Tags: bigquery, data-warehouse, data-governance, data-lifecycle-management
Slug: bigquery-table-deprecation

# Reclaiming Bigquery: A DWH Table Deprecation Strategy

## Introduction

As data warehouses grow, so does the challenge of maintaining a clean and efficient environment. In this article, I'll share a structured approach I implemented to clean up a massive BigQuery data warehouse with hundreds of unused tables consuming over 565TB of storage. This project not only resulted in significant cost savings but also improved overall data governance and warehouse performance.



## The Challenge

Upon analyzing our data warehouse, I discovered several issues:

- Hundreds of tables with unknown or undocumented usage patterns
- Over 565TB of potentially unused data storage
- Unregulated IAM access creating security concerns
- No process to identify and safely deprecate unused tables
- Lack of transparency about which tables were still in active use

Our organization needed a systematic approach to identify unused tables, safely mark them for deprecation, and ultimately remove them while ensuring no critical business processes were disrupted.

## Summary of Approach

Our solution followed a structured, data-driven approach that leveraged BigQuery's metadata tables at each step:

1. **Inventory Collection**: Used `region-us.INFORMATION_SCHEMA.SCHEMATA` to identify all datasets, then queried `project-name.{dataset}.__TABLES__` for each dataset to collect table metadata including size and last modification dates.

2. **Usage Analysis**: Analyzed query patterns with `region-us.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION`, examining the `referenced_tables` field to determine which tables had been accessed in the past 3 months.

3. **Classification System**: Combined metadata from steps 1 and 2 into a custom analysis table that categorized tables based on usage patterns and business importance.

4. **Safe Deprecation**: Applied a "_to_be_archived" suffix to potentially unused tables, monitored for impacts, then deleted confirmed unused tables after a waiting period.

This approach enabled us to safely remove hundreds of unused tables while maintaining confidence that no critical business processes would be disrupted.

## The Solution: A Four-Phase Strategy

### Phase 1: Analytics and Discovery

The first step was a comprehensive analysis of our data warehouse to understand usage patterns and identify tables that could potentially be deprecated. I developed a Python script using the BigQuery API to gather metadata about all datasets and tables:

```python
from google.cloud import bigquery
import pandas as pd

# Initialize BigQuery client
client = bigquery.Client()

# Query to get all datasets
schemata_query = """
SELECT schema_name FROM region-us.INFORMATION_SCHEMA.SCHEMATA;
"""

# Query template to get table metadata for each dataset
dataset_tables_query = """
SELECT
    table_id,
    dataset_id,
    DATE(TIMESTAMP_MILLIS(last_modified_time)) AS last_modified_date,
    size_bytes / 1024 / 1024 / 1024 as size_gb,
    size_bytes / 1024 / 1024 / 1024 /1024 as size_tb
FROM `project-name.{dataset}.__TABLES__`;
"""

# Create DataFrame to store results
dwh_analysis_df = pd.DataFrame(columns=[
    'table_id', 'dataset_id', 'last_modified_date', 'size_gb', 'size_tb'
])

def fetch_schemata(schemata_query, client):
    query_job = client.query(schemata_query)
    return query_job.result()

def schemata_data_to_list(schemata_data):
    datasets = []
    for row in schemata_data:
        datasets.append(row[0])
    return datasets

def query_table_metadata(dataset_list, client, dataset_tables_query, analysis_df):
    for dataset in dataset_list:
        tables_query = dataset_tables_query.format(dataset=dataset)
        bq_df = client.query(tables_query).to_dataframe()
        print(f'Loading {dataset}')
        analysis_df = pd.concat([analysis_df, bq_df])
    return analysis_df.to_csv('output.csv', sep=',', index=False, encoding='utf-8')

# Main execution
schemata_data = fetch_schemata(schemata_query, client)
dataset_list = schemata_data_to_list(schemata_data)
query_table_metadata(dataset_list, client, dataset_tables_query, dwh_analysis_df)
```

I then uploaded this data to a dedicated analysis table in BigQuery for further processing and querying.

The next step was to identify which tables had recent activity and which were likely unused. For this, I created a SQL query that analyzed table access patterns using the `INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION` view:

```sql
CREATE OR REPLACE TABLE `project-name.analysis_dataset.table_activity` AS(
    SELECT
        dataset,
        COUNT(DISTINCT job_id) AS jobs_in_last_3_months,
        ARRAY_AGG(DISTINCT user_email) AS users_emails
    FROM (
        SELECT
            user_email,
            rt.dataset_id AS dataset,
            job_id
        FROM
            `project-name.region-us.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION`,
            UNNEST(referenced_tables) rt
        WHERE
            rt.project_id = 'project-name'
            AND creation_time >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH))
            AND rt.dataset_id NOT LIKE '%_script%'
    )
    GROUP BY 1
)
```

I combined this activity data with the table metadata to create a comprehensive view of our warehouse:

```sql
SELECT
    'project-name' AS project_id,
    COALESCE(ta.dataset, dwh.dataset_id) AS dataset_id,
    ta.jobs_in_last_3_months,
    CASE
        WHEN dataset_id IN ('data_monitoring','prod_analytics','ml','dimensions')
        THEN TRUE
        ELSE FALSE
    END AS should_have_activity,
    dataset_size_tb,
    STRUCT(
        dwh.tables AS tables,
        ta.users_emails AS users_emails
    ) AS dataset_struct
FROM
    dwh_analysis dwh
LEFT JOIN
    table_activity ta
ON
    ta.dataset = dwh.dataset_id
```

### Phase 2: Access Control and Documentation

The next phase involved removing unregulated IAM access to prevent unauthorized changes during the deprecation process. I also documented all known service level agreements (SLAs) and critical tables that needed to be preserved.

I created a classification system for tables:
- **Critical tables**: Known business-critical tables that should never be deprecated
- **Active tables**: Tables with recent query activity (within 90 days)
- **Inactive tables**: Tables with no recent activity and no documented purpose
- **Unknown tables**: Tables with no activity and no documentation

This classification helped establish a clear framework for the deprecation process.

### Phase 3: Safe Marking and Breaking Dependencies

For tables classified as inactive or unknown, I implemented a creative approach to safely identify any undocumented dependencies. Instead of immediately deleting these tables, I added a suffix "_to_be_archived" to their names, which would intentionally break any queries or processes still depending on them.

I created a Python script that would be executed through Airflow to automate this renaming process:

```python
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, NotFound

# Initialize BigQuery client
client = bigquery.Client()

# Query to identify tables for deprecation
query = """
SELECT
    project_id,
    dataset_id,
    table_id
FROM
    `project-name.analysis_dataset.warehouse_activity_analysis`
WHERE
    should_have_activity IS FALSE
    AND table_id NOT LIKE '%_to_be_archived%'
"""

def check_table_type(table_dict):
    """Check if the given table ID corresponds to a TABLE type."""
    table_ref = client.dataset(table_dict['dataset_id']).table(table_dict['table_id'])
    table = client.get_table(table_ref)
    return table.table_type

def add_archive_suffix(table_dict, suffix='_to_be_archived'):
    """Add suffix to table name to identify it for archiving."""
    if check_table_type(table_dict) == "TABLE":
        table_id = f"{table_dict['project_id']}.{table_dict['dataset_id']}.{table_dict['table_id']}"

        # Create SQL to rename the table
        alter_table_query = f"ALTER TABLE IF EXISTS {table_id} RENAME TO {table_dict['table_id']}{suffix}"

        try:
            query_job = client.query(alter_table_query)
            query_job.result()  # Wait for the query to complete
            print(f"Successfully renamed {table_id}")
            return True
        except BadRequest as e:
            print(f"Cannot rename table {table_id}: {e}")
            return False
        except NotFound as e:
            print(f"Table {table_id} not found: {e}")
            return False
    else:
        print(f"{table_dict['table_id']} is not a table, skipping")
        return False

# Main execution
datasets_df = client.query(query).to_dataframe()
table_list = datasets_df.to_dict(orient='records')

for table in table_list:
    add_archive_suffix(table)
```

This approach provided a safety net: if renaming a table broke a critical process, we could quickly identify and restore it. After deploying this change, we monitored for issues over a two-week period.

### Phase 4: Cleanup and Deletion

After confirming no critical processes were broken by the renamed tables, I created a final script to safely delete the marked tables:

```python
import time
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Initialize BigQuery client
client = bigquery.Client()

# Query to get datasets with marked tables
fetch_datasets_query = """
SELECT
    dataset_id
FROM
    `project-name.analysis_dataset.warehouse_activity_analysis`,
    UNNEST(dataset_struct.tables) as dst
WHERE
    should_have_activity IS FALSE
    AND table_id LIKE '%_to_be_archived%'
GROUP BY 1
"""

def dataset_exists(client, dataset_id):
    """Check if dataset exists."""
    try:
        dataset_ref = client.dataset(dataset_id)
        dataset = client.get_dataset(dataset_ref)
        tables = list(client.list_tables(dataset))
        return True
    except Exception:
        return False

def delete_dataset(client, dataset_id):
    """Delete dataset and all its contents."""
    dataset_id = 'project-name' + '.' + dataset_id
    client.delete_dataset(
        dataset_id,
        delete_contents=True,
        not_found_ok=False
    )
    print(f"Deleted dataset {dataset_id}")

# Main execution
dataset_ids_list = client.query(fetch_datasets_query).to_dataframe()['dataset_id'].tolist()

for dataset in dataset_ids_list:
    if dataset_exists(client, dataset):
        # For safety, require manual confirmation before deletion
        user_input = input(f'Do you want to delete the dataset {dataset}? (Y/n): ')
        if user_input.lower() == "y" or not user_input.strip():
            print(f'Deleting {dataset}')
            delete_dataset(client, dataset)
        else:
            print(f'Skipping {dataset}')

print('All marked datasets have been processed')
```

## Results and Impact

This structured approach to table deprecation delivered significant benefits:

1. **Storage Optimization**: Successfully identified and removed 565TB of unused data, resulting in substantial cost savings.

2. **Improved Security**: Removed unregulated IAM access, strengthening our data warehouse security posture.

3. **Enhanced Data Governance**: Created a comprehensive inventory of all datasets and tables with their usage patterns.

4. **Reduced Complexity**: Eliminated confusion about which tables were current and actively used.

5. **Better Performance**: Reduced overall warehouse size improved query performance across the system.

6. **Transparent Process**: The gradual approach with clear communication ensured no business disruption.

## Key Lessons

Several important lessons emerged from this project:

1. **Analysis before action**: A thorough understanding of table usage patterns is essential before any deprecation.

2. **Break connections safely**: Renaming tables before deletion provides a critical safety mechanism.

3. **Automation is key**: Scripts and workflows make the process repeatable and less error-prone.

4. **Communication matters**: Keeping stakeholders informed throughout the process ensures alignment.

5. **Documentation is crucial**: Maintaining clear documentation of what was removed and why helps with future governance.

## Conclusion

Table deprecation in BigQuery doesn't have to be risky or disruptive. By following a methodical approach—analyzing usage, communicating with stakeholders, safely marking tables, and only then performing deletion—you can confidently clean up your data warehouse, reduce costs, and improve overall system performance.

This framework can be adapted to any BigQuery environment, regardless of size, and provides a template for ongoing data lifecycle management rather than just a one-time cleanup.
