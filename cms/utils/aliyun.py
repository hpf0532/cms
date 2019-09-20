import requests
import json
from urllib import request
from urllib import parse
import sys
import hmac
import hashlib
from hashlib import sha1
import base64
import uuid
import time

access_key_id = 'LTAI7ojt8k01JjAV'
access_key_secret = 'Vhy0IH3n5ZFgnT892i3clEnrIjQiln'
cdn_server_address = "https://cdn.aliyuncs.com"

def percent_encode(str):
    res = request.quote(str, 'utf-8')
    # res = request.quote(str)
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res


def compute_signature(parameters, access_key_secret):
    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])

    canonicalizedQueryString = ''
    for (k,v) in sortedParameters:
        canonicalizedQueryString += '&' + percent_encode(k) + '=' + percent_encode(v)

    stringToSign = 'GET&%2F&' + percent_encode(canonicalizedQueryString[1:])
    # print(stringToSign)
    # return stringToSign


    h = hmac.new(bytes(access_key_secret + "&", encoding='utf-8'), bytes(stringToSign, encoding='utf-8'), sha1)
    # return h.digest()
    signature = base64.encodebytes(h.digest()).strip()
    return str(signature, 'utf-8')


def compose_url(user_params):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    parameters = {
            'Format'        : 'JSON',
            'Version'       : '2018-05-10',
            'AccessKeyId'   : access_key_id,
            'SignatureVersion'  : '1.0',
            'SignatureMethod'   : 'HMAC-SHA1',
            'SignatureNonce'    : str(uuid.uuid1()),
            'Timestamp'         : timestamp,
    }

    for key in user_params.keys():
        parameters[key] = user_params[key]

    signature = compute_signature(parameters, access_key_secret)
    parameters['Signature'] = signature
    return parameters


# user_params = {
#     "Action": "RefreshObjectCaches",
#     "ObjectPath": "cdn.pursedada.com/1.txt",
#     "ObjectType": "File",
# }

# ret = requests.get(cdn_server_address, params=params)
# print(json.loads(ret.text))

# timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
# parameters = {
#     'Format': 'JSON',
#     'Version': '2018-05-10',
#     'AccessKeyId': access_key_id,
#     'SignatureVersion': '1.0',
#     'SignatureMethod': 'HMAC-SHA1',
#     'SignatureNonce': str(uuid.uuid1()),
#     'Timestamp': timestamp,
# }

# ret = compute_signature(parameters, access_key_secret)
# ret = bytes(access_key_secret, encoding="utf-8")
# parameters = compose_url(user_params)
# print(parameters)

# ret = percent_encode("哈哈哈.com/1.txt")
# ret = requests.get(cdn_server_address, params=parameters)
# print(ret.text)