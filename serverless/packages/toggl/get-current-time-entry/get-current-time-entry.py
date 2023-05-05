import requests
import os
import json
from base64 import b64encode

def main(args):
    data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries/current', headers={'content-type': 'application/json', 'Authorization' : 'Basic ' + os.environ['TOGGL_B64']})
    resp = data.json()
    tags = resp['tags']

    match resp['project_id']:
        case 163283056:
            return {"body" : {"currently" : "napping" if "Napping" in tags else "sleeping", "color" : "#9e5bd9"}}
        case 163283062:
            return {"body" : {"currently" : "playing games with friends" if "friends" in tags else "playing games", "color" : "#2da608"}}
        case 163283071:
            return {"body" : {"currently" : "doing " + (tags[0] if len(tags) > 0 else "some") + " homework", "color" : "#d92b2b"}}
        case 163283073:
            return {"body" : {"currently" : "journaling" if "Pre-Sleep" in tags else "doing personal work", "color" : "#d94182"}}
        case 163283083 | 163283084:
            return {"body" : {"currently" : "showering", "color" : "#0b83d9"}}
        case 163283087:
            return {"body" : {"currently" : "eating with friends" if "friends" in tags else "eating", "color" : "#e36a00"}}
        case 163283089:
            return {"body" : {"currently" : "socializing with " + ("family" if "Family" in tags else "friends"), "color" : "#06a893"}}
        case 163283101:
            return {"body" : {"currently" : "scrolling", "color" : "#bf7000"}}
        case 163283106:
            return {"body" : {"currently" : "between activities", "color" : "#c9806b"}}
        case 163283552:
            return {"body" : {"currently" : "running errands", "color" : "#566614"}}
        case 163283553:
            return {"body" : {"currently" : "in transit", "color" : "#991102"}}
        case 163284065:
            return {"body" : {"currently" : "practicing the saxophone", "color" : "#525266"}}
        case 164101407:
            return {"body" : {"currently" : "in a club meeting", "color" : "#465bb3"}}
        case 166780430:
            return {"body" : {"currently" : "booting up", "color" : "#06a893"}}
        case 178792504:
            return {"body" : {"currently" : "at work", "color" : "#c7af14"}}
        case 163284076:
            return {"body" : {"currently" : "in class", "color" : "#d92b2b"}}
        case 164680168:
            return {"body" : {"currently" : "working out", "color" : "#0b83d9"}}
        case _:
            return {"body" : {"currently" : "doing something", "color" : "#000000"}}