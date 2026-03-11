import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-Vaga: Agenda", page_icon="⚡")

# Conexão com o Google Sheets via Service Account
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

horarios_disponiveis = ["07:00 - 10:00", "10:00 - 13:00", "13:00 - 16:00", "16:00 - 19:00"]

st.title("⚡ Agenda de Carregamento")

# Formulário
nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

if nome_sel:
    horario_sel = st.select_slider("Janela de horário:", options=horarios_disponiveis)
    vaga_sel = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        try:
            df = conn.read(worksheet="fila", ttl="0s")
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            
            # Adiciona colunas se estiver vazio
            if df is None or df.empty:
                df = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])

            conflito = df[(df['Turno'] == horario_sel) & (df['Vaga'] == vaga_sel) & (df['Data'] == data_hoje)]
            
            if not conflito.empty:
                st.error("Horário já ocupado!")
            else:
                novo = pd.DataFrame([{"Nome": nome_sel, "Vaga": vaga_sel, "Turno": horario_sel, "Data": data_hoje}])
                df_final = pd.concat([df, novo], ignore_index=True)
                conn.update(worksheet="fila", data=df_final)
                st.success("Agendado!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

st.divider()
st.subheader("📋 Grade de Ocupação")

try:
    df_view = conn.read(worksheet="fila", ttl="0s")
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    if df_view is not None and not df_view.empty:
        df_hoje = df_view[df_view['Data'] == data_hoje]
    else:
        df_hoje = pd.DataFrame()

    for hr in horarios_disponiveis:
        c1, c2 = st.columns(2)
        vagas_cols = {"Vaga 1": c1, "Vaga 2": c2}
        for v_nome, v_col in vagas_cols.items():
            reserva = df_hoje[(df_hoje['Turno'] == hr) & (df_hoje['Vaga'] == v_nome)]
            if not reserva.empty:
                v_col.error(f"🚫 {hr}\n\n{reserva.iloc[0]['Nome']}")
            else:
                v_col.success(f"✅ {hr}\n\nLivre")
except:
    st.info("Agenda pronta para o primeiro registro.")
