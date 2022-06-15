import requests
from urllib.parse import urljoin

class Voiceflow:
  def __init__(self, apiKey, versionID):
    self.apiKey = apiKey
    self.url = "https://general-runtime.voiceflow.com"
    self.versionID = versionID

  def interact(self, input):

    # Call interactions
    body = {
      "action": {
        "type": 'text',
        "payload": input,
      },
      "config": {
        "tts": "true",
      },
    }
    response = requests.post(urljoin(self.url, "/state/user/demo/interact"), json=body, headers={"Authorization":self.apiKey,"Accept": "application/json","Content-Type": "application/json"}).json()

    # Return response
    return response

  def init_state(self):
   # Begin initial session
    initialBody = {
      "action": {
        "type": 'launch'
      },
      "config": {
        "tts": "true",
      },
    }
    response = requests.post(urljoin(self.url, "/state/user/demo/interact"), json=initialBody, headers={"Authorization":self.apiKey,"Accept": "application/json","Content-Type": "application/json"}).json()

    return response

