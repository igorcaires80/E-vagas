import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página para Mobile
st.set_page_config(page_title="E-Vaga: Agenda", page_icon="⚡", layout="centered")

# Conexão Segura com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lista Oficial de Usuários e Veículos
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

# Janelas de Horário (Encerramento às 19h)
horarios_disponiveis = [
    "07:00 - 10:00", 
    "10:00 - 13:00", 
    "13:00 - 16:00", 
    "16:00 - 19:00"
]

st.title("⚡ Agenda de Carregamento")
st.markdown("---")

# --- FORMULÁRIO DE AGENDAMENTO ---
st.subheader("Fazer Reserva")
nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

if nome_sel:
    st.info(f"🚗 {usuarios[nome_sel]}")
    horario_sel = st.select_slider("Escolha a janela de horário:", options=horarios_disponiveis)
    vaga_sel = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        try:
            df_existente = conn.read(worksheet="fila", ttl="0s")
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            
            # Verifica se o slot está ocupado
            conflito = df_existente[
                (df_existente['Turno'] == horario_sel) & 
                (df_existente['Vaga'] == vaga_sel) & 
                (df_existente['Data'] == data_hoje)
            ]
            
            if not conflito.empty:
                st.error(f"A {vaga_sel} já está reservada para {horario_sel} por {conflito.iloc[0]['Nome']}.")
            else:
                novo_registro = pd.DataFrame([{
                    "Nome": nome_sel,
                    "Vaga": vaga_sel,
                    "Turno": horario_sel,
                    "Data": data_hoje
                }])
                updated_df = pd.concat([df_existente, novo_registro], ignore_index=True)
                conn.update(worksheet="fila", data=updated_df)
                st.success("✅ Agendado com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao conectar com a planilha. Verifique os Secrets.")

st.divider()

# --- GRADE DE OCUPAÇÃO VISUAL ---
st.subheader("📋 Grade de Ocupação (Hoje)")

try:
    df_view = conn.read(worksheet="fila", ttl="0s")
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    if df_view is not None and not df_view.empty:
        df_hoje = df_view[df_view['Data'] == data_atual]
    else:
        df_hoje = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])

    # Exibição em Cards Verdes/Vermelhos
    for hr in horarios_disponiveis:
        col1, col2 = st.columns(2)
        vagas = {"Vaga 1": col1, "Vaga 2": col2}
        
        for vg, col in vagas.items():
            reserva = df_hoje[(df_hoje['Turno'] == hr) & (df_hoje['Vaga'] == vg)]
            if not reserva.empty:
                col.error(f"🚫 {hr}\n\n**{reserva.iloc[0]['Nome']}**")
            else:
                col.success(f"✅ {hr}\n\nDisponível")

except:
    st.info("Agenda disponível. Faça o primeiro check-in.")

# --- PAINEL DE CONTROLE (ADMIN) ---
with st.expander("⚙️ Administração"):
    if st.button("Zerar Agenda (Limpar Planilha)"):
        vazio = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])
        conn.update(worksheet="fila", data=vazio)
        st.success("Agenda zerada!")
        st.rerun()
