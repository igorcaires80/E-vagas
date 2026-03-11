import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="E-Vaga: Agenda", page_icon="⚡")

conn = st.connection("gsheets", type=GSheetsConnection)

# Lista de usuários (mantida conforme sua lista oficial)
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
st.markdown("Reserve seu horário. **Limite: 3h por veículo.**")

# 1. Seleção de Usuário
nome_sel = st.selectbox("Selecione seu nome:", [""] + list(usuarios.keys()))

# 2. Janelas de Horário ajustadas para encerrar às 19:00
horarios_disponiveis = [
    "07:00 - 10:00", 
    "10:00 - 13:00", 
    "13:00 - 16:00", 
    "16:00 - 19:00"
]

if nome_sel:
    st.caption(f"Veículo: {usuarios[nome_sel]}")
    
    # Seleção da Janela de Horário
    horario_sel = st.select_slider("Escolha sua janela de horário:", options=horarios_disponiveis)
    
    # Seleção da Vaga
    vaga_sel = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

    if st.button("Confirmar Agendamento"):
        df_existente = conn.read(worksheet="fila", ttl=0)
        
        # Verifica se o horário e vaga já estão ocupados para o dia de hoje
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        conflito = df_existente[
            (df_existente['Turno'] == horario_sel) & 
            (df_existente['Vaga'] == vaga_sel) & 
            (df_existente['Data'] == data_hoje)
        ]
        
        if not conflito.empty:
            st.error(f"A {vaga_sel} já está ocupada das {horario_sel}.")
        else:
            novo_registro = pd.DataFrame([{
                "Nome": nome_sel,
                "Vaga": vaga_sel,
                "Turno": horario_sel,
                "Data": data_hoje
            }])
            updated_df = pd.concat([df_existente, novo_registro], ignore_index=True)
            conn.update(worksheet="fila", data=updated_df)
            st.success(f"Agendado! {nome_sel} na {vaga_sel} das {horario_sel}.")
            st.rerun()

st.divider()

# 3. Visualização da Agenda Organizada
st.subheader("📋 Grade de Ocupação (Hoje)")

try:
    df_view = conn.read(worksheet="fila", ttl="0")
    
    # Se a planilha existir mas estiver vazia, cria um DF vazio com colunas
    if df_view is None or df_view.empty:
        df_hoje = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])
    else:
        data_atual = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df_view[df_view['Data'] == data_atual]

    # Exibição dos cards
    for hr in horarios_disponiveis:
        cols = st.columns(2)
        for idx, vg in enumerate(["Vaga 1", "Vaga 2"]):
            reserva = df_hoje[(df_hoje['Turno'] == hr) & (df_hoje['Vaga'] == vg)]
            if not reserva.empty:
                cols[idx].error(f"🚫 {hr}\n\n{reserva.iloc[0]['Nome']}")
            else:
                cols[idx].success(f"✅ {hr}\n\nDisponível")
except Exception as e:
    st.error("Erro ao carregar a agenda. Verifique se a aba 'fila' existe na planilha.")
    st.info("Dica: Certifique-se de que a planilha está compartilhada como 'Editor' para 'Qualquer pessoa com o link'.")

# Botão de Gestão
with st.expander("⚙️ Administração"):
    if st.button("Limpar todos os dados da Planilha"):
        conn.update(worksheet="fila", data=pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"]))
        st.rerun()
