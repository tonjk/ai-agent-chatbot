# AI Agent Chatbot

A chatbot system built with LangChain that uses AI agents to interact with users and perform tasks. The system leverages OpenAI's powerful language models and LangChain's agent framework to create an intelligent conversational interface.

## Features

- OpenAI-powered conversational AI using GPT-4 models
- PostgreSQL database integration for data persistence
  - Stores user information and conversation history
  - Supports complex SQL queries through database agent
- LangSmith integration for tracing and monitoring
  - Track agent performance and conversation flows
  - Debug and optimize agent behavior
  - Monitor usage metrics and costs
- Environment-based configuration
  - Secure API key management
  - Flexible database connection settings
  - Easy deployment across environments

## Prerequisites

- Python 3.8+ with pip package manager
- PostgreSQL database server (version 12+)
- OpenAI API key with access to GPT-4 models
- LangSmith account (for tracing)
  - API key for LangSmith integration
  - Project setup in LangSmith dashboard

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env_bak` to `.env` and configure your environment variables
5. Initialize the PostgreSQL database with the provided schema

## Usage

1. Start the chatbot: `python db_agent.py`
2. Interact with the agent through natural language queries
3. Monitor interactions in the LangSmith dashboard

## Next Steps

- Add Langgraph to control other agents
  - Implement complex agent workflows
  - Enable multi-agent collaboration
  - Add branching logic and decision trees
- Enhance database capabilities
- Improve error handling and recovery
- Add user authentication and authorization

## Note
Good luck with your implementation! Feel free to contribute or raise issues if you encounter any problems.