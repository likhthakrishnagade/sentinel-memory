from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

results = client.recall(
    bank_id="sentinel-memory-demo",
    query=(
        "Have we seen recurring schema compatibility failures in the "
        "daily_sales_agg pipeline? What happened before, what was fixed, "
        "and what postmortem prevention work was recorded?"
    ),
    budget="high",
)

print("\n========================================")
print("SENTINEL MEMORY - RECALL TEST")
print("========================================\n")

print(results)