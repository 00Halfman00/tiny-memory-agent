# Tiny Memory Agent

This project is a demonstration of a "tiny" Large Language Model (LLM) agent that has been given a form of long-term memory. It's a fascinating look into how we can augment these powerful language models to create more capable and knowledgeable AI assistants.

## How it Works: A Glimpse into the AI's Mind

Imagine an AI that doesn't just understand language, but can also remember things it learns over time. That's the core idea behind this project. We've created a system where a small, efficient LLM can interact with different types of memory to provide more helpful and context-aware responses.

Here's a breakdown of the different memory systems at play, and how they come together to create a "Final Unified Mental Model":

*   **The LLM (The Thinker):** This is the core language model, the part of the AI that reasons, talks, and understands your requests. In this project, we're using a smaller, more efficient model that can run on consumer hardware.

*   **The Embedding Model (The Translator):** This is a special model that translates the meaning of text into a mathematical representation called a "vector." This allows the AI to understand the relationships between different pieces of information.

*   **The Vector DB (RAG) (The Rememberer):** This is the AI's long-term memory for facts and experiences. When you tell the AI something new, it uses the Embedding Model to translate that information into a vector and stores it in the Vector DB. When you ask a question, the AI can then search its memory for the most similar and relevant information to give you the best possible answer. This process is called Retrieval-Augmented Generation (RAG).

*   **The Knowledge Graph (The Knower):** This is a more structured form of memory that stores information about entities (like people, places, and organizations) and the relationships between them. For example, it might know that "John Doe" "works at" "Acme Inc." This allows the AI to build a more complex and interconnected understanding of the world.

*   **The Relational DB (The Question Asker):** This is a special memory system that keeps track of questions that the AI doesn't know the answer to. When you ask a question that the AI can't answer from its other memory systems, it will record the question in the Relational DB. This allows the AI's human operator to review the questions and provide answers, which can then be added to the AI's long-term memory.

*   **The RAG System (The Grounder):** This is the system that brings everything together. It uses the information from the different memory systems to "ground" the LLM's responses in reality. This helps to ensure that the AI's answers are accurate and consistent with what it knows.

## Prerequisites

Before running the agent, you'll need to set up a few things on your machine:

1.  **Ollama:** This project uses a local Large Language Model. Download and install it from [ollama.com](https://ollama.com/).
2.  **Custom Model:** We use a specific model configuration. Once Ollama is installed and running, open your terminal in this project's directory and run:
    ```bash
    ollama create gpt-oss:20b-lab -f ModelFile.txt
    ```
3.  **uv:** This project uses `uv` for lightning-fast dependency management.
    -   **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
    -   **macOS/Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Hardware Recommendations

The agent runs a 20B parameter model locally. For a smooth experience:
- **GPU:** An NVIDIA RTX 3080 (or equivalent) with at least **16GB of VRAM** is recommended.
- **Memory:** The `ModelFile.txt` is optimized to offload layers to the GPU. If you have less than 16GB of VRAM, the model will "spill over" to your system RAM, significantly slowing down the response time.
- **CPU:** At least 8 cores are recommended to handle background tasks and any non-GPU-accelerated layers.

## Getting Started

### 1. Fork and Clone
Fork this repository to your GitHub account, then clone it:
```bash
git clone https://github.com/your-username/tiny_memory_agent.git
cd tiny_memory_agent
```

### 2. Install Dependencies
Run the following command to set up the Python environment and install all necessary libraries:
```bash
uv sync
```

### 3. Run the Agent
Execute the main script to start the conversation:
```bash
uv run python twin/memory_agent.py
```

This will start the agent, and you'll see it initializing the different memory systems. You can interact with it by modifying the `task` variable inside `twin/memory_agent.py`.

We hope you have as much fun experimenting with the Tiny Memory Agent as we did building it!
