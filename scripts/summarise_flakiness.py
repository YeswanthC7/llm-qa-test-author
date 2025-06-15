import json, glob, statistics, sys

runs = [json.load(open(p)) for p in glob.glob("pytest_run*.json")]
fails = [r["failed"] for r in runs]
dur   = [r["duration"] for r in runs]

print("── Flakiness summary ──")
print(f" total failures across 3 runs : {sum(fails)}")
print(f" avg  duration                : {statistics.mean(dur):.2f}s")

# fail job *only* if results are inconsistent (some runs pass, others fail)
if len(set(fails)) > 1:
    print("Tests are flaky ❌")
    sys.exit(1)
print("No flakiness detected ✅")
