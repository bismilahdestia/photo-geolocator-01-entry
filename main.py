#!/usr/bin/env python3
"""photo-geolocator-01 entry: code-only prior guess, no model calls.

No Anthropic/OpenAI key is available to this entry, so every photo is placed
with the same fixed prior: the point on Earth that minimises the total
haversine error over the kit's 75 practice photos (lat 56.80, lon 27.00,
near the Baltic). On the practice pool that prior averages ~6,843 km per
photo. It is deterministic: the same photos always get the same answers.
"""
import json
import os
import urllib.request

# Fixed prior: geometric median of the 75 practice photos' true locations
# (grid search minimising total haversine distance), lat/lon in degrees.
LAT = 56.80
LON = 27.00


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def post(url, payload):
    """POST with one retry on a transient failure; a refusal is final."""
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(2):
        try:
            req = urllib.request.Request(
                url, data=data, headers={"content-type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read().decode("utf-8")
        except Exception as e:
            if attempt == 0:
                print(f"photo-geolocator: answers POST failed ({e}), retrying once")
                continue
            raise


def main():
    env = os.environ["MAKEFUN_ENV_URL"].rstrip("/")
    listed = get(env + "/photos")
    photos = [p for p in listed["photos"] if not p.get("answered")]
    answers = [
        {"id": p["id"], "lat": LAT, "lon": LON} for p in photos
    ]
    if not answers:
        print("photo-geolocator: no photos left to answer")
        return 0
    status, body = post(env + "/answers", {"answers": answers})
    print(f"photo-geolocator: {len(answers)} of {listed['total']} photos answered: HTTP {status} {body}")
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
