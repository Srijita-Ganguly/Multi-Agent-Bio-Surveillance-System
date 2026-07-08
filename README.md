# Multi-Agent Bio-Surveillance System
*Gemini-driven multi-agent system that monitors global health signals and scientific insights to detect outbreaks and flag emerging threats.*
### Run the Notebook
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/Srijita-Ganguly/Multi-Agent-Bio-Surveillance-System/blob/main/Multi_Agent_Bio_Surveillance_System.ipynb)

---------------------------------------------------------------------------------------------------------------------------------------------------------
## Demo Video

Watch the demo of the Multi-Agent Bio-Surveillance System in action on the GoogleADK Web UI.
The main demo starts at 1:50, where the agent begins answering the user's queries related to news and research on disease outbreaks.
[![Watch the Demo](https://img.youtube.com/vi/VooSqpvJVOs/hqdefault.jpg)](https://www.youtube.com/watch?v=VooSqpvJVOs)

## PROJECT OVERVIEW: 
This is a multi-agent bio-surveillance system powered by Gemini containing sequential workflow with custom tools to scan real-time news and research publications, and to extract the critical information of the emerging pathogens.
Implementing such multi-agent system enables government, researchers, and healthcare systems to respond faster by developing counter measures and significantly reduce the risk of future outbreaks escalating into global pandemics.

## PRACTICAL IMPACT:
By correlating real-time news signals with peer-reviewed scientific literature, this system forms an intelligent early-warning engine for infectious disease threats. Its agent design, sequential workflow, custom tools, sessions, and observability establish a robust, and transparent bio-surveillance platform capable of supporting data-driven public-health intelligence. This multi-agent system holds the potential for monitoring future disease outbreaks.

<img width="994" height="560" alt="Workflow" src="https://github.com/user-attachments/assets/98eeb724-05b5-48b6-8eed-e3acb0749a87" />

## SYSTEM ARCHITECTURE OVERVIEW: 
This Multi-Agent Bio-Surveillance System implements LLM-driven architecture that integrates specialized agents to provide continuous monitoring, analysis, and synthesis of infectious disease intelligence. It is built using the Google ADK, the system combines real-time data ingestion, scientific literature mining, structured reasoning pipelines, and orchestration to deliver automated early-warning insights for emerging health threats.

The following are the key features this system includes,

**1. LLM Driven Multi-Agent Design:** A set of domain specific agents including news_surveillance_agent, bio_surveillance_agent and root_agent execute specialized roles across news scanning, literature retrieval, information extraction, reasoning, and final reporting.

**2. Sequential Multi-Agent Orchestration:** A layered processing pipeline coordinates the agents in sequence for increasingly refined analysis. The bio_surveillance_agent combines paper-finding and information-extraction roles, while the fusion_pipeline chains news surveillance, literature analysis, and data aggregation. Each step builds on outputs from the previous one, enabling structured processing.

**3. Integration of Custom Data-Retrieval Tools:** Agents access external data sources through custom python tools, including real-time outbreak news collector and PubMed search functions. These tools enable targeted retrieval from the Serper.dev News and NCBI PubMed, for verified, up-to-date data.

**4. Session & State Management:** Short-term conversational memory is handled via InMemorySessionService, allowing agents to recognize and respond to ongoing context within a session, this enables natural follow-up queries.

**5. Context Engineering:** Each LLM Agent is designed with detailed instructions (prompts) that define its persona, responsibilities, and expected output format. These structured prompts ensure consistent behavior, and maintain strict formats such as standardized surveillance reports and well-structured JSON summaries which ensures their performance on handling specific tasks accurately and adhere to predefined rules and output structures.

**6. Observability:** Through LoggingPlugin integration, every agent invocation, tool call, and LLM exchange is recorded. This enables deep visibility into decision paths, supports debugging, and provides accountability across complex multi-agent interactions.

## Installation
### 1. Clone the repository

```bash
git clone https://github.com/Srijita-Ganguly/Multi-Agent-Bio-Surveillance-System.git
cd Multi_Agent_Biosurveillance_System
```

### 2. Create a virtual environment (recommended)

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file inside the agent package directory and add the following:

```text
GOOGLE_API_KEY=your_google_ai_api_key
SERPER_API_KEY=your_serper_api_key
NCBI_API_KEY=your_ncbi_api_key
```

### 5. Start the application

From the project root, launch the ADK Web UI:

```bash
adk web
```

After the server starts, open the local URL displayed in the terminal (typically `http://127.0.0.1:8000`) in your browser.

## Using the Application

The application is an AI-powered biosurveillance assistant that combines real-time outbreak news with scientific literature from PubMed.

Users can interact with the application using natural language. No special commands are required.

### Example Queries

#### Disease Surveillance

* Show the latest H5N1 outbreak news.
* What are the current dengue outbreaks?
* Provide the latest surveillance report for Nipah virus.

#### Scientific Literature

* Find recent PubMed papers on H5N1.
* Show recent research on antimicrobial resistance.
* Retrieve molecular evidence for SARS-CoV-2 variants.

#### Combined Surveillance + Research

* Give me the latest H5N1 outbreak together with recent molecular evidence.
* Summarize current mpox surveillance and recent scientific findings.
* Provide both surveillance data and PubMed evidence for Ebola virus.

### Output

Depending on the request, the application returns:

* Current outbreak news
* Threat assessment
* Geographic distribution
* PubMed research papers
* Molecular evidence extracted from literature
* Integrated surveillance and research summary
* References with news links and DOI information

## Notes

* A valid Google AI API key is required.
* A Serper API key is required for news retrieval.
* An NCBI API key is recommended for higher PubMed request limits.
* Internet connectivity is required for retrieving live news and scientific literature.
* If the Gemini API returns a **503 UNAVAILABLE** error, it indicates temporary service overload from the API provider. Retry the request after a short delay.

## Workflow in Google Colab: 
To run the Jupyter Notebook without installing anything locally, open it directly in Google Colab:

🔗 **Google Colab Link:**  
https://colab.research.google.com/github/Srijita-Ganguly/Multi-Agent-Bio-Surveillance-System/blob/main/Multi_Agent_Bio_Surveillance_System.ipynb

## Limitations and Future Improvements
**1. Memory (Long Term Memory) Addition:** The system lacks persistent memory, limiting continuity across interactions. Integrating scalable memory would enhance contextual understanding.

**2. Enhancing Context Engineering:** Sometime queries expose gaps in adaptive response, indicating the need for improved context-handling.

**3. Agent Evaluation Incorporation:** A comprehensive evaluation framework to ensure reliability and consistent agent performance across diverse scenarios.

### *Acknowledgement*
My sincere thanks to Kaggle × Google for the 5-Day Agents Intensive Course. The knowledge gained enabled me to develop this system to help monitor emerging infectious diseases and support responsible outbreak mitigation.
Debugging and code review were completed with the assistance of OpenAI's ChatGPT.
