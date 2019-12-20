from datetime import datetime, timedelta
import json
import requests

# beta convert service (deprecated)
nrgApiUrl = 'https://nrgconvert.azurewebsites.net/api/Convert?code=yafm/4r/axuaMMGTP9SkBRNrpmEhrrM4B4sU6ehrXDG6bJaMpFhbIg=='
token=''

# 2020 convert service
RequestTokenUrl = 'https://dataservicesconvert.azurewebsites.net/api/ConvertToken?code=WUO2Dkq5He5Zp9XHddTGuQuNkoF09YWceIVphPhxIFn7hLGH6fvKSA=='
ConvertServiceUrl = 'https://dataservicesconvert.azurewebsites.net/api/Convert?code=rWNCyVxJAtaaMD/cr5otcCiQs8pVUuVlikEG684eibKcBhK/hLju6g=='


def request_session_token(client_id="", client_secret=""):
    """
    generates a new session token for convert service api
    requires an active account with NRG Systems. to sign
    up for an account, go to:
    https://services.nrgsystems.com

    parameters
    ----------
            client_id : obtained from NRG Systems
        client_secret : ""

    returns
    -------
             session_token : valid for 24 hour
        session_start_time : start time of 24 hour countdown
    """
    request_token_header = { 'content-type' : 'application/json' }
    request_payload = { 'client_id' : '{}'.format(client_id), 'client_secret' : '{}'.format(client_secret)}

    resp = requests.post(data=json.dumps(request_payload), headers=request_token_header, url=RequestTokenUrl)
    session_start_time = datetime.now()

    if resp.status_code == 200:
        session_token = json.loads(resp.text)['access_token']
    else:
        session_token = False

    return session_token, session_start_time


def token_valid(session_start_time):
    """
    check if token is still valid

    parameters
    ----------
        session_start_time : datetime, generated at time of token request

    returns
    -------
        status : boolean, true if still valid, false if expired
    """
    if datetime.now() < session_start_time + timedelta(hours=24):
        return True
    return False
