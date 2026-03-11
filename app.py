import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="E-Vagas", page_icon="⚡")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURAÇÃO DE FUSO HORÁRIO E DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo') # Garante o horário de Brasília
agora = datetime.now(fuso_br)
hoje = agora.strftime("%d/%m/%Y")
hora_atual = agora.hour

# --- LISTA DE USUÁRIOS ATUALIZADA ---
usuarios = {
    "Johana": "BYD King Branco (UIV6C56)", 
    "Andréia": "BYD Yuan Pro Branco (PBZ6D66)",
    "Cinthya": "ORA Branco (UIV4J70) / BYD King Branco (PBZ7E00)", 
    "Hyago": "BYD King Preto (PAR5I69)",
    "Renata": "BYD Yuan Pro Cinza (IUV4I50)", 
    "Victor": "BYD Yuan Pro Cinza (OZX7D03)",
    "João Paulo": "BYD Dolphin Mini Branco (SSI9A98)", 
    "Luciano": "BYD Dolphin Cinza (SGY6F66)",
    "Guilherme Gomes": "BYD King Cinza (SGZ1E58)", 
    "Mariana Dutra": "GWM ORA (SSN2A80)",
    "Edgard Sousa": "Volvo EX30 Cinza (SSJ-9C15)", 
    "Igor Caires": "BYD Song Pro Preto (UIX2B28)",
    "Hugo": "BYD MINI Preto (PBH3E31)", 
    "Ana Carolina": "BYD MINI (UJL1F84)",
    "Gabriela": "GWM ORA Branco (UJL2D89)"
}

horarios = ["10:00 - 13:00", "13:00 - 16:00", "16:00 - 19:00"]

# --- AUTOMAÇÃO: LIMPEZA DIÁRIA INTELIGENTE ---
try:
    df_geral = conn.read(worksheet="fila", ttl=0)
    if not df_geral.empty and 'Data' in df_geral.columns:
        if not df_geral[df_geral['Data'] != hoje].empty:
            df_limpo = df_geral[df_geral['Data'] == hoje]
            conn.update(worksheet="fila", data=df_limpo)
except Exception:
    pass 

# --- TÍTULO E SUBTÍTULO CORRIGIDOS ---
st.title("⚡ E-Vagas EV")
st.subheader("Seu APP de reservas de vagas de carregamento no CNJ")
st.divider()

# --- INSTRUÇÕES DE AGENDAMENTO ---
st.markdown("""
**Como agendar o seu carregamento:**
1. Verifique na **Grade de Hoje** (abaixo) quais horários e vagas estão livres.
2. Selecione o seu nome na lista.
3. Escolha a janela de horário e a vaga desejada.
4. Clique em **Confirmar Agendamento**.  

**Obs. Todos os dias a fila é zer
