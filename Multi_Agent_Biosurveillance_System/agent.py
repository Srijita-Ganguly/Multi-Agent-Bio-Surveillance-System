#Importation
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents import Agent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from typing import Any, Dict, List
from google.adk.tools import load_memory, preload_memory
from google.adk.memory import InMemoryMemoryService
from google.adk.tools.agent_tool import AgentTool
import requests
from google.adk.plugins.logging_plugin import (LoggingPlugin,)
import asyncio
import os
import re
from dotenv import load_dotenv
import os

load_dotenv()

#Configure Retry Options
#When working with LLMs, you may encounter transient errors like rate limits or temporary service unavailability. Retry options automatically handle these failures by retrying the request with exponential backoff.
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

#Setup the API Keys
serper_api_key = os.getenv("SERPER_API_KEY")
NCBI_api_key = os.getenv("NCBI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 1. RAW NEWS COLLECTION
def get_disease_outbreak_news(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Fetch news from Serper.dev News API.
    This function has an ADK-safe signature: only primitive input args.
    """

# 🔑 Use your Serper API key
    api_key = serper_api_key

# 🧾 Query payload (what you are asking the news API to search for)
    url = "https://google.serper.dev/news"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

# 📡 Send POST request to Serper API to get the news articles
    response = requests.post(url, headers=headers, json=payload)

# ❌ Error handling: if API fails, print status and return empty list
    if response.status_code != 200:
        print(f"News failed ({response.status_code}): {response.text}")
        return []

    data = response.json()

# 🧩 Extract the "news" list and limit to the requested number of results
    articles = data.get("news", [])[:num_results]

# 📦 Build a simplified, clean list of article dictionaries
    return [
        {
            "title":   item.get("title"),
            "link":    item.get("link"),
            "snippet": item.get("snippet"),
            "source":  item.get("source"),
        }
        for item in articles
    ]

# 2. FILTERED OUTBREAK NEWS FUNCTION
def disease_outbreak_news(query: str) -> List[Dict[str, str]]:
    """
    Fetch current microbial or viral outbreak news using the Serper News API.
    Applies filtering for emerging infectious disease–related content.

    Returns:
        List[Dict[str, str]]
    """

# 📰 First, get the raw news articles using the function above
    raw_news = get_disease_outbreak_news(query)

# 🧬 Keywords to identify outbreak-related stories
    outbreak_keywords = [
        "virus", "bacteria", "fungus", "fungal",
        "prion", "parasite",
        "outbreak", "cluster", "disease",
        "epidemic", "pandemic",
        "infection", "infectious", "news",
        "pathogen", "case count",
    ]

# 🔍 Evaluate each article to check for outbreak-related keywords
    filtered = []
    for item in raw_news:
        text = f"{item['title']} {item['snippet']}".lower()

        if any(keyword in text for keyword in outbreak_keywords):
            filtered.append(item)

# 📤 Return only the filtered outbreak-related articles
    return filtered

#1. RESEARCH PAPERS COLLECTION AND FILTERING
def get_pubmed_papers(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch research papers from PubMed.
    Applies filtering for infectious disease–related content.
    """

# 🔑 NCBI API key for PubMed E-utilities access
    api_key = NCBI_api_key

# 🧾 Search parameters:

    #    - term=query          → your input search query
    #    - retmax=max_results  → max number of IDs to return
    #    - retmode="json"      → request JSON response

    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "api_key": api_key,
        "retmode": "json"
    }

# 📡 Send the search request
    search_response = requests.get(search_url, params=search_params)
    ids = search_response.json().get("esearchresult", {}).get("idlist", [])

# ❌ No IDs returned → no papers found, return empty list
    if not ids:
        return []

# 🧾 parameters:
    #    - db="pubmed"       → get from PubMed database
    #    - id="comma list"   → get multiple IDs at once
    #    - retmode="xml"     → efetch returns XML

    get_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    get_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
        "api_key": api_key
    }

  # 📡 Send the fetch request for full article details
    get_response = requests.get(get_url, params=get_params)

# 📦 Parse returned XML with BeautifulSoup
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(get_response.text, "xml")

    papers = []
    for article in soup.find_all("PubmedArticle"):

      # 🏷️ Title (if available)
        title = article.ArticleTitle.text if article.ArticleTitle else None

      # 📝 Abstract (may be missing)
        abstract = (
            article.Abstract.AbstractText.text
            if article.Abstract and article.Abstract.AbstractText
            else None
        )

      # 📰 Journal name
        journal = (
            article.Journal.Title.text
            if article.Journal and article.Journal.Title
            else None
        )

      # 👥 Author list extraction (first + last names)
        authors = []
        for author in article.find_all("Author"):
            first = author.ForeName.text if author.ForeName else ""
            last = author.LastName.text if author.LastName else ""
            if first or last:
                authors.append(f"{first} {last}")

      # 🔗 DOI identifier
        doi_tag = article.find("ArticleId", {"IdType": "doi"})
        doi = doi_tag.text if doi_tag else None

      # 📄 Append paper metadata to list
        papers.append(
            {
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "authors": authors,
            }
        )

# 📤 Return the list of processed papers
    return papers

# NEWS ON INFECTIOUS DISEASES

# Create an LLM-powered agent that analyzes infectious-disease news
news_surveillance_agent = LlmAgent(
    name="newssurveillanceagent",        # 🔹 Unique agent name (used internally in ADK)
    model=Gemini(
        model="gemini-2.5-flash-lite",   # ⚡ Lightweight, fast Gemini model for surveillance tasks
        retry_options=retry_config       # 🔁 Retry logic for API robustness
    ),

    instruction="""
You are the **NEWS Surveillance Analyzer (SP)**.
Your only job is to generate a short, data-driven Surveillance Report using the 'disease_outbreak_news' tool.

---

# OUTPUT FORMAT (MANDATORY — NO EXCEPTIONS)

### 1. Threat Assessment
State the current risk level (LOW / MODERATE / HIGH) and give one short justification.

### 2. Epidemic Trends
Summarize key indicators such as trend direction.
Do not invent values not present in the data.

### 3. Geographic Distribution
List the relevant hotspots or monitored regions based strictly on the provided data.

### 4. References
"references": [
       {
          "title": "...",
          "link": "...",
          "source": "..."
       }
  ]

---

# RULES
- Do not invent data.
- Include ALL article links from the tool output in "references".
- Use ONLY the simulated data given in the prompt.
- Do NOT add, guess, or extrapolate new statistics.
- No external assumptions.
- Keep the report concise, factual, and neutral.

""",

# These tools allow the agent to collect and filter real news articles
    tools=[disease_outbreak_news, get_disease_outbreak_news]
)

#A. RESEARCH PAPER FINDER

# Create an LLM-powered agent for collecting research papers from PubMed
research_paper_finder_agent = LlmAgent(
    name="paperingestion",              # 🔹 Unique agent name for internal tracking
    model=Gemini(
        model="gemini-2.5-flash-lite",  # ⚡ Lightweight Gemini model for fast response
        retry_options=retry_config),    # 🔁 Retry logic to handle transient API failures
    instruction="""
        You are a research paper ingestion agent.
        Use the get_pubmed_papers tool whenever the user requests:
        - research papers
        - PubMed articles
        - biomedical literature
        - research work
        - recent research
        Return structured metadata (DOI, title, authors, abstract, journal).
        If full text is requested, explain whether full text is available via PubMed or must be accessed externally.
    """,

# Only the `get_pubmed_papers` tool is available, so the agent can retrieve PubMed research papers as requested.
    tools=[get_pubmed_papers],

# Defines the key under which the agent’s structured response is stored.
    output_key="paper_metadata"
)

#B. RESEARCH EXTRACTOR

# Create an LLM-powered agent to extract structured information from research paper metadata retrieved by the research_paper_finder_agent.
research_extractor_agent = LlmAgent(
    name="researchextractor",         # 🔹 Unique name for internal tracking
    model=Gemini(
        model="gemini-2.5-flash-lite",# ⚡ Lightweight model suitable for extraction tasks
        retry_options=retry_config),  # 🔁 Retry logic to handle transient failures
    instruction="""
    Using the output of 'paper_metadata'
    Extract structured fields:
    - DOI
    - pathogen
    - variant
    - virulence_factor
    - gene_or_protein
    - mechanism
    - mutations
    - evidence_strength
    - date
    Format output as JSON list.

    # OUTPUT FORMAT (MANDATORY — NO EXCEPTIONS)
[
  {
    "doi": "...",
    "pathogen": "...",
    "variant": "...",
    "virulence_factor": "...",
    "gene_or_protein": "...",
    "mechanism": "...",
    "mutations": "...",
    "evidence_strength": "...",
    "date": "...",
    "reference": {
         "doi": "..."
    }
  }
]

• Ensure the DOI is always included inside "reference".
    """,
)

# Note: No additional tools are required, this agent works purely on the metadata produced by the previous agent.

#C. BIOSURVEILLANCE

# Create a SequentialAgent that chains multiple agents together
# This agent performs a complete biosurveillance workflow:
# 1️⃣ Collect research papers
# 2️⃣ Extract structured pathogen-related information
bio_surveillance_agent = SequentialAgent(
    name="biosurveillanceagent",            # 🔹 Unique name for internal tracking
    sub_agents=[
        research_paper_finder_agent,        # Step 1: Get PubMed research papers
        research_extractor_agent,           # Step 2: Extract structured information from papers
    ]
)

# AGGREGATION OF THE NEWS AND RESEARCH OUTPUTS

# Create an LLM-powered agent that fuses outputs from news and research pipelines
data_aggregator_agent = LlmAgent(
    name="dataaggregatoragent",            # 🔹 Unique agent name for tracking
    model=Gemini(
        model="gemini-2.5-flash-lite",     # ⚡ Lightweight model suitable for summarization and fusion tasks
        retry_options=retry_config         # 🔁 Retry logic for robustness
    ),

    instruction="""
You are the Fusion Intelligence Agent.

You will receive:
- news_surveillance_output
- bio_surveillance_output

Your job is to integrate these into a unified analytic snapshot.

────────────────────────────────────────
FUSION TASKS (MANDATORY)
────────────────────────────────────────
1. Aggregate both inputs into a single, concise summary:
    • Key pathogen(s)
    • Relevant mutations or molecular signals
    • Outbreak regions or clusters
    • CRITICAL: Any apparent correlation between surveillance and research literatures

2. Apply the RISK ENGINE (rules below).

────────────────────────────────────────
RISK ENGINE RULES
────────────────────────────────────────
Assign a HIGH / MODERATE / LOW risk score:

- HIGH if:
    • surveillance mentions "rapid spread", "cluster expansion", or
    • molecular evidence includes "increased transmissibility",
      "immune escape", or "high-impact mutation".

- MODERATE if:
    • surveillance reports emerging but contained outbreaks OR
    • literature indicates mutations of uncertain significance.

- LOW if:
    • minimal surveillance signals AND
    • no concerning molecular factors.

────────────────────────────────────────
FUSION REQUIREMENTS
────────────────────────────────────────
1. Create a single concise analytic summary.
2. Apply the Risk Engine.
3. Aggregate ALL references:
    • News article links from surveillance
    • DOIs from molecular papers

────────────────────────────────────────
OUTPUT FORMAT (STRICT)
────────────────────────────────────────
{
  "fusion_summary": "...",
  "risk_level": "HIGH | MODERATE | LOW",
  "justification": "...",
  "references": {
        "news_articles": [
             {"title": "...", "link": "...", "source": "..."}
        ],
        "research_articles": [
             {"doi": "..."}
        ]
  }
}

────────────────────────────────────────
RULES:
• Do not fabricate references.
• Only use references passed by prior agents.
• Keep the summary concise.
""",
)

#THE FUSION PIPELINE — SEQUENTIAL AGENT

# Chain the agents into a complete fusion pipeline:
# 1️⃣ news_surveillance_agent → collects outbreak news
# 2️⃣ bio_surveillance_agent → collects and extracts structured research data
# 3️⃣ data_aggregator_agent → integrates outputs and produces a unified analytic snapshot

fusion_pipeline = SequentialAgent(
    name="fusion_pipeline",
    sub_agents=[
        news_surveillance_agent,      # existing surveillance agent
        bio_surveillance_agent,    # existing molecular evidence pipeline
        data_aggregator_agent                 # fusion layer
    ]
)

# THE MAIN ORCHESTRATOR: THE CHATBOT
root_agent = LlmAgent(
    name="InteractingAgent",              # 🔹 Unique root agent name
    model=Gemini(
        model="gemini-2.5-flash-lite",    # ⚡ Lightweight, fast model for orchestration
        retry_options=retry_config        # 🔁 Retry logic for API robustness
    ),

    instruction="""
You are the Pandemic Surveillance & Molecular-Evidence Orchestrator.

Your responsibilities are strictly limited to:
    (1) Providing optional high-level surveillance context on request
    (2) Extracting molecular evidence from scientific literature

────────────────────────────────────────────
SURVEILLANCE REQUEST ROUTING
────────────────────────────────────────────
If the user explicitly asks for:
    • surveillance
    • outbreak signals
    • global monitoring
    • epidemic situation
    • risk level
    • current news
    • latest information

Then you MUST immediately call the tool:
    news_surveillance_agent
and pass the entire user query as the input.

────────────────────────────────────────────
MOLECULAR-EVIDENCE ROUTING
────────────────────────────────────────────
If the user message contains ANY of the following words:
    virulence, virulence factor, mutation, variant,
    gene, protein, genomic, molecular, mechanism,
    sequence, strain, evidence, research,

Then you MUST immediately call the tool:
    bio_surveillance_agent
and pass the entire user query as the input.

────────────────────────────────────────────
FUSION ROUTING
────────────────────────────────────────────
If the user requests BOTH:
    • surveillance context
AND
    • molecular evidence

Then call the tool:
    fusion_pipeline

────────────────────────────────────────────
OUT OF SCOPE
────────────────────────────────────────────
If the query does not involve:
    • surveillance/outbreak context OR
    • molecular evidence

Respond ONLY with:

    "Hello! I am your research assistant. I can assist you with current surveillance reports and molecular-evidence analysis related to emerging or known diseases."

────────────────────────────────────────────
SAFETY
────────────────────────────────────────────
Never give wet-lab steps, genetic engineering instructions,
experimental workflows, or anything operational.
Only high-level summaries of published literature or simulated data.
""",

# These are wrapped sub-agents, enabling routing based on user intent:
    tools=[
        AgentTool(agent=news_surveillance_agent),
        AgentTool(agent=bio_surveillance_agent),
        AgentTool(agent=fusion_pipeline)
    ]
)