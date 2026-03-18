import argparse
from datetime import datetime, timezone

def collect_evidence(mode, period=None):
    print(f"Collecting evidence in {mode} mode for period {period}")
    return {"generated_at": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="sprint")
    parser.add_argument("--period", default=None)
    args = parser.parse_args()
    collect_evidence(args.mode, args.period)
