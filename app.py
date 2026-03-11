import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-Vagas", page_icon="⚡")

# Conexão profissional via Service Account
conn = st.connection("gsheets", type=GSheetsConnection)

usuarios = {
    "Johana": "BYD King Branco (UIV6C56)", "Andréia": "BYD Yuan Pro Branco (PBZ6D66)",
    "Cinthya": "ORA/BYD King (UIV4J70 / PBZ7E00)", "Hyago": "BYD King Preto (PAR5I69)",
    "Renata": "BYD Yuan Pro Cinza (IUV4I50)", "Victor": "BYD Yuan Pro Cinza (OZX7D03)",
    "João Paulo": "BYD Dolphin Mini Branco (SSI9A98)", "Luciano": "BYD Dolphin Cinza (SGY6F66)",
    "Guilherme Gomes": "BYD King Cinza (SGZ1E58)", "Mariana Dutra": "GWM ORA (SSN2A80)",
    "Edgard Sousa": "Volvo EX30 Cinza (SSJ-9C15)", "Igor Caires": "BYD Song Pro Preto (UIX2B28)",
    "Hugo": "BYD MINI Preto (PBH3E31)", "Gabriela": "GWM ORA Branco (UJL2D89)"
}

st.title("⚡ Agenda de Carregamento")

horarios_disponiveis = ["07:00 - 10:00", "10:00 - 13:00", "13:00 - 16:00", "16:00 - 19:00"]

nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

if nome_sel:
    horario_sel = st.select_slider("Janela de horário:", options=horarios_disponiveis)
    vaga_sel = st.radio("Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        try:
            df = conn.read(worksheet="fila", ttl=0)
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            
            # Verifica conflito
            if not df[(df['Turno'] == horario_sel) & (df['Vaga'] == vaga_sel) & (df['Data'] == data_hoje)].empty:
                st.error("Horário já ocupado nesta vaga!")
            else:
                novo = pd.DataFrame([{"Nome": nome_sel, "Vaga": vaga_sel, "Turno": horario_sel, "Data": data_hoje}])
                conn.update(worksheet="fila", data=pd.concat([df, novo], ignore_index=True))
                st.success("Agendado!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao gravar: {e}")

st.divider()
st.subheader("📋 Grade de Ocupação")

try:
    df_view = conn.read(worksheet="fila", ttl=0)
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    df_hoje = df_view[df_view['Data'] == data_hoje] if not df_view.empty else pd.DataFrame()

    for hr in horarios_disponiveis:
        cols = st.columns(2)
        for idx, vg in enumerate(["Vaga 1", "Vaga 2"]):
            reserva = df_hoje[(df_hoje['Turno'] == hr) & (df_hoje['Vaga'] == vg)]
            if not reserva.empty:
                cols[idx].error(f"🚫 {hr}\n\n{reserva.iloc[0]['Nome']}")
            else:
                cols[idx].success(f"✅ {hr}\n\nLivre")
except:
    st.info("Agenda disponível.")
