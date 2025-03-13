Title: Building a Natural Language Data Interface with LLM Agents: Breaking Down the Technical Barriers
Date: 2024-03-20
Category: data engineering
Tags: LLM, agents, data, interface, slack, python, product
Slug: slack-analytics-bot

## The Data Access Challenge We Faced

As our data team grew, we encountered a familiar problem in the analytics world: the growing gap between those who could write SQL and those who needed data insights. We noticed our small analytics team was becoming a bottleneck - spending hours each week answering repetitive questions and writing similar queries for different stakeholders. Product managers and business teams were waiting days for simple data answers, while our data engineers and analysts were pulled away from more strategic work.

What started as a minor inconvenience turned into a significant operational problem when we realized that:

1. Non-technical team members were making decisions without data because the process to get insights was too cumbersome
2. Our analytics team was overwhelmed with ad-hoc requests, with little time for deeper analysis
3. Similar questions were being asked repeatedly, but the knowledge wasn't being captured or shared

## Taking Action with a Serverless Analytics Bot Powered by LLM Agents

After researching various approaches, we decided to create a serverless analytics bot that could understand natural language questions about our data, translate them to SQL, and deliver results directly in Slack where our teams already collaborated.

At its core, our solution leveraged a modern LLM agent architecture that enabled four key capabilities:

1. **Schema Understanding**: The ability to access and understand database schema information, including table structures, relationships, and data types
2. **Query Generation**: The ability to translate natural language questions into accurate SQL
3. **Query Execution**: The ability to safely execute generated queries against our data warehouse
4. **Result Analysis**: The ability to interpret query results and present them in human-friendly language

The solution we designed had several key components:

```
┌─────────────┐     ┌──────────────┐    ┌───────────────┐
│             │     │              │    │               │
│  Slack User │────▶│ Cloud        │───▶│ chatGPT API   │
│             │     │ Function     │    │ Agent         │
└─────────────┘     └──────────────┘    └───────────────┘
                           │                    │
                           │                    │
                           ▼                    │
                    ┌──────────────┐            │
                    │              │            │
                    │  Data        │◀───────────┘
                    │  Warehouse   │
                    └──────────────┘
```

## Understanding LLM Agent Architecture

Traditional chatbots are essentially stateless text generators - they receive input, generate a response, and that's it. LLM agents, in contrast, can maintain conversations with themselves, use specialized tools, and make decisions about which actions to take based on context.

Our implementation leveraged a function-calling pattern, where the LLM didn't directly execute code, but instead requested specific well-defined functions to be called with structured parameters. This created several key advantages:

- **Security**: The LLM never had direct access to our database or systems
- **Reliability**: Each function had predictable behavior and comprehensive error handling
- **Specialization**: Each function was optimized for a specific task in the data analysis workflow

When a user asked a question like "How many users signed up last month?", this triggered a self-conversation flow:

1. The LLM identified it needed schema information to answer the question
2. It called our schema tool with the relevant table names
3. Our system retrieved the actual database metadata
4. The LLM used this schema to generate a SQL query tailored to our database structure
5. The query was executed and results returned to the LLM
6. The LLM analyzed and explained the results to the user in natural language

This multi-step approach made complex queries approachable for non-technical users while ensuring accuracy and reliability throughout the process.

## Key Coding Concepts That Enabled Our Solution

The technical implementation of our analytics bot relied on several core programming principles and design patterns that created a robust bridge between technical and non-technical worlds.

### 1. Dependency Injection and Modular Tool Design

Our implementation created clear separation between the LLM's reasoning capabilities and the technical tools it could use. Instead of hardcoding functionality, we defined specific functions that the LLM could call when needed:

```python
# Example of our modular tool design (simplified)
def run_prompt(self, prompt):
    """Runs the assistant with the specified prompt."""
    try:
        return self.assistant.run(
            prompt=prompt,
            get_db_schema_tool=self._get_db_schema,
            generate_sql_tool=self._generate_sql,
            execute_sql_query_tool=self._execute_sql_query,
        )
    except Exception as error:
        log(f"Error running prompt: {error}")
        raise BotError from error
```

Each tool had a specific purpose and clear interface, allowing the LLM to choose the right tool for each user query:

- `get_db_schema_tool`: Retrieved metadata about database tables
- `generate_sql_tool`: Created SQL queries based on natural language and schema
- `execute_sql_query_tool`: Safely ran queries and returned results

This approach allowed us to rapidly add new features without disrupting existing functionality, creating a system that evolved with user needs rather than requiring users to adapt to rigid technical constraints.

### 2. Schema-Aware Query Generation

A critical innovation in our system was making the LLM aware of the actual database schema, enabling it to generate accurate SQL:

```python
# Example of schema-aware query generation (simplified)
def _generate_sql(self, goal, table_names):
    """Generates SQL for the specified goal using table metadata."""
    schemas = self._get_db_schema(table_names=table_names)

    prompt_template = (
        "Generate SQL that accomplishes this task:\n"
        f"```\n{goal}\n```\n\n"
        f"The dataset structure is as follows:\n```\n{schemas}\n```\n\n"
    )
    return self._generate_with_llm(prompt_template)
```

This approach was transformative because:
- It grounded the LLM in the actual database structure
- It eliminated hallucinated column names or tables
- It encouraged better SQL through knowledge of data types and constraints
- It improved query performance through awareness of table relationships

For non-technical users, this feature was perhaps the most important bridge. It allowed product managers to ask questions like "How many users tried our new feature last week?" without knowing table names, column structures, or SQL syntax. The bot translated these natural questions into precise technical queries because it understood both the human intent and the underlying data structure.

### 3. Error Handling as a Conversation

Instead of crashing when it encountered an error, we built our system to handle errors as part of the conversation flow:

```python
# Example of conversational error handling (simplified)
def execute_query(self, sql_query):
    """Executes SQL and handles errors gracefully."""
    try:
        results = self.database_client.query(sql_query).result()
        return (results, None)
    except Exception as e:
        error_message = f"Error executing query: {str(e)}"
        return ([], error_message)
```

When an error occurred, the system would pass this information back to the LLM, which could then:
1. Explain the error to the user in simple terms
2. Try a different approach to answer the question
3. Ask for clarification if needed

For example, if a user asked about a metric that didn't exist in our database, instead of returning a cryptic error, the bot might say: "I tried looking for data about daily sign-ups, but it seems we don't track that specific metric. However, I can show you weekly sign-ups or total monthly activations. Would either of those work for you?"

### 4. Stateless Implementation with Thread Management

We designed our system to be stateless (allowing it to scale horizontally) while preserving conversation context through a thread-based architecture:

```python
# Example of thread management (simplified)
def get_thread_id(self, conversation_id):
    """Retrieve LLM thread_id for a conversation."""
    query = """
        SELECT thread_id
        FROM conversation_threads
        WHERE conversation_id = '{conversation_id}'
    """
    results = self.database_client.query(query).result()
    for row in results:
        return row.thread_id
    return None
```

This approach gave us the best of both worlds:
- **Serverless scalability**: Each function invocation was independent
- **Conversation continuity**: Users could have multi-turn discussions about their data

For non-technical users, this meant they could have natural conversations with the bot that felt continuous and coherent. The technical complexity of maintaining state in a distributed system was completely invisible to them.

### 5. Comprehensive Observability

We built detailed instrumentation from the beginning, recording every step of each interaction:

```python
# Example of our observability pattern (simplified)
class BotRecorder:
    """Records all aspects of bot interactions."""

    time_of_request: str
    event_id: str
    user: str
    prompt: str
    thread_id: Optional[str]
    tool_calls: List[str]
    function_calls: Optional[List]
    errors: Optional[List[ProcessError]]
    output: Optional[str]
```

This approach provided us:
- A complete audit trail of all interactions
- Invaluable insights for debugging production issues
- The ability to analyze usage patterns and improve the system
- The foundation for transparency that built user trust

## Results That Bridged Technical Divides

After deploying the analytics bot, we saw several significant improvements:

### Faster Data Access
Non-technical team members went from waiting days for data insights to getting answers in seconds or minutes. Product managers could quickly test hypotheses without scheduling meetings with the analytics team.

### Reduced Technical Burden
Our data engineers and analysts reported a 70% reduction in ad-hoc query requests, freeing them to focus on more complex analytical work and system improvements.

### Knowledge Democratization
The bot created a transparent record of all data questions and answers, becoming an organizational knowledge base that anyone could access and learn from.

### Unexpected Cultural Benefits
Perhaps the most surprising outcome was how the bot changed the relationship between our technical and non-technical teams. By providing a simple interface to complex data, it:

1. Helped product managers develop more data-informed intuition
2. Gave business teams the vocabulary to ask better questions
3. Allowed technical teams to understand business priorities more clearly

One product manager shared: "I'm no longer afraid to ask 'stupid' data questions since I can just ask the bot. This has helped me understand our metrics much better and make more confident decisions."

## Lessons and Future Improvements

While the project was largely successful, we learned several important lessons:

1. **Start simpler than you think necessary**: Our initial architecture was overly complex. We should have built a minimal viable product first and then iterated.

2. **Invest in clear table documentation**: The quality of the bot's answers was directly related to how well our database schemas were documented.

3. **Build for transparency**: Recording all bot interactions not only helped with debugging but also built trust with users who could see exactly how their questions were being interpreted.

Future improvements we'd like to implement include:

- Adding more visualization capabilities
- Building a feedback loop for continuous learning
- Integrating with our experiment tracking system

## Conclusion

Building this natural language data interface taught us that technical solutions are most powerful when they remove barriers rather than create them. By focusing on the human element—making data accessible to everyone regardless of technical ability—we created a tool that not only improved efficiency but also transformed how our organization related to its data.

The combination of modern LLM agent architecture with thoughtful system design principles created a solution that could:

1. **Understand** natural language questions about complex data
2. **Translate** these questions into accurate database queries
3. **Execute** these queries efficiently against our data warehouse
4. **Explain** the results in accessible, non-technical language

The most rewarding aspect wasn't the technical implementation, but seeing how it empowered our non-technical colleagues to become more data-driven in their thinking and decision-making. This experience reinforced our belief that the most valuable technical work often happens at the intersection of human needs and technical capabilities.

For organizations looking to build similar bridges between technical and non-technical teams, we recommend focusing on:

- A strong foundation of well-documented data schemas
- Robust error handling and feedback loops
- Clear separation of concerns between AI components and execution logic
- Comprehensive logging for transparency and debugging

With the rapid evolution of LLM capabilities, these types of interfaces will become increasingly important in democratizing data access across organizations of all sizes.
