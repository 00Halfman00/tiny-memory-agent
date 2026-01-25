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

## Hardware Recommendations

The agent runs a 20B parameter model locally. For a smooth experience:
- **GPU:** An NVIDIA RTX 3080 (or equivalent) with at least **16GB of VRAM** is recommended.
    - *Windows Users:* You can check your VRAM by opening **Task Manager** (Ctrl+Shift+Esc) -> **Performance** tab -> **GPU**. Look for "Dedicated GPU memory".
- **Memory:** The `ModelFile.txt` is optimized to offload layers to the GPU. If you have less than 16GB of VRAM, the model will "spill over" to your system RAM, significantly slowing down the response time.
- **CPU:** At least 8 cores are recommended to handle background tasks and any non-GPU-accelerated layers.

## Prerequisites (Software)

Before running the agent, you'll need to install a few tools.

### 1. Node.js (Required for Memory Graph)
The agent uses a tool called `npx` (part of Node.js) to manage its Knowledge Graph.
- **Download & Install:** Go to [nodejs.org](https://nodejs.org/) and download the **LTS** version.
- Follow the installer prompts (default settings are fine).

### 2. Git (To download the code)
- **Windows:** Download and install from [git-scm.com](https://git-scm.com/download/win).
- **macOS/Linux:** You likely already have it, or can install via your package manager (e.g., `brew install git`).

### 3. Ollama (The AI Engine)
This project uses a local Large Language Model.
- **Download & Install:** Get it from [ollama.com](https://ollama.com/).
- **Important:** The agent requires the Ollama server to be running. It is recommended to run `ollama serve` in a separate terminal window before starting the agent.
- **Note:** If you see an error indicating that an Ollama instance is already running, you should first quit the Ollama application (e.g., from the system tray) and then run `ollama serve` in your terminal.
- **Important:** Specific model configuration is required (see Step 2 below).

### 4. uv (Fast Python Tool)
This project uses `uv` for lightning-fast dependency management.
- **Windows:** Open PowerShell and run:
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS/Linux:** Open Terminal and run:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Getting Started

### Step 1: Download the Code
If you are familiar with GitHub, we recommend **forking** this repository to your own account first. Then, open your terminal (Command Prompt or PowerShell on Windows, Terminal on macOS/Linux), navigate to your desired folder, and run:

```bash
git clone https://github.com/your-username/tiny_memory_agent.git
cd tiny_memory_agent
```
*(If you didn't fork it, you can clone the original repository directly, but forking allows you to save your own changes!)*

### Step 2: Set up the Custom AI Model
1.  Ensure the **Ollama** server is running. We recommend opening a separate terminal and running:
    ```bash
    ollama serve
    ```
    *Note: If you get an error that Ollama is already running, quit the Ollama app from your system tray first.*
2.  In another terminal (inside the `tiny_memory_agent` folder), run this command to create the custom model:
    ```bash
    ollama create gpt-oss:20b-lab -f ModelFile.txt
    ```
    *This may take a while as it processes the model files.*

### Step 3: Set up Environment Variables (Required)
The agent uses the OpenAI SDK for telemetry and tracing. You must provide an API key, or the script may encounter errors:
1.  Create a file named `.env` in the project root folder.
2.  Add your OpenAI API key to the file:
    ```
    OPENAI_API_KEY=sk-proj-your-actual-key-here
    ```
    *(Bonus: Once running, you can view your execution traces at [platform.openai.com/traces](https://platform.openai.com/traces))*

### Step 4: Install Dependencies
Run this command to automatically set up the Python environment and install all libraries:
```bash
uv sync
```

### Step 5: Run the Agent
Start the interactive chat by running:
```bash
uv run twin/memory_agent.py
```

- You will see some initialization messages as the memory systems start up.
- Once ready, you can type your message next to the `You:` prompt.
- To stop the agent, type `exit` or `quit`.

## Troubleshooting

### "Model not found" error
If the command `ollama create ...` fails, it likely means the base model `gpt-oss:20b-lab` isn't in your Ollama library.
1.  Open `ModelFile.txt`.
2.  Change the first line (`FROM gpt-oss:20b-lab`) to a model you have installed (e.g., `FROM llama3` or `FROM mistral`).
3.  Save the file and run the `ollama create` command again.

### "File not found" errors
Ensure you are strictly following the "Getting Started" steps and running all commands from the root `tiny_memory_agent` folder.

We hope you have as much fun experimenting with the Tiny Memory Agent as we did building it!
