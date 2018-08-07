#-*- coding:utf-8 -*-
from flask import Flask,json    #flask용 package
from flask import jsonify       #
from flask import request       #
import requests
from xml.etree.ElementTree import XML, fromstring, tostring, fromstringlist
import html
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
    def getStationByPos(self,radius,lon,lat):   #좌표기반 근접정류소 목록 조회
        URL='http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos'
        params={"ServiceKey":key["arrival"],"tmX":lon,"tmY":lat,"radius":radius}
        response=requests.get(URL,params=params)
        myxml=fromstring(response.text)
        return myxml
    def getArrivalInfo(self,arsId):
        URL='http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid'
        params={"ServiceKey":key["arrival"], "arsId":arsId}
        response=requests.get(URL,params=params)
        myxml=fromstring(response.text)
        return myxml
    def getArrivalInf(self,stId,busRouteId,ord):
        URL='http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute'
        params={"ServiceKey":key["arrival"], "stId":stId,"busRouteId":busRouteId,"ord":ord}
        response=requests.get(URL,params=params)
        myxml=fromstring(response.text)
        return myxml
    def gbisGetStation(self,x,y):
        URL='http://openapi.gbis.go.kr/ws/rest/busstationservice/searcharound'
        params={"ServiceKey":key["arrival"],"x":x,"y":y}
        response=requests.get(URL,params=params)
        myxml=fromstring(response.text)
        return myxml
    def gbisGetArrival(self,stationId,routeId,staOrder):
        URL='http://openapi.gbis.go.kr/ws/rest/busarrivalservice'
        params={"ServiceKey":key["arrival"],"stationId":stationId,"routeId":routeId,"staOrder":staOrder}
        response=requests.get(URL,params=params)
        myxml=fromstring(response.text)
        return myxml
tc = TmapCli()
result=tc.gbisGetStation(126.924173,37.525590)
tstring=tostring(result)
tstring=html.unescape(tstring.decode("utf-8"))
print(tstring)
"""
result=result.find("msgBody").findall("itemList")
arresult=tc.getArrivalInfo(result[0].findtext("arsId"))
arresult=arresult.find("msgBody").findall("itemList")
for i in arresult:
    if i.findtext("rtNm")=="5012":
        print(i.findtext("rerideNum1"))
#print(tostring(result))
#print(type(result))
"""
