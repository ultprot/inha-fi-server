#-*- coding:utf-8 -*-
#--------------------------------------
from flask import Flask,json     #flask용 package
from flask import jsonify   #
from flask import request   #
#-----------------------------------------------------------------
import sys                                              #dialogflow용 package    
import argparse                                         #    
import uuid                                             #                    
                                                        #
import dialogflow_v2                                    #
from google.protobuf.json_format import MessageToJson   #                                            #
#----------------------------------------------------------------              
import requests #http 요청 생성용 package
#----------------------------------------------------------------
app = Flask (__name__)

with open('./apiKeys.json') as apiKeyFile:
    key=json.load(apiKeyFile)

#-------------------------------dialogflow---------------------------------------------------
def detect_intent_texts(project_id, session_id, texts, language_code):                              
    """Returns the result of detect intent with texts as inputs.                                
    Using the same `session_id` between requests allows continuation                                
    of the conversaion."""                              
    session_client = dialogflow_v2.SessionsClient()                             

    session = session_client.session_path(project_id, session_id)                               
    print('Session path: {}\n'.format(session))                             


    text_input = dialogflow_v2.types.TextInput(                             
        text=texts, language_code=language_code)                                

    query_input = dialogflow_v2.types.QueryInput(text=text_input)                               

    response = session_client.detect_intent(                                
        session=session, query_input=query_input)                               

        #print('=' * 20)
        #print('Query text: {}'.format(response.query_result.query_text))
        #print('Detected intent: {} (confidence: {})\n'.format(
        #    response.query_result.intent.display_name,
        #    response.query_result.intent_detection_confidence))
        #print('Fulfillment text: {}\n'.format(
        #    response.query_result.fulfillment_text))
    #print(response.query_result.parameters["fields"][0])
    response_json=MessageToJson(response.query_result)  #json string으로 변환
    response_json=json.loads(response_json) #json 오브젝트로 변환
    return response_json
#--------------------------------------------------------------------------------------------------------------------

#---------------------------tmap api용 클래스----------------------------------------
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
        response=requests.post(URL,params=params,headers=headers,data=payload)
        return response.text
#-----------------------------------------------------------------------------------

#----------------------
@app.route("/")
def hello():
    return "서버 작동 중"
#----------------------

#---------------------------------------------------------------------------------------------------
@app.route("/post",methods=['POST'])
def query():
    if request.method == 'POST':
        print(request.get_json())   #전달받은 json 빼내기
        querymun=request.get_json()['value']    #사용자 입력 걸러내기
        response_json=detect_intent_texts(                      #
        "guidance-2d934", str(uuid.uuid4()), querymun, 'ko')    #df에 쿼리
        intent=response_json["intent"]["displayName"]   #인텐트 빼내기
        if intent == "destination": #길찾기 인텐트
            destination=response_json["parameters"]["dest"] #목적지
            tc=TmapCli()    #tmap api 사용을 위한 인스턴스
            poi=tc.poiSearch(destination)   #poi검색 목록중 첫번째 선택
            rst=tc.pedesSearch(poi) #경로 검색
            rstJson=json.loads(rst) #json으로 변환
            return str(rstJson)
        elif intent=="bus-search2": #
            busnum=response_json["parameters"]["number"]
            busnum1=response_json["parameters"]["number1"]
            busnumber=str(int(busnum[0]))+"-"+str(int(busnum1[0]))
            return busnumber
        elif intent=="bus_search":
            busnum=response_json["parameters"]["number"]
            busnum=str(int(busnum))
            return busnum
        elif intent=="search":
            search_criteria=response_json["parameters"]["criteria"]
            search_object=response_json["parameters"]["dest"]
            search_result=str(search_criteria)+" "+str(search_object)
            return search_result
        elif intent=="Default Welcome Intent":
            welcome=response_json["fulfillmentMessages"][0]["text"]["text"][0]
            welcome=str(welcome)
            return welcome
        else:
            fallback=response_json
            fallback=str(fallback)
            return fallback
#-------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=26530)
