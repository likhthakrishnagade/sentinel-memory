import json
import time
from pathlib import Path

from hindsight_client import Hindsight


client = Hindsight(base_url="http://localhost:8888")

BANK_ID = "sentinel-memory-demo"
DATA_FILE = Path(__file__).parent.parent / "data" / "incidents.json"

# These incidents form the strongest recurring schema-failure story.
SELECTED_INCIDENTS = [
    "INC-240108-001",
    "INC-240226-014",
    "INC-240311-006",
    "INC-250819-003",
    "INC-251119-021",
]


def incident_to_memory(incident):
    error = incident.get("error", {})
    recovery = incident.get("recovery", {})

    actions = "\n".join(
        f"- {a['action_id']}: {a['description']} "
        f"| status={a['status']} | owner={a['owner']}"
        for a in incident.get("postmortem_actions", [])
    )

    related = "\n".join(
        f"- {r['incident_id']}: {r['relationship']}"
        for r in incident.get("related_incidents", [])
    )

    evidence = "\n".join(
        f"- {e['source']}: {e['observation']} "
        f"(confidence={e['confidence']})"
        for e in incident.get("evidence", [])
    )

    return f"""
Production incident: {incident['incident_id']}
Occurred: {incident['occurred_at']}

Organization: {incident['organization']}
Pipeline: {incident['pipeline']}
Service: {incident['service']}
Severity: {incident['severity']}

SYMPTOM:
{incident['symptom']}

ERROR:
Class: {error.get('class')}
Fingerprint: {error.get('fingerprint')}
Message: {error.get('message')}

ROOT CAUSE:
{incident['root_cause']}

SUCCESSFUL FIX:
{incident.get('successful_fix')}

RECOVERY:
{recovery.get('method')}

RELATED INCIDENTS:
{related or "None"}

POSTMORTEM ACTIONS:
{actions or "None"}

EVIDENCE:
{evidence or "None"}
"""


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    incidents_by_id = {
        incident["incident_id"]: incident
        for incident in dataset["incidents"]
    }

    print("========================================")
    print("Sentinel Memory - Hindsight Seeding")
    print("========================================")
    print(f"Bank: {BANK_ID}")
    print()

    for index, incident_id in enumerate(SELECTED_INCIDENTS, start=1):
        incident = incidents_by_id[incident_id]

        print(
            f"[{index}/{len(SELECTED_INCIDENTS)}] "
            f"Storing {incident_id}..."
        )

        client.retain(
            bank_id=BANK_ID,
            content=incident_to_memory(incident),
            context="production pipeline incident and postmortem history",
        )

        print(f"    Stored {incident_id}")

        # Give the Groq token window time to reset between requests.
        if index < len(SELECTED_INCIDENTS):
            print("    Waiting 15 seconds before next memory...")
            time.sleep(15)

    print()
    print("========================================")
    print("Sentinel Memory seeding complete.")
    print(f"Memories attempted: {len(SELECTED_INCIDENTS)}")
    print(f"Hindsight bank: {BANK_ID}")
    print("========================================")


if __name__ == "__main__":
    main()