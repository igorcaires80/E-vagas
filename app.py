import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de página
st.set_page_config(page_title="E-Vaga: Gestão", page_icon="⚡")

st.title("⚡ Gestão de Vagas EV")
st.info("As 2 primeiras pessoas da lista têm prioridade nas vagas.")

# Interface
nome = st.text_input("Digite seu nome para Check-in:")
turno = st.selectbox("Turno de trabalho:", ["Manhã", "Tarde", "Integral"])

if st.button("Confirmar Check-in"):
    if nome:
        st.success(f"Check-in realizado! {nome}, verifique sua posição na fila.")
    else:
        st.error("Por favor, preencha o seu nome.")

st.divider()

# Exibição (Simulação da fila)
st.subheader("📋 Fila de Uso")
# Por enquanto, como estamos testando, a fila está vazia.
st.write("1. 🔋 Vaga Disponível")
st.write("2. 🔋 Vaga Disponível")

st.caption("Ao finalizar o código com a Planilha Google, os nomes aparecerão aqui automaticamente.")