from hindsight_client import Hindsight

client = Hindsight(
    base_url="http://localhost:8888"
)

BANK_ID = "sentinel-memory"


print("1. Storing incident memory...")

client.retain(
    bank_id=BANK_ID,
    content="""
    Incident INC-001:
    The customer_orders_daily pipeline failed because the S3 IAM policy
    denied access to the required bucket.

    The engineer fixed the issue by updating the IAM policy.

    Postmortem commitment:
    Update the pipeline IAM policy permanently so this failure does not recur.
    """,
    context="production incident and postmortem"
)

print("Memory stored.")


print("\n2. Recalling related incidents...")

results = client.recall(
    bank_id=BANK_ID,
    query="customer orders pipeline S3 IAM permission failure",
)

print("\nRecall results:")
print(results)

print("\nSentinel Memory test complete.")