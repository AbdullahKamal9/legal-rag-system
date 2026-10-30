# Legal Contract Q&A: RAG System

An AI assistant that answers questions about legal contracts. Upload a contract PDF, ask a question in plain English, and get an answer with the page and section it came from.

Built with Retrieval Augmented Generation (RAG), hybrid search (BM25 + vector), and LangSmith tracing.

---

## Table of Contents

1. [Why I Built This](#why-i-built-this)
2. [What It Achieves](#what-it-achieves)
3. [What It Does](#what-it-does)
4. [How It Works](#how-it-works)
5. [Tech Stack](#tech-stack)
6. [Why Hybrid Search?](#why-hybrid-search)
7. [Project Structure](#project-structure)
8. [Dependencies](#dependencies)
9. [Setup and Run on Your Machine](#setup-and-run-on-your-machine)
10. [Example Questions](#example-questions)
11. [Failures and What I Learned](#failures-and-what-i-learned)
12. [Known Limitations](#known-limitations)
13. [Future Improvements](#future-improvements)

---

## Why I Built This

Legal contracts are long, full of dense language, and slow to read. Finding one clause (like termination terms or payment dates) means scrolling through dozens of pages. Normal chatbots are also risky here, because they can make up answers that sound correct but are not in the document.

**Purpose of this project:**

- Build a real RAG system, not just a demo that calls an LLM.
- Make an assistant that answers **only from the uploaded contract** and shows where the answer came from.
- Learn how retrieval quality affects answer quality, and how to measure it with tracing.

---

## What It Achieves

- Turns a long contract into something you can ask questions to.
- Gives answers grounded in the document, with **page and section references** so you can verify them.
- Finds both exact legal terms (keyword match) and related ideas (meaning match) by using hybrid search.
- Makes every step visible with LangSmith, so you can see what was retrieved and why an answer was good or bad.

---

## What It Does

1. You upload a contract as a PDF in the web app.
2. The app reads the PDF and splits it into small chunks.
3. Each chunk is converted into an embedding and stored in a local vector database.
4. You type a question, such as *"What is the notice period for termination?"*
5. The system finds the most relevant chunks using two search methods together.
6. Those chunks are sent to the LLM with a legal assistant prompt.
7. You get an answer with the source page and section.

---

## How It Works

```
PDF upload
   |
   v
PyPDFLoader  --> reads text page by page
   |
   v
RecursiveCharacterTextSplitter (chunk size 1000, overlap 200)
   |
   v
OpenAI text-embedding-3-small  --> embeddings
   |
   v
ChromaDB (vector store)
   |
   v
User question --> Hybrid Retrieval (BM25 + Vector MMR)
   |
   v
Top chunks + legal assistant prompt --> GPT-4o-mini
   |
   v
Answer + page/section citation  (traced in LangSmith)
```

**Key design choices:**

- **Chunk size 1000, overlap 200:** big enough to keep a full clause together, with overlap so a clause cut at the edge is not lost.
- **MMR (Maximal Marginal Relevance):** avoids returning five near-identical chunks. It picks relevant chunks that are also different from each other.
- **Prompt rule:** the model is told to answer only from the given context and to say when the answer is not in the contract.

---

## Tech Stack

| Part | Tool |
|---|---|
| LLM | GPT-4o-mini (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| Vector store | ChromaDB |
| Retrieval | Hybrid search: BM25 + Vector MMR |
| Framework | LangChain |
| Tracing | LangSmith |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## Why Hybrid Search?

Each search method fails in a different way:

- **BM25 (keyword search)**
  - Good at exact terms: "indemnification", "Section 12.3", "force majeure".
  - Bad when the question uses different words than the contract.
- **Vector search (meaning search)**
  - Good at related ideas: "ending the agreement" matches "termination".
  - Bad at exact numbers, names, and clause references.

Legal text needs both. Combining them gives better retrieval than either one alone, and retrieval quality decides answer quality.

---

## Project Structure

```
legal-rag-system/
├── app.py            # Streamlit UI: upload PDF, ask questions, show answers
├── rag.py            # RAG pipeline: load, split, embed, retrieve, answer
├── requirements.txt  # Python dependencies
├── .gitignore        # Keeps secrets and local data out of Git
└── README.md
```

---

## Dependencies

Main packages (check `requirements.txt` for the exact pinned versions):

| Package | Used for |
|---|---|
| `streamlit` | Web UI |
| `langchain` | Pipeline and prompt chain |
| `langchain-community` | PDF loader, BM25 retriever |
| `langchain-openai` | OpenAI LLM and embeddings |
| `chromadb` | Vector database |
| `pypdf` | Reading PDF files |
| `rank_bm25` | BM25 keyword search |
| `langsmith` | Tracing and debugging |
| `python-dotenv` | Loading API keys from `.env` |

**You also need:**

- Python 3.10 or newer
- An [OpenAI API key](https://platform.openai.com/api-keys) (paid usage, but small contracts cost very little)
- A [LangSmith API key](https://smith.langchain.com/) (optional, free tier works)

---

## Setup and Run on Your Machine

**1. Clone the repo**

```bash
git clone https://github.com/AbdullahKamal9/legal-rag-system.git
cd legal-rag-system
```

**2. Create a virtual environment**

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API keys**

Create a file named `.env` in the project folder:

```env
OPENAI_API_KEY=your_openai_key_here

# Optional: LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=legal-rag-system
```

Never commit this file. It is already ignored by `.gitignore`.

**5. Run the app**

```bash
streamlit run app.py
```

Open the link shown in the terminal (usually `http://localhost:8501`).

**6. Use it**

- Upload a contract PDF.
- Wait for processing to finish.
- Type your question and read the answer with its page reference.

**Common problems:**

- `ModuleNotFoundError`: the virtual environment is not active, or step 3 failed.
- `AuthenticationError`: your OpenAI key is missing or wrong in `.env`.
- Empty or wrong answers: the PDF may be a scanned image. This system needs a PDF with real text (see limitations).

---

## Example Questions

- "What is the termination notice period?"
- "Who is responsible for paying taxes under this agreement?"
- "Does the contract have a non-compete clause?"
- "What happens if a payment is late?"
- "What is the governing law?"

---

## Failures and What I Learned

> Replace the items below with your real experience. Keep only what actually happened to you.

**Failure 1: Vector search alone missed exact legal terms.**
- Questions with a specific clause name or number returned unrelated chunks.
- *Fix:* added BM25 and combined it with vector search.
- *Lesson:* semantic search is not enough when exact wording matters.

**Failure 2: Retrieved chunks were repetitive.**
- Top results were often near-duplicates, so the model saw the same text several times and missed other relevant clauses.
- *Fix:* switched to MMR for the vector side.
- *Lesson:* more chunks is not better. Diverse chunks are better.

**Failure 3: Chunking cut clauses in half.**
- Small chunks split a clause, so the answer was incomplete.
- *Fix:* tuned to chunk size 1000 with overlap 200.
- *Lesson:* chunking settings change results more than most people expect. Test them, do not guess.

**Failure 4: I could not tell why an answer was wrong.**
- Without visibility, I could not tell if retrieval or the LLM was at fault.
- *Fix:* added LangSmith tracing.
- *Lesson:* when a RAG answer is bad, retrieval is the cause most of the time. Check the retrieved chunks first.

**Failure 5: The model sometimes answered from its own knowledge.**
- It gave general legal answers not found in the contract.
- *Fix:* tightened the prompt to answer only from the context and to say "not found" otherwise.
- *Lesson:* prompt rules matter, but they reduce hallucination. They do not remove it.

---

## Known Limitations

- **Scanned PDFs do not work.** No OCR, so image-only PDFs return nothing useful.
- **Tables can break.** PDF table text often loads in a messy order.
- **One contract at a time.** No comparison across multiple documents.
- **No automated evaluation yet.** Quality is checked by hand and through traces.
- **Not legal advice.** The output can be wrong. Always check the cited page yourself.
- **Data goes to OpenAI.** Do not upload confidential contracts unless that is allowed.

---

## Future Improvements

- Add OCR for scanned contracts.
- Add a re-ranker after retrieval.
- Add an evaluation set with questions and correct answers to measure accuracy.
- Support multiple contracts and comparison between them.
- Better table handling.

---

## Disclaimer

This project is for learning and demonstration. It does not give legal advice.

## Author

**Abdullah Kamal**
GitHub: [AbdullahKamal9](https://github.com/AbdullahKamal9)
LinkedIn: [abdullah-kamal](https://linkedin.com/in/abdullah-kamal-854a59375/)
