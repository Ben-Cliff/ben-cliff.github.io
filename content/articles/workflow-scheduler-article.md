Title: Modern Data Orchestration: Why Dagster Over Industry Standards - or not?
Date: 2024-03-20
Category: Data Engineering
Tags: workflow-scheduler, dagster, airflow, prefect, google-cloud-composer, dlt
Slug: workflow-scheduler-article

As a data team grows, there often comes a point where simple cron jobs no longer suffice for orchestrating increasingly complex pipelines. This article details the journey of finding the right scheduler solution that aligns with modern data workflow needs, technical requirements, and future growth plans.

Note, here is a fun project that I did before we started using Dagster as a scheduler: [no-scheduler-no-problem]({static}/articles/no-schduler-no-problem.md)

## From Ad-hoc Scripts to Strategic Orchestration

Until recently, our approach to workflow management had been decidedly minimalist. Python scripts executed via cron jobs, manual triggers, and a handful of scheduled dbt runs had been sufficient for our core reporting needs. But this approach was showing its limitations:

Our data science team's growing collection of ML models needed reliable, parameterized execution
One-off Python jobs were becoming impossible to monitor effectively
Failures in multi-step processes went undetected until downstream consumers reported issues
Our small data engineering team (just one dedicated engineer) was spending too much time on operational monitoring
With existing investments in dbt, Airbyte, and Fivetran, we needed a solution that would complement rather than compete with these tools

What we needed wasn't just another tool, but our first true orchestration layer—one that could bring order to our increasingly complex data ecosystem without requiring DevOps expertise we didn't have in-house. The right solution needed to be quick to deploy, intuitive to operate, and specifically optimized for Python-based data science workflows that were becoming central to our value proposition.

## Evaluating the Options

After identifying requirements, it's important to evaluate the available options thoroughly. In this case, four main contenders emerged: Dagster, Apache Airflow, Prefect, and Google Cloud Composer. Each offered distinct advantages and limitations, which were cataloged in a comparison table:

### Apache Airflow: The Industry Standard

As the original workflow orchestration tool, Airflow has a large community and extensive documentation. However, several factors made it less attractive for small, innovative teams:

* **Task vs Pipeline Focus**: Airflow is fundamentally task-focused rather than pipeline-focused. It uses XComs (cross-communication) to pass data between tasks, which can become cumbersome and difficult to maintain for complex data pipelines.

* **DevOps Complexity**: Setting up and maintaining Airflow requires significant engineering resources. The infrastructure demands become even more pronounced as data volumes grow. For small teams with limited engineering capacity, this operational overhead can be prohibitive.

* **Not Designed Specifically for Data**: Despite its widespread adoption in data engineering, Airflow was originally designed as a general-purpose workflow scheduler, not specifically for data workloads. This historical background means it sometimes lacks data-specific features that newer tools have incorporated from the ground up.

* **Innovation vs Established Technology**: Organizations with a culture of innovation may prefer to adopt newer technologies that offer improved developer experiences, even if they come with some adoption risk. Choosing Airflow often means following the established path rather than embracing potentially more efficient modern alternatives.

* **Hiring Considerations**: While choosing a less mainstream tool like Dagster over Airflow might create some hiring challenges, the Python-centric and intuitive nature of Dagster means that engineers familiar with Python can quickly adapt. This tradeoff between mainstream adoption and developer experience is worth considering based on team size and growth plans.

For organizations with small data teams looking to minimize operational complexity while maximizing developer productivity, Airflow's established nature doesn't necessarily outweigh its limitations.

### Prefect: The Modern Alternative

Prefect offered a more modern take on workflow orchestration with Python-native features. While attractive, we found its documentation less clear, and it seemed to push users toward its managed service. For a team looking to self-host, this raised concerns about long-term support for the open-source version.

### Google Cloud Composer: The Managed Service

Cloud Composer, Google's managed Airflow service, promised to eliminate infrastructure management challenges. However, several key factors worked against it:

1. **Limited learning opportunity**: The team wanted hands-on experience with data orchestration infrastructure, which a fully managed service wouldn't provide
2. **Vendor lock-in concerns**: The flexibility to potentially migrate to different cloud providers in the future was important
3. **Cost considerations**: As a fully managed service, Composer came with a higher price tag that was difficult to justify
4. **Environmental complexity**: Despite being managed, Composer still required complex environment separation for development, testing, and production

### Dagster: The Balanced Solution

Dagster emerged as the frontrunner for several compelling reasons:

1. **Python-first approach**: Its design caters specifically to data science workflows with strong Python integration
2. **Intuitive environment management**: Dagster makes it easy to separate development, testing, and production environments
3. **Moderate operational overhead**: While still requiring some infrastructure management, Dagster strikes the right balance for small teams
4. **Strong open-source commitment**: Unlike Prefect, Dagster appears more committed to supporting its open-source offering
5. **Clear documentation**: The deployment patterns and setup instructions are well-documented and accessible

Here's a comparison table of the evaluated options:

|  | **Dagster (self-hosted)** | **Google Cloud Composer (hosted)** | **Apache Airflow  (self-hosted)** | **Prefect  (self-hosted)** |
| --- | --- | --- | --- | --- |
| **Maturity** | ✅ | ✅  | ✅✅ (first on the market and seen as industry standard) | ✅ |
| **Cost** | ✅ Free | ❌ Paid | ✅ Free | ✅ Free |
| **Ease of Environment /Development Management** | ✅ | ❌ | ❌ | ❌ |
| **Operational Overhead** | ➖ Moderate | ✅ Low | ❌ High | ➖ Moderate |
| **Community Support** | ➖ | ✅ managed | ✅ (due to industry adoption) | ➖ |
| **Integration with Existing Stack** | ✅ | ✅ | ✅ | ✅ |
| **Infrastructure Management Capacity Required** | ➖ Moderate | ✅ managed | ❌ very high | ➖ Moderate |
| **Ease of Use for Data Science Workflows** | ✅ | ➖ | ➖ | ✅ |
| **Overall Fit for Small Teams** | ✅ | ➖ | ❌ | ✅ |

## DLT Integration: A Key Advantage

One of Dagster's standout features is its compatibility with Data Load Tool (DLT), an increasingly popular alternative to traditional ETL tools like Airbyte and Fivetran. This integration represents a significant advantage for modern data stacks and deserves a deeper look.

### What is DLT?

DLT (Data Load Tool) is an open-source Python framework designed for building and running data pipelines. Unlike traditional ETL tools that often require specialized knowledge or separate interfaces, DLT allows data engineers to build extraction, normalization, and loading processes directly in Python code. This approach brings several advantages:

1. **Developer-friendly**: Engineers can leverage familiar Python patterns rather than learning proprietary syntax
2. **Version control integration**: Pipeline code can be managed through standard Git workflows
3. **Testability**: Standard Python testing frameworks can be used to ensure pipeline reliability
4. **Extensibility**: Custom logic can be easily incorporated without platform limitations

### Dagster + DLT: Better Together

Dagster's [built-in integration with DLT](https://docs.dagster.io/integrations/embedded-elt/dlt) creates a powerful combination for modern data teams:

1. **First-class asset definition**: DLT pipelines can be defined as Dagster assets, making them first-class citizens within the data platform. This means they participate in Dagster's dependency resolution, lineage tracking, and materialization capabilities.

2. **Seamless orchestration**: Unlike other scheduler combinations, Dagster understands the internal structure of DLT pipelines, allowing for more granular scheduling and monitoring.

3. **End-to-end observability**: When DLT pipelines run within Dagster, both the extraction and loading processes appear in Dagster's UI, providing comprehensive visibility into the entire data workflow.

4. **Configuration management**: Dagster's robust configuration system can be leveraged to manage DLT pipeline parameters across environments.

### Real-world Applications

The Dagster-DLT integration excels in several common data engineering scenarios:

1. **API data ingestion**: Replace complex Fivetran connectors with custom DLT pipelines that extract data from APIs and load it directly into your data warehouse.

2. **Custom source normalization**: Apply business-specific transformations during the extraction process rather than pushing all transformation logic to downstream dbt models.

3. **Incremental loading patterns**: Implement sophisticated incremental loading strategies that are customized to your specific data sources and business needs.

4. **Schema evolution management**: Handle schema changes gracefully through code rather than through configuration UI.

For organizations looking to reduce dependence on proprietary ETL tools while maintaining operational excellence, the combination of Dagster for orchestration and DLT for extraction and loading presents a compelling, cost-effective alternative. This integrated approach also aligns with modern data engineering practices that favor code-first, version-controlled infrastructure.

## Cost Savings: The Fivetran Migration

A significant factor in the decision was the potential to migrate existing Fivetran jobs to a combination of Dagster and DLT. With Fivetran implementations often costing organizations approximately $20,000 annually, moving these jobs to a self-hosted Dagster implementation can project substantial savings.

The migration path looks promising:
1. Set up Dagster orchestration for data workflows
2. Implement DLT connectors for each Fivetran source
3. Gradually transition jobs from Fivetran to the Dagster/DLT stack
4. Decommission the Fivetran subscription once migration is complete

While this transition requires upfront engineering effort, the long-term cost savings (potentially $20,000 annually) and increased flexibility make it an attractive option for many organizations.

## Why Not Google Cloud Composer?

When operating within the Google Cloud ecosystem, many might wonder why Google Cloud Composer wouldn't be the natural choice. The primary reasons came down to learning opportunities, flexibility, and specific workflow needs:

1. **Learning Opportunity**: The data team expressly wanted to gain hands-on experience with data orchestration infrastructure. A managed service would limit this learning opportunity and skill development.

2. **ML Workflow Compatibility**: Data science teams often work primarily with Python-based machine learning workflows. Dagster's Python-native approach aligns better with these requirements than Composer's Airflow foundation.

3. **Hands-on Control**: A small, focused team often wants deeper visibility and control over their orchestration layer. Cloud Composer abstracts away many configuration details that teams may prefer to manage themselves.

4. **Vendor Independence**: Avoiding excessive dependence on a single cloud provider is a prudent strategy. Self-hosting Dagster offers the flexibility to potentially run the orchestration layer anywhere in the future.

5. **Cost Efficiency**: For specific use cases and scales, Dagster's self-hosted option can offer better cost efficiency than Cloud Composer's pricing model.

## Implementation and Looking Ahead

With the decision made, implementing Dagster as a workflow orchestration tool can proceed. The initial setup is relatively straightforward, following the [GCP deployment pattern](https://docs.dagster.io/deployment/guides/gcp) outlined in Dagster's documentation.

A typical implementation prioritizes:
- ML workflow orchestration for data science teams
- Data ingestion processes previously handled by manual scripts
- Eventual migration of Fivetran connectors

It's worth noting that many organizations maintain their dbt implementation for SQL-based transformations, with Dagster orchestrating these workflows alongside Python-based tasks.

Looking ahead, it's important to recognize that this solution may need to evolve as teams grow. However, at a smaller scale, Dagster offers the right balance of sophistication and manageability. The decision isn't irreversible - if needs change significantly, the migration path to another orchestration tool remains manageable for small teams with limited workflow complexity.

## Conclusion

Choosing the right workflow orchestration tool involves balancing technical requirements, team resources, cost considerations, and future flexibility. For organizations with small data teams managing Python-heavy workflows and desiring operational simplicity, Dagster often emerges as a strong contender.

By prioritizing Python compatibility, environment management, and DLT integration, organizations can build more robust, maintainable data infrastructure while avoiding unnecessary operational overhead. The projected cost savings from migrating away from solutions like Fivetran (potentially $20,000 annually) can further strengthen the business case.

For teams in similar situations, it's advisable to evaluate workflow tools not just on features, but on how they align with team composition, technical stack, and growth trajectory. Sometimes, the technically "most powerful" option isn't the right fit if it creates unsustainable operational demands on a small team.

*This article draws on insights from an Architecture Decision Record (ADR) documenting a workflow tool selection process.*
