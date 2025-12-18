# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:08:30 2025

@author: RARCA
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Buscador de Instrumentos BYMA")

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
    lambda row: 'SISTACO' if row['Segmento'] == 'CT' and row['Block'] == 1
    else 'PPT' if row['Segmento'] == 'CT' and row['Block'] == 0
    else 'SENEBI' if row['Segmento'] == 'SB'
    else row['Segmento'],
    axis=1
)

# Regla Plazo
df['Plazo'] = df['Plazo'].replace({1: 'CI', 2: '24hs'})

# Regla Estado (nuevo)
df['Estado'] = df['Estado'].replace({
    0: 'Activa',
    1: 'Suspendida',
    2: 'Halted'
})

symbol = st.text_input("Ingrese el symbol").upper().strip()

if symbol:
    matches = df[df['Ticker'] == symbol]
    if not matches.empty:
        cvsaid = matches['CVSA ID'].iloc[0]
        resultados = df[df['CVSA ID'] == cvsaid]
        st.dataframe(resultados, use_container_width=True)
    else:
        st.write("Symbol no encontrado")
else:
    st.info("Ingrese un symbol para buscar")