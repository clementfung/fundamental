import requests
import os


VENMO_CLIENT_ID = os.getenv('VENMO_CLIENT_ID')
VENMO_CLIENT_SECRET = os.getenv('VENMO_CLIENT_SECRET')

BASE_URL = 'https://api.venmo.com'
SANDBOX = True
if SANDBOX:
    BASE_URL = 'https://sandbox-api.venmo.com'


def get_access_and_refresh_token(user_token):
    if SANDBOX:
        return os.getenv('VENMO_ACCESS_TOKEN')
    data = {
            "client_id": VENMO_CLIENT_ID,
            "client_secret": VENMO_CLIENT_SECRET,
            "code": user_token 
            }
    url = "https://api.venmo.com/v1/oauth/access_token"
    response = requests.post(url, data)
    response_dict = response.json()
    return [response_dict['access_token'], response_dict['refresh_token']]

def post_payment(access_token, vendor_id, note, amount):
    access_token = os.getenv('VENMO_ACCESS_TOKEN') if SANDBOX else access_token
    user_id = 145434160922624933 if SANDBOX else vendor_id # id for sandbox 
    note = "A message to accompany the payment." if SANDBOX else note
    amount = 0.10 if SANDBOX else amount
    data = {
            "access_token": access_token,
            "user_id" : user_id,
            "note" : note,
            "amount": amount,
            } 
    url = '%s/v1/payments' % BASE_URL
    response = requests.post(url, data)
    return response.json()['data']
