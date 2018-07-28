# -*- coding:utf-8 -*-
#--------------------------------------
from flask import Flask,json     #flask용 package
from flask import jsonify   #
from flask import request   #
from flask import Response
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

#---------------------------tmap api,대중교통 api 용 클래스----------------------------------------
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
        rstJson=json.loads(response.text)
        return rstJson
    def publicSearch(self,startLon,startLat,endLon,endLat): #대중교통 경로 검색
        URL='https://api.odsay.com/v1/api/searchPubTransPath'
        params=\
        {"apiKey":key["pub"],"SX":startLon,"SY":startLat,\
        "EX":endLon,"EY":endLat,"OPT":1,"SearchType":0,"SearchPathType":0}
        response=requests.get(URL,params=params)
        rstJson=json.loads(response.text)
        return rstJson
#-----------------------------------------------------------------------------------

#----------------------
@app.route("/")
def hello():
    return "서버 작동 중"
#----------------------

#-----------------------------------초기 쿼리------------------------------------------------------------
@app.route("/query",methods=['POST'])
def query():
    if request.method == 'POST':
        print(request.get_json())   #전달받은 json 빼내기
        latitude=request.get_json()['lat']  #사용자 위도
        longitude=request.get_json()['lon'] #사용자 경도
        querymun=request.get_json()['query']    #사용자 입력
        if "sessionID" in request.get_json():   #컨텍스트를 유지해야 한다면
            sessionID=request.get_json()['sessionID']
        else:   #아니라면
            sessionID=str(uuid.uuid4()) #랜덤 uuid
        response_json=detect_intent_texts(                      #
        "guidance-2d934", sessionID, querymun, 'ko')    #df에 쿼리 uuid랜덤
        intent=response_json["intent"]["displayName"]   #인텐트 빼내기
        
        if intent == "destination": #길찾기 인텐트
            lat=request.get_json()['lat']
            lon=request.get_json()['lon']
            destination=response_json["parameters"]["dest"] #목적지
            fulfillmentText=response_json["fulfillmentText"]    #대답 
            tc=TmapCli()    #tmap 인스턴스
            poi=tc.poiSearch(destination,lon,lat)   #사용자 위치, 목적지로 poi검색
            rstJson={"sessionID":sessionID,"intent":intent,\
            "fulfillmentText":fulfillmentText, "data":poi,}#poi 결과 담아서 보냄
            response=Response(
                response=json.dumps(rstJson,ensure_ascii=False),
                status=200,
                mimetype='application/json;charset=UTF-8'
            )
            return response

        elif intent=="destination_poi_select":
            fulfillmentText=response_json["fulfillmentText"]    #대답
            rstJson={"sessionID":sessionID, "intent":intent,"fulfillmentText":fulfillmentText}
            data={}
            if "poi_dest" in response_json["parameters"]:
                data["dest"]=response_json["parameters"]["poi_dest"]
            elif "poi_number" in response_json["parameters"]:
                data["number"]=response_json["parameters"]["poi_number"]
            rstJson["data"]=data
            response=Response(
                response=json.dumps(rstJson,ensure_ascii=False),
                status=200,
                mimetype='application/json;charset=UTF-8'
            )
            return response

        elif intent=="destination_path_results":
            fulfillmentText=response_json["fulfillmentText"]    #쿼리 결과
            startLon=request.get_json()['lon']   #시작 경도
            startLat=request.get_json()['lat']   #시작 위도
            endLon=request.get_json()['endLon']   #목적지 경도
            endLat=request.get_json()['endLat']   #목적지 위도
            tc=TmapCli()    #tmap 인스턴스
            path=tc.publicSearch(startLon,startLat,endLon,endLat)   #대중교통 경로 검색
            rstJson={"sessionID":sessionID, "intent":intent,"fulfillmentText":fulfillmentText,"data":path}  
            #경로 담아서 보냄
            response=Response(
                response=json.dumps(rstJson,ensure_ascii=False),
                status=200,
                mimetype='application/json;charset=UTF-8'
            )
            return response

        elif intent=="destination_path_select":
            fulfillmentText=response_json["fulfillmentText"]    #대답
            transportation=response_json["parameters"]["transportation"]    #선택된 수단
            data={"transportation":transportation}
            rstJson={"sessionID":sessionID, "intent":intent,"fulfillment":fulfillmentText,"data":data}
            #교통수단 담아서 보냄
            response=Response(
                response=json.dumps(rstJson,ensure_ascii=False),
                status=200,
                mimetype='application/json;charset=UTF-8'
            )
            return response

        elif intent=="bus_search":
            if "number1" in response_json["parameters"]:  
                busnum=str(response_json["parameters"]["number"])+"-"+str(response_json["parameters"]["number1"])
            elif "name" in response_json["parameters"]:
                busnum=str(response_json["parameters"]["name"])+" "+str(response_json["parameters"]["name"])
            else:
                busnum=str(response_json["parameters"]["number"])
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
    else:
        return "error"
#-------------------------------------------------------------------------------------------------------



if __name__ == "__main__":
	app.run(host='0.0.0.0', port=26531)
