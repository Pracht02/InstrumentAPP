# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 18:08:30 2025

@author: RARCA
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Buscador de Instrumentos BYMA")

# Carga datos desde CSV actualizado diario por GitHub Actions
df = pd.read_csv("instrumentos.csv")

symbol = st.text_input("Ingrese el symbol").upper().strip()

if symbol:
    matches = df[df['symbol'] == symbol]
    if not matches.empty:
        cvsaid = matches['CVSAId'].iloc[0]
        resultados = df[df['CVSAId'] == cvsaid]
        st.dataframe(resultados, use_container_width=True)
    else:
        st.write("Symbol no encontrado")
else:
    st.info("Ingrese un symbol para buscar")