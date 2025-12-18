# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:08:30 2025

@author: RARCA
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Buscador de Especies")

df = pd.read_csv("instrumentos.csv")

# Renombrar columnas
df = df.rename(columns={
    'symbol': 'Ticker',
    'CVSAId': 'CVSA ID',
    'category': 'Tipo instrumento',
    'market': 'Segmento',
    'currency': 'Moneda',
    'settlPeriod': 'Plazo',
    'lotSize': 'LM',
    'minimumSize': 'CM',
    'block': 'Block',
    'isin': 'ISIN',
    'instrumentStatus': 'Estado'
})

# Regla Segmento
df['Segmento'] = df.apply(
    lambda row: 'PPT' if (row['Segmento'] == 'CT' and row['Block'] == 1 and row['Tipo instrumento'] == '01-ACCIONES PRIVADAS')
    else 'SISTACO' if (row['Segmento'] == 'CT' and row['Block'] == 1)
    else 'PPT' if (row['Segmento'] == 'CT' and row['Block'] == 0)
    else 'SENEBI' if row['Segmento'] == 'SB'
    else row['Segmento'],
    axis=1
)

# Regla Plazo
df['Plazo'] = df['Plazo'].replace({1: 'CI', 2: '24hs'})

# Regla Estado
df['Estado'] = df['Estado'].replace({
    0: 'Activa',
    1: 'Suspendida',
    2: 'Halted'
})

search_type = st.selectbox("Buscar por:", ["Ticker", "CVSA ID", "ISIN"])
query = st.text_input("Ingrese el valor").upper().strip()

if query:
    if search_type == "Ticker":
        matches = df[df['Ticker'] == query]
    elif search_type == "ISIN":
        matches = df[df['ISIN'] == query]
    else:  # CVSA ID
        matches = df[df['CVSA ID'] == query]

    if not matches.empty:
        if search_type != "CVSA ID":
            cvsaid = matches['CVSA ID'].iloc[0]
            resultados = df[df['CVSA ID'] == cvsaid]
        else:
            resultados = matches
        st.dataframe(resultados, use_container_width=True)
    else:
        st.write("No encontrado")
else:
    st.info("Ingrese un valor para buscar")