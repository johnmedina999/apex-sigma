import hashlib
import arrow
import json
import aiohttp
from config import HiRezAuthKey, HiRezDevID

api_session = {
    'SessionID': None,
    'GeneratedStamp': 0
}

smite_base_url = 'http://api.smitegame.com/smiteapi.svc/'
paladins_base_url = 'http://api.paladins.com/paladinsapi.svc/'


def make_timestamp():
    return arrow.utcnow().format('YYYYMMDDHHmmss')


def make_signature(session_name):
    qry = HiRezDevID + session_name + HiRezAuthKey + make_timestamp()
    crypt = hashlib.new('md5')
    crypt.update(qry.encode('utf-8'))
    return crypt.hexdigest()


async def new_session():
    timestamp = make_timestamp()
    signature = make_signature('createsession')
    access_url = smite_base_url + 'createsessionJson/' + HiRezDevID + '/' + signature + '/' + timestamp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(access_url) as data:
            data = await data.read()

    data = json.loads(data)
    #print(data)            
    
    api_session.update({
        'SessionID': data['session_id'],
        'GeneratedStamp': arrow.utcnow().timestamp
    })
    
    return


async def get_session(cmd):
    if len(HiRezDevID) == 0:
        cmd.log.error("Invalid HiRez Dev ID")
        return -1

    if len(HiRezAuthKey) == 0:
        cmd.log.error("Invalid HiRez AuthKey")
        return -1

    curr_stamp = arrow.utcnow().timestamp
    if not api_session['SessionID'] or (api_session['GeneratedStamp'] + 980) < curr_stamp:
        await new_session()
        
    return api_session['SessionID']
