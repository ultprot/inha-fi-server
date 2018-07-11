#-*- coding:utf-8 -*-
#!/usr/bin/env python

# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DialogFlow API Detect Intent Python sample with text inputs.
Examples:
  python detect_intent_texts.py -h
  python detect_intent_texts.py --project-id PROJECT_ID \
  --session-id SESSION_ID \
  "hello" "book a meeting room" "Mountain View"
  python detect_intent_texts.py --project-id PROJECT_ID \
  --session-id SESSION_ID \
  "tomorrow" "10 AM" "2 hours" "10 people" "A" "yes"
"""

# [START import_libraries]
import argparse
import uuid

import dialogflow_v2
from google.protobuf.json_format import MessageToJson
import json
# [END import_libraries]


# [START dialogflow_detect_intent_text]
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
    response_json=MessageToJson(response.query_result)
    response_json=json.loads(response_json)
    print(response_json["parameters"]["any"])
    return str(response_json)
# [END dialogflow_detect_intent_text]


if __name__ == '__main__':
    querymun="인하대 가는 길 알려줘"
    detect_intent_texts(
        "guidance-2d934",str(uuid.uuid4()), querymun, 'ko')