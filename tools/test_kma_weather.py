from unittest.mock import patch
import fetch_kma_weather as kma

base = {'awsSp':'SA','awsTroblKnd':'','awsStnId':550,'awsStnName':'오산',
        'lat':'37.1693','lon':'127.05271','awsTmp':'4.1','tm':'202610282010'}
regional = {'items':[base, {**base,'awsStnId':439,'awsStnName':'진안 *','awsTmp':'10'},
    {**base,'awsStnId':1,'awsTroblKnd':'장애'}, {**base,'awsStnId':2,'awsTmp':'-'},
    {**base,'awsStnId':3,'lat':'nan'}]}
national = {'tm':'2026102820','data':[
    {'stnId':'550','stnKo':'오산','lat':'37.1693','lon':'127.05271','ta':'5','wwKo':'맑음'},
    {'stnId':'108','stnKo':'서울','lat':'37.57','lon':'126.97','ta':'0','wwKo':'맑음'}]}
with patch.object(kma,'get',side_effect=lambda path: national if 'current-weather-obs' in path else regional):
    data=kma.collect()
assert len(data['stations']) == 2
assert next(row for row in data['stations'] if row['id']=='550')['temperature'] == 4.1
assert next(row for row in data['stations'] if row['id']=='108')['temperature'] == 0
assert kma.timestamp('202610282010') == 1793185800000
print('KMA collector rejects faulty/auxiliary/missing sensors, preserves minute precision and zero, and prefers recent regional readings')
