import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página para ficar bem no celular (WhatsApp)
st.set_page_config(page_title="E-Vaga: Gestão", page_icon="⚡")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- A SUA LISTA DE INTERESSADOS ---
usuarios = {
    "Johana": "BYD King Branco (UIV6C56)",
    "Andréia": "BYD Yuan Pro Branco (PBZ6D66)",
    "Cinthya": "ORA/BYD King (UIV4J70 / PBZ7E00)",
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
    "Gabriela": "GWM ORA Branco (UJL2D89)"
}

st.title("⚡ Gestão de Vagas EV")

# Seção de Check-in
st.subheader("Fazer Check-in")
nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

if nome_sel:
    veiculo_info = usuarios[nome_sel]
    st.info(f"**Veículo:** {veiculo_info}")
    
    turno = st.radio("Turno de uso:", ["Manhã", "Tarde"], horizontal=True)
    
    if st.button("Confirmar Entrada na Fila"):
        # Lógica para salvar na planilha
        df_existente = conn.read(worksheet="fila", ttl=0)
        
        # Extrair placa e modelo do texto
        try:
            placa = veiculo_info.split("(")[1].replace(")", "")
            modelo = veiculo_info.split("(")[0]
        except:
            placa = "N/A"
            modelo = veiculo_info

        novo_registro = pd.DataFrame([{
            "Nome": nome_sel,
            "Veiculo": modelo,
            "Placa": placa,
            "Turno": turno,
            "Hora_Checkin": datetime.now().strftime("%H:%M")
        }])
        
        updated_df = pd.concat([df_existente, novo_registro], ignore_index=True)
        conn.update(worksheet="fila", data=updated_df)
        st.success(f"Check-in realizado! Você está na fila.")
        st.rerun()

st.divider()

# Exibição da Fila em Tempo Real
st.subheader("📋 Status das Vagas")
try:
    df_fila = conn.read(worksheet="fila", ttl=0)
    if not df_fila.empty:
        for i, row in df_fila.iterrows():
            if i < 2:
                st.success(f"🔋 **VAGA {i+1}: {row['Nome']}** ({row['Turno']})")
            else:
                st.warning(f"⏳ {i+1}º da Fila: {row['Nome']} ({row['Turno']})")
    else:
        st.info("Vagas disponíveis no momento.")
except:
    st.info("Aguardando o primeiro check-in...")

# Área do Gestor (Igor)
with st.expander("⚙️ Painel do Gestor"):
    if st.button("Limpar Fila (Zerar Dia)"):
        conn.update(worksheet="fila", data=pd.DataFrame(columns=["Nome", "Veiculo", "Placa", "Turno", "Hora_Checkin"]))
        st.rerun()
