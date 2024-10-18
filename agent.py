import os
from dotenv import load_dotenv
import subprocess
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langsmith import traceable
from langchain_community.tools.shell.tool import ShellTool
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
        else:
            return "Only basic SELECT queries are supported in this example."
    except Exception as e:
        return f"An error occurred while transforming SQL to Knex.js: {e}"

tools = [
    sql_to_knex_coffeescript,
    ShellTool(ask_human_input=True),
]

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

llm_with_tools = llm.bind_tools(tools)

agent = (
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

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while True:
    user_prompt = input("Prompt: ")
    list(agent_executor.stream({"input": user_prompt}))
