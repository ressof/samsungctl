import base64
import json
import logging
import socket
import time

from . import exceptions


class RemotePin():
    """Object for remote control connection."""

    def __init__(self, config):
        import websocket
        import requests
        from . import aes_cipher

        if not config["port"]:
            config["port"] = 8000

        if config["timeout"] == 0:
            config["timeout"] = None

        HTTP_URL_FORMAT = 'http://{}:{}/socket.io/1/?t={}'
        WS_URL_FORMAT = 'ws://{}:{}/socket.io/1/websocket/{}'

        millis = int(round(time.time() * 1000))
        websocket_key = requests.get(HTTP_URL_FORMAT.format(config["host"], config["port"], millis))


        """Make a new connection."""
        self.aesCipher = aes_cipher.AESCipher(config['session_key'], config['session_id'])
        self.connection = websocket.create_connection(WS_URL_FORMAT.format(config["host"], config["port"], websocket_key.text.split(':')[0]), config["timeout"])
        time.sleep(0.35)
        self.connection.send('1::/com.samsung.companion')

        #self._read_response()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.debug("Connection closed.")



    def control(self, key):
        """Send a control command."""
        if not self.connection:
            raise exceptions.ConnectionClosed()

        payload = self.aesCipher.generate_command(key)
        logging.info("Sending control command: %s", key)
        self.connection.send(payload)
        time.sleep(self._key_interval)
        
     def getFullUrl(urlPath):
        global tvIP, tvPort
        return "http://"+config['host']+":8080"+urlPath
        
     def GetFullRequestUri(step, appId, deviceId):
        return getFullUrl("/ws/pairing?step="+str(step)+"&app_id="+appId+"&device_id="+deviceId)

    _key_interval = 1.0
    
    
    @staticmethod
    def pair(config):
        import requests
        import urllib3
        import codecs
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        external_server = 'https://34.210.190.209:5443'
        external_headers = {'Authorization': 'Basic b3JjaGVzdHJhdG9yOnBhc3N3b3Jk', 'Content-Type': 'application/json',
                            'User-Agent': 'Remotie%202/1 CFNetwork/893.7 Darwin/17.3.0'}

        ### STEP 0 START
        AppId = "12345"
        deviceId =  "7e509404-9d7c-46b4-8f6a-e2a9668ad184"
        step0_pin_url = 'http://' + config['host'] + ':8080/ws/apps/CloudPINPage'
        requests.post(step0_pin_url, data='pin4')
        #step0_url = 'http://' + config['host'] + ':8080/ws/pairing?step=0&app_id=com.samsung.companion&device_id=' + device_id + '&type=1'
        step0_url = GetFullRequestUri(0,AppId, deviceId)+"&type=1"
        #r = requests.get(step0_url)  # we can prob ignore this response
        r = requests.get(step0_url).text
        ### STEP 0 START


        ### STEP 1 START
        pin = input("Enter TV Pin: ")
#        payload = {'pin': pin, 'payload': '', 'deviceId': device_id}
#        r = requests.post(external_server + '/step1', headers=external_headers, data=json.dumps(payload), verify=False)
        step1_url = GetFullRequestUri(1,AppId, deviceId)+"&type=1"
        #step1_url = 'http://' + config['host'] + ':8080/ws/pairing?step=1&app_id=com.samsung.companion&device_id=' + device_id + '&type=1'
        #step1_response = requests.post(step1_url, data=r.text)
        step1_response = requests.get(step1_url).text
        #### STEP 1 END


        ### STEP 2 START
        #payload = {'pin': pin, 'payload': codecs.decode(step1_response.text, 'unicode_escape'), 'deviceId': device_id}
        #r = requests.post(external_server + '/step2', data=json.dumps(payload), headers=external_headers, verify=False)
        #step2_url = 'http://' + config['host'] + ':8080/ws/pairing?step=2&app_id=com.samsung.companion&device_id=' + device_id + '&type=1&request_id=0'
        step2_url = GetFullRequestUri(2, AppId, deviceId)
        step2_response = requests.post(step2_url, data=r.text)
        ### STEP 2 END


        ### STEP 3 START
        #payload = {'pin': pin, 'payload': codecs.decode(step2_response.text, 'unicode_escape'), 'deviceId': device_id}
        #r = requests.post(external_server + '/step3', data=json.dumps(payload), headers=external_headers, verify=False)
        enc_key = r.json()['session_key']
        session = r.json()['session_id']
        print('session_key: ' + enc_key)
        print('session_id: ' + session)
        step3_url = 'http://' + config['host'] + ':8080/ws/apps/CloudPINPage/run'
        requests.delete(step3_url)
        ### STEP 3 END



    def _read_response(self):
        response = self.connection.recv()
        response = json.loads(response)

        if response["event"] != "ms.channel.connect":
            self.close()
            raise exceptions.UnhandledResponse(response)

        logging.debug("Access granted.")

