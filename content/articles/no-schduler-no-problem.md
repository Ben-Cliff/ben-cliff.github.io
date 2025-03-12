Title: No Scheduler No Problem (kindof)
Date: 2024-03-20
Category: Data Engineering
Tags: cloud-engineering, aws, lambda, eventbridge, python
Slug: no-scheduler-no-problem

# Improvising a Cloud Solution: no schduler no problem (kindof)

## The Challenge

When I joined the data team within one of my previous roles, we faced a significant operational hurdle: we had no dedicated scheduler or orchestration tool for our Python-based data pipelines. This limitation became particularly problematic when we needed to regularly collect and analyze social media metrics from influencer partnerships across Instagram, TikTok, and YouTube.

Our partnerships team was manually tracking post performance, which was time-consuming and error-prone. The business needed reliable metrics to measure campaign ROI, but we lacked the proper infrastructure to automate this process. Most frustratingly, we couldn't use traditional workflow orchestration tools due to organizational constraints and approval timelines.

We needed a solution—and we needed it quickly, even if it meant building something that wasn't architecturally perfect.

_I've added some thoughts on this experience [here]({static}/articles/onboarding-reflection.md) as an indication of how onboardings can tell a lot about a tech stack and culture_

## The Approach

Given the constraints, I decided to create a "hack" solution using tools I could access immediately without lengthy approval processes. Instead of waiting for proper infrastructure, I improvised with available services to get the job done:

1. **Repurposing Serverless Functions**: I leveraged AWS Lambda as a makeshift scheduler, despite it not being designed for this purpose. While not ideal, Lambda offered a way to execute code on a schedule without requiring dedicated servers or orchestration tools.

2. **Workaround for Time Limitations**: Lambda's 15-minute execution timeout posed a significant challenge for our scraping needs. I addressed this by implementing a batch processing system that would process chunks of data within the time constraint, effectively breaking a larger job into manageable pieces.

3. **EventBridge as an Improvised Scheduler**: Without access to proper workflow tools like Airflow or Prefect, I used AWS EventBridge to trigger the Lambda functions every 15 minutes, creating a rudimentary scheduling system through multiple discrete executions.

4. **Validation Layer for Inconsistent Data**: To handle the varying data quality from manual inputs and different platform schemas, I built validation classes as a safety net, ensuring the pipeline remained functional despite upstream inconsistencies.

## Implementation Details

The solution was deliberately designed as a minimally viable product that could be implemented quickly without proper infrastructure:

```python
# Example of how I worked around Lambda time limitations
def lambda_handler(event, context):
    # Get only what we can process in ~15 minutes
    urls = get_next_url_batch(batch_size=25)

    # Log starting point for debugging across executions
    logging.info(f"Processing batch starting at offset {current_offset}")

    # Process as much as we can in the available time
    results = []
    for url in urls:
        # Check remaining time to avoid timeouts
        if context.get_remaining_time_in_millis() < 30000:  # 30 second buffer
            logging.warning("Running out of time, stopping batch processing")
            break

        # Process URL if time allows
        data = process_social_media_url(url)
        results.append(data)

    # Update processing marker for next Lambda invocation
    store_processing_state(current_offset + len(results))

    return {"processed_count": len(results), "remaining": len(urls) - len(results)}
```

To manage the distributed nature of this improvised solution, I created a simple state tracking mechanism:

```python
def get_next_url_batch(batch_size):
    # Read last processed position from S3
    current_position = read_marker_from_s3()

    # Query data source for next batch
    query = f"""
    SELECT url, platform_type, post_date
    FROM social_media_posts
    ORDER BY post_date DESC
    LIMIT {batch_size} OFFSET {current_position}
    """

    # Get the next batch to process
    return execute_query(query)
```

The entire solution involved cobbling together several AWS services in ways they weren't necessarily intended to be used, but that solved our immediate problem:

```python
# Example of our makeshift scheduling mechanism
def schedule_next_execution():
    # If we didn't process all URLs, ensure next Lambda runs soon
    if more_urls_to_process():
        # Create a one-time trigger to process more data
        response = events_client.put_rule(
            Name="immediate-continuation-rule",
            ScheduleExpression="rate(1 minute)",
            State="ENABLED"
        )
        # This creates a one-time execution to continue processing
```

## Results and Impact

Despite being a temporary workaround, this improvised solution delivered surprisingly effective results:

1. **Immediate Business Value**: Without waiting for proper infrastructure approval, we were able to deliver automated metrics within days rather than the months it might have taken to implement a "proper" solution.

2. **Cost Effectiveness**: The serverless approach meant we only paid for the actual execution time, keeping costs minimal compared to running dedicated servers.

3. **Sufficient Reliability**: While not architecturally elegant, the solution achieved approximately 98% data collection reliability, which was a massive improvement over the previous manual process.

4. **Proof of Concept**: The success of this hacky solution ultimately helped make the case for investing in proper data orchestration tools, as it demonstrated the clear business value of automation.

## Technical Challenges Overcome

Throughout this project, I encountered and solved several interesting challenges:

1. **Stateless to Stateful**: Lambda functions are designed to be stateless, but our process needed to track progress across executions. I created a simple state tracking mechanism using S3 to store processing markers.

2. **Timeout Management**: I implemented dynamic batch sizing that would adjust based on observed processing times, ensuring we maximized throughput without hitting Lambda timeouts.

3. **Error Containment**: Since each Lambda execution processed just a small batch, failures were isolated and didn't impact the entire dataset processing.

4. **Debugging Across Distributed Executions**: I implemented comprehensive logging with execution IDs to trace processing across multiple Lambda invocations, making it possible to debug issues in this distributed system.

## Lessons Learned

This project taught me several valuable lessons about pragmatic problem-solving in cloud environments:

1. **Perfect is the enemy of done**: Sometimes an imperfect solution that works today is better than a perfect solution that arrives too late.

2. **Creative use of available tools**: Cloud services can often be repurposed in creative ways when the ideal tool isn't available.

3. **Building with evolution in mind**: Even when implementing a stopgap solution, designing with eventual migration to a proper solution makes future transitions easier.

4. **Technical debt awareness**: I was transparent about the limitations of this approach from the beginning, ensuring everyone understood this was a temporary solution.

The "hack job" nature of this solution wasn't something to hide, but rather an example of pragmatic engineering in constrained circumstances. It demonstrated my ability to quickly deliver business value using cloud services, even when the ideal tools weren't available. Eventually, this solution was replaced with a proper orchestration system, but it served its purpose admirably during a critical time for the business.
