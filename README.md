# Sentinel Memory

> An on-call incident agent that remembers every past pipeline failure and postmortem commitment, so recurring failures become progressively easier to diagnose and resolve.

## Overview

Sentinel Memory is an incident-response agent for recurring production and data-pipeline failures.

Instead of treating every incident as a completely new problem, the agent uses **Hindsight** to remember historical incidents, previous fixes, postmortem actions, and recurring failure patterns.

When a similar incident happens again, Sentinel Memory retrieves the relevant history and uses it to produce a more informed triage recommendation.

## What This Demonstrates

The key idea is simple:

**Without memory:**  
A new incident receives a generic diagnosis based only on the information provided.

**With Hindsight memory:**  
The agent can recognize a recurring failure, retrieve previous incidents, identify what fixed the problem before, and check whether the preventive postmortem action was actually completed.

This makes memory the central part of the agent rather than an optional feature.

## Architecture

```text
                 New Incident
                      |
                      v
              Sentinel Memory
                 Python Agent
                      |
                      v
             Hindsight API
              localhost:8888
                      |
          +-----------+-----------+
          |                       |
          v                       v
       Recall                  Memory
      history                  store
          |
          v
   Triage recommendation

Hindsight UI:
localhost:9999
````

## Hindsight Integration

Sentinel Memory uses the official Hindsight memory system.

Hindsight stores and connects information about:

* Past incidents
* Root causes
* Successful fixes
* Postmortem actions
* Evidence about whether preventive actions were completed
* Recurring failure patterns

The Python application communicates with Hindsight through its API using the `hindsight-client` package.

The agent primarily uses Hindsight **recall** during live triage.

## Demonstration Scenario

The demonstration uses a recurring `daily_sales_agg` Airflow pipeline failure.

A new incident reports:

```text
Pipeline: daily_sales_agg
Service: Airflow
Error class: SchemaMismatch

Symptom:
Daily aggregate failed after raw_orders added a nullable column.
```

Hindsight retrieves historical incidents including:

* `INC-240108-001`
* `INC-240226-014`

The agent can then identify:

1. This is part of the same schema-compatibility failure family.
2. A previous successful fix allowed additive nullable fields and replayed the affected partition.
3. A previous postmortem called for compatibility tests.
4. Historical evidence indicated that the preventive compatibility-test change had not been merged before the later recurrence.
5. The next step should therefore include checking the prevention mechanism before applying another narrowly scoped patch.

This is the key behavior change produced by memory.

## Dataset

The project uses a synthetic dataset of production-style pipeline incidents.

Dataset:

```text
data/incidents.json
```

The dataset contains 14 incidents across several organizations and pipeline systems.

It includes recurring and non-recurring incidents so that the agent can distinguish between:

* Genuine recurring failures
* Related incidents with different root causes
* False positives
* Previously resolved problems
* Incomplete preventive actions

## Project Structure

```text
sentinel-memory/
|
+-- agent/
|   +-- triage.py
|
+-- data/
|   +-- incidents.json
|
+-- memory/
|   +-- seed.py
|   +-- test_recall.py
|
+-- test_memory.py
|
+-- requirements.txt
+-- README.md
```

## Requirements

* Windows, macOS, or Linux
* Python 3.12+
* Docker Desktop
* Hindsight
* Groq API key
* Git

## Running Hindsight

Pull and run the official Hindsight image:

```powershell
docker run -d `
  --name hindsight `
  -p 8888:8888 `
  -p 9999:9999 `
  -v hindsight-data:/home/hindsight/.pg0 `
  -e HINDSIGHT_API_LLM_PROVIDER=groq `
  -e HINDSIGHT_API_LLM_API_KEY="YOUR_GROQ_API_KEY" `
  -e HINDSIGHT_API_LLM_MODEL="openai/gpt-oss-120b" `
  -e HINDSIGHT_API_LLM_GROQ_SERVICE_TIER=on_demand `
  ghcr.io/vectorize-io/hindsight:latest
```

Hindsight API:

```text
http://localhost:8888
```

Hindsight UI:

```text
http://localhost:9999
```

## Python Environment

Create a virtual environment with Python 3.12:

```powershell
uv python install 3.12
uv venv --python 3.12
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
uv pip install hindsight-client
```

## Environment Variables

Set the Hindsight LLM configuration:

```powershell
$env:HINDSIGHT_API_LLM_PROVIDER="groq"
$env:HINDSIGHT_API_LLM_API_KEY="YOUR_GROQ_API_KEY"
$env:HINDSIGHT_API_LLM_MODEL="openai/gpt-oss-120b"
$env:HINDSIGHT_API_LLM_GROQ_SERVICE_TIER="on_demand"
```

Do not commit API keys to GitHub.

## Seeding Memory

Historical incidents can be stored in Hindsight using:

```powershell
python memory/seed.py
```

The seed script prepares historical incident information and stores it in the Hindsight memory bank.

## Running the Agent

Start the interactive triage agent:

```powershell
python agent/triage.py
```

Enter a new incident when prompted.

Example:

```text
Incident ID: INC-DEMO-002
Pipeline: daily_sales_agg
Service: Airflow
Error class: SchemaMismatch
Symptom: Daily aggregate failed after raw_orders added a nullable column
```

The agent retrieves relevant historical memories from Hindsight and produces a triage analysis.

## Memory Demonstration

The most important part of the demo is showing the difference between an agent with and without memory.

### Without Memory

The agent sees only:

```text
daily_sales_agg failed
SchemaMismatch
nullable column was added
```

It can suggest a generic schema compatibility investigation.

### With Hindsight Memory

The agent can retrieve historical context such as:

```text
INC-240108-001
INC-240226-014
ACT-240108-01
```

It can connect the current incident to previous failures and recommend checking whether the previous preventive action was actually implemented.

The agent therefore moves from:

```text
"What could be wrong?"
```

toward:

```text
"Have we seen this before, what fixed it, and did we actually prevent it?"
```

## Hindsight Memory UI

Hindsight's UI makes the stored memory visible.

The Sentinel Memory demonstration shows:

* Historical memories
* Relationships between memories
* Semantic connections
* Temporal relationships
* Entity relationships
* Causal relationships
* Incident and postmortem information

The memory graph provides a visual representation of the accumulated incident knowledge.

## Current Prototype Limitations

This is a prototype focused on demonstrating the value of persistent incident memory.

Current limitations include:

* The triage reasoning layer is still partly rule-based.
* The prototype currently focuses primarily on Hindsight recall.
* The synthetic dataset is relatively small.
* Production integrations such as ServiceNow and CloudWatch are not yet connected.
* Preventive-action verification would benefit from direct integration with source-control and deployment systems.

These limitations are intentional boundaries of the current prototype rather than claims of production readiness.

## Future Work

Potential next steps include:

* ServiceNow integration for incident creation and lookup
* CloudWatch log retrieval
* Automatic postmortem tracking
* Git/Bitbucket verification of preventive fixes
* More sophisticated incident similarity detection
* Automated incident timelines
* Continuous memory updates from production incidents
* Stronger reasoning over completed versus incomplete postmortem actions
* Evaluation against a larger incident dataset

## Why I Built Sentinel Memory

I work with incident creation and support for production and data-pipeline systems.

A recurring part of incident response is investigating failures, checking previous incidents, looking at previous fixes, and determining whether a preventive action was actually completed.

That led to a simple question:

> What if the incident agent could remember all of that automatically?

Sentinel Memory explores that idea by making persistent memory the core of incident triage.

The goal is not to build an agent that knows everything.

The goal is to build an agent that **doesn't make us forget what we've already learned.**

## Built With

* Python
* Hindsight
* Hindsight Client
* Groq
* Docker
* Airflow incident concepts
* Synthetic production-style incident data

## Hindsight

Official documentation:

[https://hindsight.vectorize.io/](https://hindsight.vectorize.io/)

Official GitHub repository:

[https://github.com/vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)

Hindsight UI:

[https://ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io)


