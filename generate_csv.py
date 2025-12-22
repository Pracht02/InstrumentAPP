# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:05:08 2025

@author: RARCA
"""

import requests
import pandas as pd
import os

base_url = "https://apigw.byma.com.ar"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    url = f"{base_url}/oauth/token/"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "marketDataInstruments.read"
    }
    r = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    r.raise_for_status()
    return r.json()["access_token"]

def get_instrument_equity(token):
    groups = ["ACCIONES", "CEDEARS", "FONDOSINVERSION", "ADRS", "ACCIONESPYMES"]
    url = f"{base_url}/market-data-instruments/v1/equities.json/"
    headers = {"Authorization": f"Bearer {token}"}
    dfs = {}
    for group in groups:
        params = {"group": group}
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()["result"]
        dfs[group] = pd.DataFrame(data)
    return dfs

def get_instrument_rf(token):
    groups = ["TITULOSPUBLICOS", "BONOSCONSOLIDACION", "LETRAS", "LETRASTESORO",
              "TITULOSDEUDA", "CERTPARTICIPACION", "OBLIGACIONESNEGOC", "ONPYMES"]
    markets = ["PPT", "SENEBI"]
    url = f"{base_url}/market-data-instruments/v1/fixed-income.json/"
    headers = {"Authorization": f"Bearer {token}"}
    dfs = {}
    for group in groups:
        for market in markets:
            params = {"group": group, "market": market}
            r = requests.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()["result"]
            dfs[f"{group}_{market}"] = pd.DataFrame(data)
    return dfs

if __name__ == "__main__":
    token = get_token()
    equity = get_instrument_equity(token)
    rf = get_instrument_rf(token)
    columns = ['symbol', 'CVSAId', 'securityDescription','issuer', 'category', 'market', 'currency', 'settlPeriod', 'lotSize', 'minimumSize', 'block', 'isin', 'instrumentStatus']
    all_dfs = list(equity.values()) + list(rf.values())
    combined_df = pd.concat(all_dfs, ignore_index=True)[columns]
    combined_df.to_csv("instrumentos.csv", index=False)

    print("CSV generado exitosamente")
