# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:08:30 2025

@author: RARCA
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Buscador de Especies")

# Carga CSV directo desde GitHub (sin rebuild en Render)
df = pd.read_csv("https://raw.githubusercontent.com/Pracht02/InstrumentAPP/main/instrumentos.csv")

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

query = st.text_input("Ingrese Ticker, ISIN o CVSA ID").upper().strip()

if query:
    # Busca en las 3 columnas
    matches = df[
    (df['Ticker'] == query) |
    (df['ISIN'] == query) |
    (df['CVSA ID'].astype(str) == query)
    ]

    if not matches.empty:
        cvsaid = matches['CVSA ID'].iloc[0]
        resultados = df[df['CVSA ID'] == cvsaid]
        st.dataframe(resultados, use_container_width=True)
    else:
        st.write("No encontrado")
else:

    st.info("Ingrese Ticker, ISIN o CVSA ID para buscar")
