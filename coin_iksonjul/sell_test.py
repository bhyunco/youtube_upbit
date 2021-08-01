#!/usr/bin/env python
# coding: utf-8

# In[2]:


import getpass
def login():
    global access_key
    global secret_key
    access_key = getpass.getpass("access_key:")
    secret_key = getpass.getpass("secret_key:")
login()


get_ipython().system('pip install selenium')
get_ipython().system('pip install jwt')
get_ipython().system('pip install pyupbit')
get_ipython().system('pip install upbit-client')
get_ipython().system('pip install pyperclip')


import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import random
import pandas as pd
import datetime
import requests #서버에 접속해서 데이터를 받아오는 역할
import re
import json # json 을 해석해주는 역할을 한다.
import pyperclip
import pprint
import pyupbit
from upbit.client import Upbit
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode


def price_trim(price_trim):   
    #~10원 미만[소수점 둘째자리]
    if price_trim<10:
        price_trim = round(price_trim,2)  
    #10~100원 미만 - [소수점첫째자리]
    elif price_trim<100:
        price_trim = round(price_trim,1)  
    #100~1,000원 미만 - [1원단위]
    elif price_trim<1000:
        price_trim = round(price_trim)
    #1,000~10,000원 미만[5원단위]
    elif price_trim<10000:
        price_trim = round(price_trim*2,-1)/2
    #10,000~100,000원 미만[10원단위]
    elif price_trim<100000:
        price_trim = round(price_trim,-1) 
    #100,000~500,000원 미만 [50원단위]    
    elif price_trim<500000:
        price_trim = round(price_trim*2,-2)/2 
    #500,000원~1,000,000원 미만[100원단위]        
    elif price_trim<1000000:
        price_trim = round(price_trim,-2)
    #1,000,000~2,000,000 [500원단위]
    elif price_trim<2000000:
        price_trim = round(price_trim*2,-3)/2
    #2,000,000 이상 [1000원단위]
    else:
        price_trim = round(price_trim,-3)
    return price_trim

def Timestamp(a):
    return a

#주문취소
def order_cancel(ud):
    query = {
        'uuid': ud,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.delete(server_url + "/v1/order", params=query, headers=headers)

    print(res.json())  

def coins(current):
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"true"}
    response = requests.request("GET", url, params=querystring)
    response_json = json.loads(response.text)

    KRWticker = []
    BTCticker = []
    USDTticker = []

    for a in response_json:
    #     print(a['market'])
        if "KRW-" in a['market']:
            KRWticker.append(a['market'])
        elif "BTC-" in a['market']:
            BTCticker.append(a['market'])
        elif "USDT-" in a['market']:
            USDTticker.append(a['market'])    
    ticker = {
        "KRW":KRWticker,
        "BTC":BTCticker,
        "USDT":USDTticker
    }
#     print(ticker)
    if current=="ALL":
        ticker = ticker
    else:
        ticker = ticker[current]
    return ticker

#암호화폐 시세조회

def coin_price(coin):
    url = "https://api.upbit.com/v1/orderbook"
    querystring = {"markets":coin}
    response = requests.request("GET", url, params=querystring)
    response_json = json.loads(response.text)
    coin_now_price = response_json[0]["orderbook_units"][0]["ask_price"]
    return coin_now_price
#시세 호가 정보(Orderbook) 조회 // 호가 정보 조회


def coin_history(coin,time1='minute',time2=""):
    url = f"https://api.upbit.com/v1/candles/{time1}/{time2}"

    querystring = {"market":coin,"count":"200"}

    response = requests.request("GET", url, params=querystring)
    response_json = json.loads(response.text)
    # print(type(response_json))
    df = pd.DataFrame(response_json)
    return df

#로그인
# def login():
#     f=open("upbit_api_특정코인익절손절.txt")
#     lines = f.readlines()
#     global access_key
#     global secret_key
#     access_key = str(lines[0].strip())
#     secret_key = str(lines[1].strip())
#     f.close
# login()

#order_list 보는법
def order_list():
    client = Upbit(access_key, secret_key)
    resp = client.Order.Order_info_all()
    return resp['result']

#나의 계좌 잔액 조회

def balance():
    global server_url
    server_url = 'https://api.upbit.com'

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)
#     print(res.json())
    return res.json()
balance()
#매수(지정가)

def buy_limit(coin,volume,price):
    query = {
        'market': coin,
        'side': 'bid',
        'volume': volume,
        'price': price,
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(res.json())
    return res.json()

#매수(시장가)
def buy_market(coin,price):
    query = {
        'market': coin,
        'side': 'bid',
        'volume': '',
        'price': price,
        'ord_type': 'price',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(res.json())
    return res.json()


#매도(지정가)

def sell_limit(coin,volume,price):
    query = {
        'market': coin,
        'side': 'ask',
        'volume': volume,
        'price': price,
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(res.json())
    return res.json()

#매도(시장가)

def sell_market(coin,volume):
    query = {
        'market': coin,
        'side': 'ask',
        'volume': volume,
        'price': '',
        'ord_type': 'market',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    print(res.json())
    return res.json()

tickers = pyupbit.get_tickers(fiat="KRW")

for a in balance():
    if a['currency']=="KRW":
        pass
    else:
        coin_name = "KRW-"+a['currency']
        now_price = coin_price("KRW-"+a['currency'])
        buy_avg_price = float(a['avg_buy_price'])
        if buy_avg_price*0.9>now_price:
            print("sell_start")
            sell_amount = a['balance']
            sell_market(coin_name,sell_amount)
            print("sell_complete")


# In[16]:




