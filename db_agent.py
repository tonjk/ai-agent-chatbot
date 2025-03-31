from langchain.agents import Tool, AgentExecutor, create_openai_tools_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
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
        # self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0,)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", temperature=0, max_output_tokens=2048)

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

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

        # Create agent prompt with chat history and agent_scratchpad
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful database agent that can interact with a PostgreSQL database.
            When using SQL queries:
            - Always use proper SQL syntax
            - Be careful with UPDATE and DELETE operations
            - Validate input before executing queries
            - Return meaningful responses to the user
            - Use the chat history to maintain context of the conversation
            
            Current database schema:
            - user_info (id, name, email, created_at)
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent with the updated prompt
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            # memory=self.memory  # Add memory to the executor
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
                "chat_history": self.memory.chat_memory.messages,
                "agent_scratchpad": []  # Initialize empty scratchpad
            })
            
            # Store the interaction in memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response["output"])
            
            return response["output"]
        except Exception as e:
            error_msg = f"Error running agent: {str(e)}"
            self.memory.chat_memory.add_ai_message(error_msg)
            return error_msg

    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the current chat history
        
        Returns:
            List[Dict[str, str]]: List of chat messages
        """
        messages = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                messages.append({"role": "assistant", "content": message.content})
        return messages

    def clear_history(self):
        """Clear the chat history"""
        self.memory.clear()

async def main():
    agent = DatabaseAgent()
    print("Database Agent initialized. Type 'quit' to exit.")
    print("Special commands:")
    print("  - 'history': Show chat history")
    print("  - 'clear': Clear chat history")
    print("  - 'quit': Exit the program")
    
    while True:
        user_input = input("\nWhat would you like to know about the database? ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            history = agent.get_chat_history()
            print("\nChat History:")
            for msg in history:
                print(f"{msg['role'].title()}: {msg['content']}")
            continue
            
        if user_input.lower() == 'clear':
            agent.clear_history()
            print("\nChat history cleared.")
            continue
        
        if not user_input:
            continue
            
        try:
            response = await agent.run_agent(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 