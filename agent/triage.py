from hindsight_client import Hindsight


BANK_ID = "sentinel-memory-demo"


def get_memory_text(memory):
    return memory.text.lower()


def analyze_memories(memories):
    """
    Turn Hindsight's retrieved historical memories into
    an operational triage recommendation.
    """

    all_text = "\n".join(get_memory_text(m) for m in memories)

    has_previous_incident = (
        "inc-240108-001" in all_text
        and "inc-240226-014" in all_text
    )

    has_schema_failure = (
        "schemamismatch" in all_text
        or "schema mismatch" in all_text
        or "schema-mismatch" in all_text
    )

    has_previous_fix = (
        "successful fix" in all_text
        or "fix applied" in all_text
        or "compatibility" in all_text
    )

    has_postmortem_action = (
        "act-240108-01" in all_text
        or "postmortem action" in all_text
    )

    has_incomplete_prevention = (
        "never merged" in all_text
        or "not been merged" in all_text
        or "had not been merged" in all_text
    )

    print()
    print("========================================")
    print("SENTINEL MEMORY - TRIAGE RESULT")
    print("========================================")
    print()

    print("RECURRENCE ASSESSMENT")
    print("---------------------")

    if has_previous_incident and has_schema_failure:
        print(
            "Historical memory shows that this incident belongs "
            "to the same schema-compatibility failure family as "
            "a previous daily_sales_agg incident."
        )
    else:
        print(
            "No strong historical recurrence evidence was found."
        )

    print()
    print("RELATED HISTORY")
    print("----------------")

    if has_previous_incident:
        print(
            "INC-240108-001 and INC-240226-014 are the relevant "
            "historical incidents retrieved from Hindsight."
        )
    else:
        print(
            "No closely related historical incident was identified."
        )

    print()
    print("PREVIOUS FIX")
    print("------------")

    if has_previous_fix:
        print(
            "Historical memory shows that the earlier incident "
            "was resolved by allowing additive nullable fields "
            "in the contract and replaying the affected partition."
        )
    else:
        print("No previous fix was confidently identified.")

    print()
    print("POSTMORTEM FOLLOW-UP")
    print("--------------------")

    if has_postmortem_action:
        print(
            "Hindsight retrieved postmortem action ACT-240108-01: "
            "add compatibility tests for additive nullable fields "
            "to the raw_orders contract CI."
        )

        if has_incomplete_prevention:
            print(
                "Historical evidence indicates that this prevention "
                "action had not been merged before the later incident."
            )
        else:
            print(
                "The retrieved memories do not establish that the "
                "prevention action was incomplete."
            )
    else:
        print("No related postmortem action was found.")

    print()
    print("RECOMMENDED NEXT STEP")
    print("---------------------")

    if has_previous_incident and has_postmortem_action:
        print(
            "Check repository and deployment history for the "
            "compatibility-test prevention action before applying "
            "another narrowly scoped schema patch."
        )
    else:
        print(
            "Investigate the current schema contract and compare "
            "it with historical incident evidence."
        )

    print()
    print("========================================")
    print("HINDSIGHT MEMORIES RETRIEVED")
    print("========================================")

    for memory in memories:
        print(f"[{memory.type}] {memory.text}")


def main():

    print()
    print("========================================")
    print("SENTINEL MEMORY")
    print("========================================")
    print()
    print("Enter the new incident details.")
    print()

    incident_id = input("Incident ID: ")
    pipeline = input("Pipeline: ")
    service = input("Service: ")
    error_class = input("Error class: ")
    symptom = input("Symptom: ")

    query = f"""
Find historical production incidents relevant to this new incident.

NEW INCIDENT
Incident ID: {incident_id}
Pipeline: {pipeline}
Service: {service}
Error class: {error_class}
Symptom: {symptom}

Find memories involving:
- similar incidents
- previous fixes
- recurring failure patterns
- postmortem actions
- prevention work
- evidence about whether prevention was completed

Prioritize the most relevant historical memories.
"""

    print()
    print("Searching Hindsight memory...")
    print()

    with Hindsight(base_url="http://localhost:8888") as client:

        results = client.recall(
            bank_id=BANK_ID,
            query=query,
        )

        if not results:
            print("No historical memories were found.")
            return

        analyze_memories(results)


if __name__ == "__main__":
    main()