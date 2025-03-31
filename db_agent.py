from langchain.agents import Tool, AgentExecutor, create_openai_tools_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import asyncio
# Load environment variables
load_dotenv()

class DatabaseTools:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )

    def query_database(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return the results"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def modify_database(self, query: str) -> str:
        """Execute INSERT, UPDATE, or DELETE queries"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                return "Operation completed successfully"
        except Exception as e:
            self.connection.rollback()
            return f"Error modifying database: {str(e)}"

class DatabaseAgent:
    def __init__(self):
        self.db_tools = DatabaseTools()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.4,
            max_output_tokens=5096
        )

        # Define tools
        self.tools = [
            Tool(
                name="query_database",
                func=self.db_tools.query_database,
                description="Use this tool to execute SELECT queries on the database. Input should be a valid SQL SELECT query."
            ),
            Tool(
                name="modify_database",
                func=self.db_tools.modify_database,
                description="Use this tool to execute INSERT, UPDATE, or DELETE queries. Input should be a valid SQL query."
            )
        ]

        # Create agent prompt with agent_scratchpad
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful database agent that can interact with a PostgreSQL database.
            When using SQL queries:
            - Always use proper SQL syntax
            - Be careful with UPDATE and DELETE operations
            - Validate input before executing queries
            - Return meaningful responses to the user
            
            Current database schema:
            - user_info (id, name, email, created_at)
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent with the updated prompt
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True  # Add error handling for parsing
        )

    async def run_agent(self, query: str) -> str:
        """
        Run the agent with the given query
        
        Args:
            query (str): The user's query about database operations
            
        Returns:
            str: The agent's response
        """
        try:
            response = await self.agent_executor.ainvoke({
                "input": query,
                "agent_scratchpad": []  # Initialize empty scratchpad
            })
            return response["output"]
        except Exception as e:
            return f"Error running agent: {str(e)}"

async def main():
    agent = DatabaseAgent()
    print("Database Agent initialized. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nWhat would you like to know about the database? ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
            
        try:
            response = await agent.run_agent(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 