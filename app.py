import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-Vaga: Agenda", page_icon="⚡")

conn = st.connection("gsheets", type=GSheetsConnection)

# Sua lista de usuários permanece a mesma
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

st.title("⚡ Agenda de Carregamento")
st.markdown("Reserve seu horário. **Máximo 3h por veículo.**")

# 1. Seleção de Usuário
nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

# 2. Seleção de Horário (Fila Dinâmica)
horarios_disponiveis = [
    "08:00 - 11:00", "11:00 - 14:00", 
    "14:00 - 17:00", "17:00 - 20:00"
]

if nome_sel:
    # Mostra qual veículo a pessoa está usando
    st.caption(f"Veículo: {usuarios[nome_sel]}")
    
    # Seleção da Janela de Horário
    horario_sel = st.select_slider("Escolha sua janela de horário:", options=horarios_disponiveis)
    
    # Seleção da Vaga (1 ou 2)
    vaga_sel = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        df_existente = conn.read(worksheet="fila", ttl=0)
        
        # Verifica se o horário e vaga já estão ocupados
        conflito = df_existente[(df_existente['Turno'] == horario_sel) & (df_existente['Vaga'] == vaga_sel)]
        
        if not conflito.empty:
            st.error(f"Ops! A {vaga_sel} já está reservada para o horário {horario_sel}.")
        else:
            novo_registro = pd.DataFrame([{
                "Nome": nome_sel,
                "Vaga": vaga_sel,
                "Turno": horario_sel,
                "Data": datetime.now().strftime("%d/%m/%Y")
            }])
            updated_df = pd.concat([df_existente, novo_registro], ignore_index=True)
            conn.update(worksheet="fila", data=updated_df)
            st.success("Horário agendado com sucesso!")
            st.rerun()

st.divider()

# 3. Visualização da Agenda (Tabela Organizadora)
st.subheader("📋 Grade de Horários")
df_view = conn.read(worksheet="fila", ttl=0)

if not df_view.empty:
    # Mostra a lista de forma organizada por horário
    st.table(df_view.sort_values(by="Turno")[["Turno", "Vaga", "Nome"]])
else:
    st.info("Nenhum horário reservado para hoje.")

# Botão de Gestão para o Adm
if st.button("Zerar Agenda (Novo Dia)"):
    conn.update(worksheet="fila", data=pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"]))
    st.rerun()
