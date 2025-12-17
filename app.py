# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 14:23:31 2025

@author: RARCA
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

base_url = "https://apigw.byma.com.ar"
client_id = "0oauyi61ssGJ1K1av697"
client_secret = "bmZk2WZPWJ0qoCVMvUcaXN4qXjyKx2_DXXcfGYxkbFR0honYq7A43lGkrIwKyhJt"

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Buscador de Instrumentos")

symbol = st.text_input("Ingrese el symbol").upper().strip()

if symbol:
    with st.spinner("Cargando datos de API BYMA..."):
        try:
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
                        key = f"{group}_{market}"
                        params = {"group": group, "market": market}
                        r = requests.get(url, headers=headers, params=params)
                        r.raise_for_status()
                        data = r.json()["result"]
                        dfs[key] = pd.DataFrame(data)
                return dfs

            token = get_token()
            equity = get_instrument_equity(token)
            rf = get_instrument_rf(token)
            columns = ['symbol', 'CVSAId', 'category', 'market', 'currency', 'settlPeriod', 'lotSize', 'minimumSize', 'block', 'isin', 'instrumentStatus']
            all_dfs = list(equity.values()) + list(rf.values())
            combined_df = pd.concat(all_dfs, ignore_index=True)[columns]
            df = combined_df

        except Exception as e:
            st.error(f"Error al conectar con API BYMA: {e}")
            df = pd.DataFrame()

    if not df.empty:
        matches = df[df['symbol'] == symbol]
        if not matches.empty:
            cvsaid = matches['CVSAId'].iloc[0]
            resultados = df[df['CVSAId'] == cvsaid]
            st.dataframe(resultados)
        else:
            st.write("Symbol no encontrado")
    else:
        st.write("No se pudieron cargar los datos")
else:
    st.info("Ingrese un symbol para buscar")