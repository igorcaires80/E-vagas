import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-Vagas", page_icon="⚡")

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

# Horários atualizados para iniciar às 10:00
horarios = ["10:00 - 13:00", "13:00 - 16:00", "16:00 - 19:00"]

st.title("⚡ Agenda de Carregamento")

nome = st.selectbox("Quem é você?", [""] + list(usuarios.keys()))

if nome:
    # Destaque do veículo e placa do motorista selecionado
    st.success(f"🚗 **Seu Veículo:** {usuarios[nome]}")
    
    # Seleção por botões (radio) em vez de linha horizontal
    horario = st.radio("Escolha o Horário:", options=horarios)
    vaga = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        try:
            df = conn.read(worksheet="fila", ttl=0)
            hoje = datetime.now().strftime("%d/%m/%Y")
            
            if df is None or df.empty:
                df = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])
            
            if not df[(df['Turno'] == horario) & (df['Vaga'] == vaga) & (df['Data'] == hoje)].empty:
                st.error("Este horário já está ocupado nesta vaga!")
            else:
                novo = pd.DataFrame([{"Nome": nome, "Vaga": vaga, "Turno": horario, "Data": hoje}])
                conn.update(worksheet="fila", data=pd.concat([df, novo], ignore_index=True))
                st.success("Agendamento realizado com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao agendar: {e}")

st.divider()
st.subheader("📋 Grade de Hoje")

try:
    df_view = conn.read(worksheet="fila", ttl=0)
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    df_hoje = df_view[df_view['Data'] == hoje] if df_view is not None else pd.DataFrame()
    
    for h in horarios:
        c1, c2 = st.columns(2)
        for i, v in enumerate(["Vaga 1", "Vaga 2"]):
            res = df_hoje[(df_hoje['Turno'] == h) & (df_hoje['Vaga'] == v)]
            col = [c1, c2][i]
            if not res.empty:
                col.error(f"🚫 {h}\n\n**{res.iloc[0]['Nome']}**")
            else:
                col.success(f"✅ {h}\n\nLivre")
except:
    st.info("Agenda pronta para o primeiro registro.")
