# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:05:08 2025

@author: RARCA
"""

import requests
import pandas as pd
import os

# Configuración base
base_url = "https://apigw.byma.com.ar"
client_id = os.getenv("CLIENT_ID")      # Credenciales desde variables de entorno
client_secret = os.getenv("CLIENT_SECRET")

def get_token(scope):
    """Obtiene token OAuth para el scope indicado"""
    url = f"{base_url}/oauth/token/"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    r = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    r.raise_for_status()
    return r.json()["access_token"]

if __name__ == "__main__":
    # --- Instrumentos (referencia estática) ---
    instr_token = get_token("marketDataInstruments.read")  # Token para instrumentos

    def get_instrument_equity(token):
        """Descarga instrumentos de renta variable por grupo"""
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
        """Descarga instrumentos de renta fija por grupo y mercado"""
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

    # Concatena todos los instrumentos en un solo DataFrame
    df_instr = pd.concat(
        list(get_instrument_equity(instr_token).values()) +
        list(get_instrument_rf(instr_token).values()),
        ignore_index=True
    )[ ['securityId','symbol', 'CVSAId', 'category', 'market', 'currency', 'settlPeriod', 'lotSize', 'minimumSize', 'block', 'isin', 'instrumentStatus', 'issuer', 'securityDescription', 'tickPriceId'] ]

    # --- Snapshot (cotizaciones) ---
    snap_token = get_token("snapshot.read")  # Token para snapshot

    def get_snapshot_all(token, operativeform="CONTADO"):
        """Descarga snapshot completo de equity y renta fija"""
        all_data = []
        # Equity
        equity_groups = ["ACCIONES", "CEDEARS", "FONDOSINVERSION", "ADRS", "CUPONESPRIVADOS"]
        equity_url = f"{base_url}/snapshot/v1/equity.raw/"
        headers = {"Authorization": f"Bearer {token}"}
        for group in equity_groups:
            params = {"group": group, "operativeform": operativeform}
            r = requests.get(equity_url, headers=headers, params=params)
            r.raise_for_status()
            all_data.extend(r.json().get("result", []))
        # Renta Fija
        rf_markets = ["PPT", "SENEBI"]
        rf_groups = ["TITULOSPUBLICOS", "BONOSCONSOLIDACION", "LETRAS", "LETRASTESORO", "TITULOSDEUDA", "CERTPARTICIPACION", "OBLIGACIONESNEGOC", "ONPYMES"]
        rf_url = f"{base_url}/snapshot/v1/fixed_income.raw/"
        for market in rf_markets:
            for group in rf_groups:
                params = {"group": group, "market": market, "operativeform": operativeform}
                r = requests.get(rf_url, headers=headers, params=params)
                r.raise_for_status()
                all_data.extend(r.json().get("result", []))
        return pd.DataFrame(all_data)

    # Snapshot con columnas seleccionadas y renombrada
    columns_snap = ['security_id', 'symbol', 'category', 'market', 'currency', 'settlPeriod']
    df_snap = get_snapshot_all(snap_token)[columns_snap].rename(columns={'security_id': 'securityId'})

    # Homogeneizar category
    category_map = {
        '1': '01-ACCIONES PRIVADAS',
        '3': '03-TITULOS PUBLICOS',
        '5': '05-OBLI. NEGOCIABLES',
        '13': '13-LETRAS',
        '14': '14-OBLIG. NEG. PYMES',
        '17': '17-LETRAS TESORO NAC',
        '18': '18-FONDOS INVERSION',
        '19': '19-TITULOS DE DEUDA',
        '20': '20-CERTIF. PARTICIP.',
        '23': '23-CEDEARS',
        '27': '27-ACCIONES PYMES'
    }
    df_snap['category'] = df_snap['category'].astype(str).map(category_map)

    # Novedades: securityId en snapshot pero no en instruments
    df_novedades = df_snap[~df_snap['securityId'].isin(df_instr['securityId'])].copy()
    df_novedades = df_novedades.reset_index(drop=True)

    # DataFrame final: instruments + novedades
    df_final = pd.concat([df_instr, df_novedades], ignore_index=True)
    #drop securityId asi no aparece en la app
    df_final = df_final.drop(columns=['securityId'], errors='ignore')
    # Guardar CSV
    df_final.to_csv("instrumentos.csv", index=False)
    print("CSV generado exitosamente")


