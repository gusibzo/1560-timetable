"""Build the two route snapshots from the public GBIS mobile route views."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

ROUTES = {"A": 234000884, "B": 228000433}
KOREA = timezone(timedelta(hours=9))


def fetch(endpoint, route_id):
    with urlopen(f"https://m.gbis.go.kr/api/{endpoint}?routeId={route_id}", timeout=10) as response:
        return json.load(response)


def stations(data):
    rows = sorted(data["records"], key=lambda row: row["stationSeq"])
    if len(rows) < 2 or len({row["stationSeq"] for row in rows}) != len(rows):
        raise ValueError("Incomplete station list")
    return [{"seq": row["stationSeq"], "id": row["stationId"], "name": row["stationName"],
             "area": row.get("regionName", ""), "number": str(row.get("mobileNo") or "").zfill(5)
             if row.get("mobileNo") else "", "turn": row.get("turnYn") == "Y"} for row in rows]


def positions(data, route_id, stops):
    response = data["response"]
    header = response["msgHeader"]
    code = int(header["resultCode"])
    if code not in (0, 4):
        raise ValueError("GBIS position feed unavailable")
    when = datetime.fromisoformat(header["queryTime"]).replace(tzinfo=KOREA)
    rows = [] if code == 4 else response["msgBody"]["busLocationList"]
    if isinstance(rows, dict):
        rows = [rows]
    by_seq = {row["seq"]: row["id"] for row in stops}
    buses = []
    for row in rows:
        seq = row["stationSeq"]
        if row["routeId"] != route_id or by_seq.get(seq) != row["stationId"]:
            continue
        buses.append({"seq": seq, "vehicle": str(row.get("plateNo") or "")[-4:],
                      "seats": row.get("remainSeatCnt")})
    return {"at": when.isoformat(), "buses": buses}


def refresh(item, directory):
    route, route_id = item
    path = directory / f"{route}.json"
    fallback = json.loads(path.read_text())
    try:
        stops = stations(fetch("routeStations", route_id))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"1560{route} using bundled station list: {error}", file=sys.stderr)
        stops = fallback["stops"]
    try:
        observation = positions(fetch("busLocationsOfRoute", route_id), route_id, stops)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"1560{route} position data unavailable: {error}", file=sys.stderr)
        observation = None
    path.write_text(json.dumps({"route": route, "stops": stops, "observation": observation},
                               ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"1560{route}: {len(stops)} stations; positions available: {observation is not None}")


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda item: refresh(item, directory), ROUTES.items()))
