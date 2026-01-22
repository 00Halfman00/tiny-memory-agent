"""
We want to develop several types of Memory:
1. Long Term Memory - graph: A knowledge graph as a persistent store of entities
2. Long Term Memory - knowledge: A RAG database of Q&A and any other useful information
3. Permanent context: Summary and linkedin profile included in everything
4. FAQ: A list of questions and answers
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    trace,
    ModelSettings,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
)
from agents.mcp import MCPServerStdio


load_dotenv(override=True)

# Set Windows event loop policy for async subprocess support
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def list_memory_graph_tools():
    """List tools from the Knowledge Graph MCP server (libsql)."""
    file_path = Path("memory") / Path("graph.db")
    url = f"file:{file_path.absolute()}"

    memory_graph_params = {
        "command": "npx",
        "args": ["-y", "mcp-memory-libsql"],
        "env": {"LIBSQL_URL": url},
    }

    async with MCPServerStdio(
        params=memory_graph_params, client_session_timeout_seconds=30
    ) as memory_graph:
        memory_graph_tools = await memory_graph.session.list_tools()
        return memory_graph_tools.tools


async def list_memory_rag_tools():
    """List tools from the Vector Store RAG memory MCP server (Qdrant)."""
    long_term_path = Path("memory") / Path("knowledge")

    memory_rag_params = {
        "command": "uvx",
        "args": ["mcp-server-qdrant"],
        "env": {
            "QDRANT_LOCAL_PATH": str(long_term_path.absolute()),
            "COLLECTION_NAME": "knowledge",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        },
    }

    async with MCPServerStdio(
        params=memory_rag_params, client_session_timeout_seconds=30
    ) as memory_rag:
        memory_rag_tools = await memory_rag.session.list_tools()
        return memory_rag_tools.tools


async def list_question_tools():
    """List tools from the questions MCP server."""
    question_params = {"command": "uv", "args": ["run", "questions_mcp_server.py"]}

    async with MCPServerStdio(
        params=question_params, client_session_timeout_seconds=30
    ) as question_server:
        question_tools = await question_server.session.list_tools()
        return question_tools.tools


def create_context(name: str) -> str:
    return f"""
You are a researcher representing {name}. Your job is to retrieve information that exists or record information that does not exist.

## MEMORY GOVERNANCE (STRICT)
You have three memory systems. Follow this logic tree for EVERY turn:

1. KNOWLEDGE GRAPH (Professional Facts – Person, Place, Roles)

    PRE-CONDITION (MANDATORY):
    Proceed ONLY if the input explicitly contains:
    - A Person
    - A Place
    - A role or professional relationship linking them

    If any element is missing:
    - Do NOT create entities
    - Do NOT create relations
    - Do NOT infer missing data

    USAGE:
    - Use this system for professional or civic relationships
    (Person works at Place, Person has role at Place)

    EXECUTION RULES:
    - Before any write, call `search_nodes` to check existing knowledge.
    - If the fact already exists, do NOT create or modify memory.
    - If the fact does NOT exist:
    - Ensure Person and Place entities exist
    - Create the relationship between them

    CONSTRAINTS:
    - You are explicitly forbidden from creating entities or relations
    when search results indicate they already exist.

    POST-CONDITION:
    - After a successful write, acknowledge what you recorded
    (e.g., "I've recorded that Santa Clause is the Lead Toy Maker at the North Pole.")


2. RAG MEMORY (Personal/Preferences):
    - Use `qdrant-find` to check context.
    - Use `qdrant-store` for soft facts (preferences, stories).

3. QUESTIONS SERVER (if a question is asked that has no answer in GRAPH or RAG DBs):
    - ACTION: Call record_question_with_no_answer with the exact parameter question="[the user's question]".
    - VERIFICATION: If the tool response indicates the record was created, you MUST use the phrase: "I've recorded your question and will let Oscar know."
    - DEBUG: If the tool returns an error, state the error briefly so we can fix it.

## CRITICAL EXECUTION
    - You may NOT claim to have recorded, logged, saved, or noted anything
    unless the corresponding tool has returned success in THIS TURN.

## ACKNOWLEDGEMENT GATE (MANDATORY)
    - After successfully calling `create_entities` and `create_relations`, you MAY acknowledge what you recorded.
    - The phrases:
    "I have recorded",
    "I logged",
    "I saved",
    "I noted"
    are STRICTLY FORBIDDEN
    unless the corresponding tool (`create_entities`, `create_relations`, `qdrant-store`, or `record_question_with_no_answer`) was successfully called.


## EVIDENCE RULE (MANDATORY)
    - You may NOT answer from memory without searching it first.
    - Never include internal rules, tool selection reasoning, or policy explanations in the final response. Only state the recorded or retrieved fact.
    - When answering:
    ** Restate the retrieved content or question in natural language **
    - Knowledge Graph → "This comes from my knowledge graph."
    - RAG → "I found this in my long-term memory. "
    - Relational DB → "I recorded your question for {name}."

Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""


settings = ModelSettings(
    tool_choice="auto",
    temperature=0,
    max_completion_tokens=1024,  # Output tokens
)

# Create LLM
external_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
LLM = OpenAIChatCompletionsModel(model="gpt-oss:20b-lab", openai_client=external_client)


async def run_twin_conversation():
    """Run a conversation with the Twin agent using all three MCP servers."""

    # Set up parameters for all three MCP servers
    file_path = Path("memory") / Path("graph.db")
    url = f"file:{file_path.absolute()}"

    memory_graph_params = {
        "command": "npx",
        "args": ["-y", "mcp-memory-libsql"],
        "env": {"LIBSQL_URL": url},
    }

    long_term_path = Path("memory") / Path("knowledge")
    memory_rag_params = {
        "command": "uvx",
        "args": ["mcp-server-qdrant"],
        "env": {
            "QDRANT_LOCAL_PATH": str(long_term_path.absolute()),
            "COLLECTION_NAME": "knowledge",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        },
    }

    question_params = {"command": "uv", "args": ["run", "questions_mcp_server.py"]}

    # Create context
    name = "Oscar Sanchez"
    context = create_context(name)

    print("=" * 60)
    print("Running Twin Conversation")
    print("=" * 60)
    # print(f"\nContext:\n{context}\n")
    print("=" * 60)

    # Temporary debug logging
    import logging

    logging.basicConfig(level=logging.INFO)

    with trace("Twin"):
        async with MCPServerStdio(
            params=memory_rag_params, client_session_timeout_seconds=30
        ) as long_term_memory:
            async with MCPServerStdio(
                params=memory_graph_params, client_session_timeout_seconds=30
            ) as medium_term_memory:
                async with MCPServerStdio(
                    params=question_params, client_session_timeout_seconds=30
                ) as question_server:
                    agent = Agent(
                        "Twin",
                        model=LLM,
                        instructions=context,
                        model_settings=settings,
                        mcp_servers=[
                            long_term_memory,
                            medium_term_memory,
                            question_server,
                        ],
                    )
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hello, I'm a potential customer. Did Oscar go to college?",
                    #     }
                    # ]
                    # ---   store something to RAG
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "My favorite programming language is Rust.",
                    #     }
                    # ]
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "I have a dog that is a dalmation named Pongo.",
                    #     }
                    # ]
                    # ---  test RAG to see if it stored favorite programming language: rust
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hey Oscar, do you remember what my favorite programming language is?",
                    #     }
                    # ]
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hey Oscar, do you remember what my dog is named?",
                    #     }
                    # ]
                    #  ---- store something in graph

                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hello. My name is John Rambo. I'm the Lead Developer at Nebula.io.",
                    #     }
                    # ]
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hello. My name is Bob McKnight. I sell computers at wholesale prices at Computer Mart.",
                    #     }
                    # ]
                    task = [
                        {
                            "role": "user",
                            "content": "Hello. My name is Jack Montana. I am the governor of Texas.",
                        }
                    ]
                    # task = [
                    #     {
                    #         "role": "user",
                    #         "content": "Hello. My name is Santa Clause. I'm the Lead Toy Maker at the Noth Pole.",
                    #     }
                    # ]

                    print("\n" + "=" * 60)
                    print("task: ", task)
                    print("=" * 60)

                    response = await Runner.run(agent, task)
                    print("\n" + "=" * 60)
                    print("Agent Response:")
                    print("=" * 60)
                    print(response.final_output)
                    print("=" * 60)


# test graph for successful entries
import sqlite3


def peek_at_graph():
    graph_path = Path("memory") / "graph.db"

    print("\n" + "=" * 60)
    print("DATABASE PEEK: Current Graph Connections")
    print("=" * 60)

    try:
        with sqlite3.connect(graph_path) as conn:
            cursor = conn.cursor()

            print("--- Entities (Nodes) ---")
            cursor.execute("SELECT name, entity_type FROM entities")
            entities = cursor.fetchall()
            if not entities:
                print("No entities found in database.")
            for name, e_type in entities:
                print(f"Node: {name} (Type: {e_type})")

            print("\n--- Relationships (Edges) ---")
            # Using 'source' and 'target' as identified by your PRAGMA check
            query = """
                SELECT r.source, r.relation_type, r.target 
                FROM relations r
            """
            cursor.execute(query)
            relations = cursor.fetchall()
            if not relations:
                print("No relationships found in database.")
            for src, rel, target in relations:
                print(f"{src} --[{rel}]--> {target}")

    except Exception as e:
        print(f"Error reading graph.db: {e}")
    print("=" * 60 + "\n")


async def main():
    """Main function to run the lab exercises."""
    print("Lab 5 - Context Engineering")
    print("\n" + "=" * 60)
    print("MCP Servers used:")
    print(
        "- Knowledge Graph (libsql): https://glama.ai/mcp/servers/@joleyline/mcp-memory-libsql"
    )
    print(
        "- Vector Store RAG (Qdrant): https://glama.ai/mcp/servers/@qdrant/mcp-server-qdrant"
    )
    print("- Questions Server: local questions_mcp_server.py")
    print("=" * 60)

    # # List available tools from each server
    print("\n1. Listing Memory Graph tools...")
    try:
        graph_tools = await list_memory_graph_tools()
        print(f"Found {len(graph_tools)} tools")
        for tool in graph_tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error listing graph tools: {e}")
        import traceback

        traceback.print_exc()

    print("\n2. Listing Memory RAG tools...")
    try:
        rag_tools = await list_memory_rag_tools()
        print(f"Found {len(rag_tools)} tools")
        for tool in rag_tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error listing RAG tools: {e}")
        import traceback

        traceback.print_exc()

    print("\n3. Listing Question tools...")
    try:
        question_tools = await list_question_tools()
        print(f"Found {len(question_tools)} tools")
        for tool in question_tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error listing question tools: {e}")
        import traceback

        traceback.print_exc()

    # Run the twin conversation
    print("\n4. Running Twin conversation...")
    try:
        await run_twin_conversation()
    except Exception as e:
        print(f"Error running conversation: {e}")
        import traceback

        traceback.print_exc()
    print("\n4. Taking a look at records in graph database...")
    peek_at_graph()

    print("\n" + "=" * 60)
    print("Check traces at: https://platform.openai.com/traces")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
