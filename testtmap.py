#-*- coding:utf-8 -*-
from flask import Flask,json    #flask용 package
from flask import jsonify       #
from flask import request       #
import requests

with open('./apiKeys.json') as apiKeyFile:
    key=json.load(apiKeyFile)

class TmapCli:
    def poiSearch(self,dest,lon=127.0017441,lat=37.5395634):    #poi검색
        URL='https://api2.sktelecom.com/tmap/pois'  #get URL
        params=\
        {'version':'1','page':'1','count':'10',\
        'searchKeyword':dest,'areaLLCode':'11','areaLMCode':'000',\
        'resCoordType':'WGS84GEO','searchType':'name','multiPoint':'N',\
        'searchtypCd':'A','radius':'1','reqCoordType':'WGS84GEO',\
        'centerLon':lon,'centerLat':lat}
        headers=\
        {'Accept':'application/json',\
        'Content-Type':'application/json;charset=UTF-8',\
        'appKey':key["tmap"]}
        response=requests.get(URL,params=params,headers=headers)
        resultJson=json.loads(response.text)
        print("dest=%s",dest)
        print("lon=%s",lon)
        print("lat=%s",lat)
        return resultJson
    def pedesSearch(self,poiresult,lon=127.0017441,lat=37.5395634):
        URL='https://api2.sktelecom.com/tmap/routes/pedestrian'
        params=\
        {'version':'1'}
        headers=\
        {'Accept':'application/json',\
        'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',\
        'appKey':key["tmap"]}
        endx=poiresult['searchPoiInfo']['pois']['poi'][0]['noorLon']
        endy=poiresult['searchPoiInfo']['pois']['poi'][0]['noorLat']
        lon=str(lon)
        lat=str(lat)
        payload=\
        {'startX':lon,'startY':lat,\
        'endX':endx,'endY':endy,\
        'startName':'st','endName':'en'}
        
        print(payload)
        response=requests.post(URL,params=params,headers=headers,data=payload)
        return response.text

tc = TmapCli()
poi=tc.poiSearch('서울역')
print(poi)
rst=tc.pedesSearch(poi)
print(str(rst))