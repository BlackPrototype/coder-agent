# Guided Project 2: Coder Agent

## Recent Changes
Created a new feature to transform SQL queries into Knex.js queries in CoffeeScript language. You can compile CoffeeScript to JavaScript using the [CoffeeScript Compiler](https://coffeescript.org/v1/) by clicking the 'TRY COFFEESCRIPT' button. After compiling, you can validate the Knex.js code using the [Knex Playground](https://dgadelha.github.io/knex-playground/). This ensures that all CoffeeScript and Knex.js code is working correctly.
Eg:
```Prompt: change this sql to knex: "select * from fruits where a = 1 and b > 11 or c = 'apple'"


> Entering new AgentExecutor chain...

Invoking: `sql_to_knex_coffeescript` with `{'sql_query': "select * from fruits where a = 1 and b > 11 or c = 'apple'"}`

The equivalent Knex.js query in CoffeeScript syntax is:

\`\`\`coffeescript
knex 'fruits'
.select '*'
.where 'a', '=', 1
.andWhere 'b', '>', 11
.orWhere 'c', '=', 'apple'
```

## Overview
In this project, we developed a coder agent to enhance developer productivity. The core functionality of our agent is to write code and execute terminal commands on your behalf, streamlining your workflow and allowing you to focus on higher-level tasks. This approach can help speed up development, allowing development time on higher level tasks.

## Prerequisites
- Python 3.11 or greater (local setup)

## Setup and Execution

### Set up environment variables:
- Copy the sample environment file:
  ```
  cp .env.sample .env
  ```
- Edit the `.env` file and add your API keys:
  ```
   OPENAI_API_KEY=your-openai-key
   LANGCHAIN_API_KEY=your-langchain-key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=week_4_3
  ```

## Local Setup
If you prefer to run the examples locally:

1. Ensure you have Python 3.11.0 or higher installed.
2. Clone the repository:
    ```
    git clone [repository-url]
    cd [repository-name]
    ```
3. Set up the virtual environment:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
4. Configure environment variables as described in the Setup section.
5. export your `.env` variables to the system (python-dotenv should take care of this for you, but this is how you can do it manually):
   **Linux / Mac / Bash**
      ```
      export $(grep -v '^#' .env | xargs)
      ```
6. Run the script:
    ```
    python3 agent.py
    ```