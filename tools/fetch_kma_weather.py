"""Publish public KMA observations for the static site; no user locations or keys."""
from datetime import datetime, timezone, timedelta
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KST = timezone(timedelta(hours=9))
BASE = 'https://www.weather.go.kr/w/'
SOURCE = BASE + 'weather/land/aws-obs.do'

def timestamp(value):
    return int(datetime.strptime(str(value), '%Y%m%d%H%M').replace(tzinfo=KST).timestamp() * 1000)

def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Non-finite observation')
    return result

def get(path):
    request = Request(BASE + path, headers={
        'User-Agent': '1560-timetable-weather/1.0', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=25) as response:
        return json.load(response)

def collect():
    stations, conditions = {}, []
    # The route operates in Seoul/Gyeonggi. Include Incheon and national ASOS
    # observations as well. Omit starred auxiliary sites and faulty sensors.
    for area in ('1100000000', '4100000000', '2800000000'):
        try:
            query = urlencode({'db':'MINDB_01M', 'stnId':0, 'sidoCode':area,
                               'sort':'awsStnId/asc', 'tm':''})
            data = get('observation/land/aws-obs-data.do?' + query)
            for row in data['items']:
                try:
                    if row.get('awsSp') not in ('SS', 'SA') or '*' in row['awsStnName']:
                        continue
                    if row.get('awsTroblKnd') not in ('', None, 'N/A'):
                        continue
                    temp, lat, lon = number(row['awsTmp']), number(row['lat']), number(row['lon'])
                    if not (-60 <= temp <= 60 and 32 < lat < 40 and 124 < lon < 133):
                        continue
                    station_id = str(row['awsStnId'])
                    stations[station_id] = {'id':station_id, 'name':row['awsStnName'],
                        'latitude':lat, 'longitude':lon, 'temperature':temp,
                        'observedAt':timestamp(row['tm'])}
                except (ValueError, KeyError, TypeError):
                    continue
        except Exception as error:
            print('KMA regional observations unavailable: ' + type(error).__name__, file=sys.stderr)
    try:
        data = get('renew2021/rest/main/current-weather-obs.do')
        observed = timestamp(data['tm'] + '00')
        for row in data['data']:
            try:
                lat, lon, temp = number(row['lat']), number(row['lon']), number(row['ta'])
                if not (-60 <= temp <= 60 and 32 < lat < 40 and 124 < lon < 133):
                    continue
                record = {'id':str(row['stnId']), 'name':row['stnKo'],
                    'latitude':lat, 'longitude':lon, 'temperature':temp, 'observedAt':observed}
                stations.setdefault(record['id'], record)
                if row.get('wwKo'):
                    conditions.append({**record, 'description':row['wwKo']})
            except (ValueError, KeyError, TypeError):
                continue
    except Exception as error:
        print('KMA current sky observations unavailable: ' + type(error).__name__, file=sys.stderr)
    return {'schema':1, 'source':'기상청 날씨누리', 'sourceUrl':SOURCE,
        'fetchedAt':int(datetime.now(timezone.utc).timestamp() * 1000),
        'stations':list(stations.values()), 'conditions':conditions}

if __name__ == '__main__':
    output = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/weather/kma.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    data = collect()
    output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f"KMA snapshot: {len(data['stations'])} stations, {len(data['conditions'])} sky reports")
