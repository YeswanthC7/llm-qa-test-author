import json, glob, statistics, sys

runs = [json.load(open(p)) for p in glob.glob("pytest_run*.json")]
durations = [r["duration"] for r in runs]
fails     = sum(r["failed"] for r in runs)

print("── Flakiness summary ──")
print(f" total failures across 3 runs : {fails}")
print(f" avg  duration                : {statistics.mean(durations):.2f}s")
print(f" stdev duration               : {statistics.stdev(durations):.2f}s" if len(durations) > 1 else "")
if fails:
    sys.exit(1)          # mark job red if flaky
