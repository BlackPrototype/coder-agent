import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

ROOT_DIR = "./"
VALID_FILE_TYPES = {"py", "md", "coffee", "sql", "js"}

@tool
def check_sql_syntax(sql_query: str) -> str:
    """
    Checks the SQL syntax for PostgreSQL using a basic parser.
    Parameters:
    sql_query (str): The SQL query to check.
    Returns:
    str: A message indicating whether the syntax is correct or an error message.
    """
    if not sql_query.strip().endswith(";"):
        return "SQL syntax error: Query should end with a semicolon."
    
    if sql_query.count("(") != sql_query.count(")"):
        return "SQL syntax error: Unbalanced parentheses."
    
    keywords = ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE"]
    if not any(keyword in sql_query.upper() for keyword in keywords):
        return "SQL syntax error: Missing SQL command keyword."
    
    return "SQL syntax appears to be correct."

@tool
def suggest_sql_improvements(sql_query: str) -> str:
    """
    Suggests improvements for the given SQL query.
    Parameters:
    sql_query (str): The SQL query to improve.
    Returns:
    str: Suggestions for improving the SQL query.
    """
    suggestions = []
    if "SELECT *" in sql_query.upper():
        suggestions.append("Avoid using SELECT *; specify columns explicitly.")
    if "JOIN" in sql_query.upper() and "ON" not in sql_query.upper():
        suggestions.append("Ensure JOIN conditions are specified with ON.")
    if "WHERE" in sql_query.upper() and "INDEX" not in sql_query.upper():
        suggestions.append("Consider using indexes for columns in WHERE clause.")
    return "SQL Improvement Suggestions:\n" + "\n".join(suggestions) if suggestions else "SQL query is well-optimized."

@tool
def sql_to_knex_coffeescript(sql_query: str) -> str:
    """
    Transforms an SQL query into a Knex.js query in CoffeeScript syntax.
    Parameters:
    sql_query (str): The SQL query to transform.
    Returns:
    str: The equivalent Knex.js query in CoffeeScript.
    """
    try:
        sql_query = sql_query.strip().lower()
        if sql_query.startswith("select"):
            select_part = sql_query.split("from")[0].replace("select", "").strip()
            table_part = sql_query.split("from")[1].strip().split(" ")[0]

            where_clause = []
            if "where" in sql_query:
                where_part = sql_query.split("where")[1].strip()
                conditions = where_part.split()
                current_operator = "where"
                for i in range(0, len(conditions), 4):
                    if i > 0:
                        if conditions[i-1].lower() == "and":
                            current_operator = "andWhere"
                        elif conditions[i-1].lower() == "or":
                            current_operator = "orWhere"
                    column, operator, value = conditions[i:i+3]

                    if value.isdigit():
                        formatted_value = value
                    elif value.startswith("'") and value.endswith("'"):
                        formatted_value = value
                    else:
                        formatted_value = f"'{value}'"

                    where_clause.append(f".{current_operator} '{column}', '{operator}', {formatted_value}")

            knex_query = f"knex '{table_part}'\n.select '{select_part}'"
            for clause in where_clause:
                knex_query += f"\n{clause}"

            return f"{knex_query}\n"
        return "Only basic SELECT queries are supported in this example."
    except Exception as e:
        return f"An error occurred while transforming SQL to Knex.js: {e}"

@tool
def clean_code_tool(code_snippet: str) -> str:
    """
    Checks if the code snippet follows clean code practices.
    """
    issues = []
    lines = code_snippet.split('\n')
    for i, line in enumerate(lines):
        if len(line) > 80:
            issues.append(f"Line {i+1} exceeds 80 characters.")
        if line.startswith(' ') and (len(line) - len(line.lstrip(' '))) % 2 != 0:
            issues.append(f"Line {i+1} is not indented with 2 spaces.")
    if not code_snippet.strip().endswith('\n\n'):
        issues.append("Ensure there is an empty line after variable declarations.")
    if not code_snippet.strip().endswith('.coffee'):
        issues.append("The code should be a good example of a CoffeeScript file.")
    return "Clean Code Issues:\n" + "\n".join(issues) if issues else "Code is clean."

@tool
def improvement_tool(code_snippet: str) -> str:
    """
    Suggests improvements for the given code snippet.
    """
    suggestions = []
    
    if "for" in code_snippet and "for" in code_snippet.split("for", 1)[1]:
        suggestions.append("Consider refactoring nested loops for better performance.")
    
    if "if" in code_snippet and "and" in code_snippet.split("if", 1)[1]:
        suggestions.append("Simplify complex conditions in if statements.")
    
    lines = code_snippet.split('\n')
    if len(lines) != len(set(lines)):
        suggestions.append("Avoid code repetition; consider using functions.")
    
    return "Logic Improvement Suggestions:\n" + "\n".join(suggestions) if suggestions else "Code logic is well-structured."

@tool
def check_code_snippet(input: dict) -> str:
    """
    Uses multiple tools to check and improve a code snippet.
    """
    print(input)
    code_snippet = input.get("input", "")
    clean_code_output = clean_code_tool(code_snippet)
    improvement_output = improvement_tool(code_snippet)
    return f"{clean_code_output}\n\n{improvement_output}"

llm = ChatOpenAI(model="gpt-4o", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert web developer.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_sql_tools = llm.bind_tools([suggest_sql_improvements, check_sql_syntax])
llm_with_code_tools = llm.bind_tools([check_code_snippet, clean_code_tool, improvement_tool])
llm_with_knex_tool = llm.bind_tools([sql_to_knex_coffeescript])

def create_agent(llm_with_tools):
    return (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )

def create_agent_executor(agent, tools, verbose=True):
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)

sql_agent = create_agent(llm_with_sql_tools)
code_agent = create_agent(llm_with_code_tools)
knex_agent = create_agent(llm_with_knex_tool)

agent_executor = create_agent_executor(sql_agent, [suggest_sql_improvements, check_sql_syntax])
code_agent_executor = create_agent_executor(code_agent, [check_code_snippet, clean_code_tool, improvement_tool])
knex_agent_executor = create_agent_executor(knex_agent, [sql_to_knex_coffeescript])

def run_agents():
    executors = {
        "code": code_agent_executor,
        "knex": knex_agent_executor,
        "sql": agent_executor
    }
    
    while True:
        print("Use one of the following keywords based on your needs: " +
              ", ".join(executors.keys()))
        user_prompt = input("Prompt: ").lower()
        
        for key, executor in executors.items():
            if key in user_prompt:
                print(f"Running {key} agent...")
                list(executor.stream({"input": user_prompt}))

if __name__ == "__main__":
    run_agents()
