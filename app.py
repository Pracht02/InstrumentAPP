# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:08:30 2025

@author: RARCA
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Buscador de Instrumentos BYMA")

df = pd.read_csv("https://raw.githubusercontent.com/Pracht02/InstrumentAPP/main/instrumentos.csv")

# Renombrar columnas
df = df.rename(columns={
    'symbol': 'Ticker',
    'CVSAId': 'CVSA ID',
    'category': 'Tipo instrumento',  # Temporal para usar
    'market': 'Segmento',
    'currency': 'Moneda',
    'settlPeriod': 'Plazo',
    'lotSize': 'LM',
    'minimumSize': 'CM',
    'block': 'Block',
    'isin': 'ISIN',
    'instrumentStatus': 'Estado'
})

# Reglas existentes...
df['Segmento'] = df.apply(
    lambda row: 'PPT' if (row['Segmento'] == 'CT' and row['Block'] == 1 and row['Tipo instrumento'] == '01-ACCIONES PRIVADAS')
    else 'SISTACO' if (row['Segmento'] == 'CT' and row['Block'] == 1)
    else 'PPT' if (row['Segmento'] == 'CT' and row['Block'] == 0)
    else 'SENEBI' if row['Segmento'] == 'SB'
    else row['Segmento'],
    axis=1
)

df['Plazo'] = df['Plazo'].replace({1: 'CI', 2: '24hs'})
df['Estado'] = df['Estado'].replace({0: 'Activa', 1: 'Suspendida', 2: 'Halted'})

query = st.text_input("Ingrese Ticker, ISIN o CVSA ID").upper().strip()

if query:
    matches = df[
        (df['Ticker'] == query) |
        (df['ISIN'] == query) |
        (df['CVSA ID'].astype(str) == query)
    ]

    if not matches.empty:
        cvsaid = matches['CVSA ID'].iloc[0]
        resultados = df[df['CVSA ID'] == cvsaid]

        first_row = resultados.iloc[0]
        st.subheader("Descripción del instrumento")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Emisor:** {first_row.get('issuer', 'N/A')}")
        with col2:
            st.write(f"**Tipo:** {first_row.get('Tipo instrumento', 'N/A')}")
        with col3:
            st.write(f"**Descripción:** {first_row.get('securityDescription', 'N/A')}")

        # Ocultar columnas issuer, securityDescription y Tipo instrumento
        resultados = resultados.drop(columns=['securityId', 'issuer', 'securityDescription', 'Tipo instrumento'], errors='ignore')

        st.dataframe(resultados, use_container_width=True)
    else:
        st.write("No encontrado")
else:
    st.info("Ingrese Ticker, ISIN o CVSA ID para buscar")




