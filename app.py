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

# --- TÍTULO E SUBTÍTULO ---
st.title("⚡ E-Vagas EV")
st.subheader("Seu APP de reservas de vagas de carregamento no CNJ")
st.divider()

# --- INSTRUÇÕES DE AGENDAMENTO ---
texto_instrucoes = (
    "**Como agendar o seu carregamento:**\n"
    "1. Verifique na **Grade de Hoje** (abaixo) quais horários e vagas estão livres.\n"
    "2. Selecione o seu nome na lista.\n"
    "3. Escolha a janela de horário e a vaga desejada.\n"
    "4. Clique em **Confirmar Agendamento**.\n\n"
    "**Obs. Todos os dias a fila é zerada e o agendamento é disponibilizado novamente às 10h.**"
)
st.markdown(texto_instrucoes)
st.divider()

# --- REGRA DE NEGÓCIO: BLOQUEIO ANTES DAS 10H ---
if hora_atual < 10:
    st.warning("⏳ Bom dia! A marcação de vagas só é liberada diariamente a partir das **10h da manhã**.")
    st.info(f"🕒 Horário atual do sistema: {agora.strftime('%H:%M')}")
else:
    st.subheader("Fazer Reserva")
    nome = st.selectbox("Quem é você?", [""] + list(usuarios.keys()))

    if nome:
        st.success(f"🚗 **Seu Veículo:** {usuarios[nome]}")
        
        horario = st.radio("Escolha o Horário:", options=horarios)
        vaga = st.radio("Selecione a Vaga:", ["Vaga 1", "Vaga 2"], horizontal=True)

        if st.button("Confirmar Agendamento"):
            try:
                df = conn.read(worksheet="fila", ttl=0)
                if df is None or df.empty:
                    df = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])
                
                if not df[(df['Turno'] == horario) & (df['Vaga'] == vaga) & (df['Data'] == hoje)].empty:
                    st.error("⚠️ Este horário já está ocupado nesta vaga!")
                else:
                    novo = pd.DataFrame([{"Nome": nome, "Vaga": vaga, "Turno": horario, "Data": hoje}])
                    conn.update(worksheet="fila", data=pd.concat([df, novo], ignore_index=True))
                    st.success("✅ Agendamento realizado com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao agendar: {e}")

st.divider()
st.subheader("📋 Grade de Hoje")

try:
    df_view = conn.read(worksheet="fila", ttl=0)
    df_hoje = df_view[df_view['Data'] == hoje] if df_view is not None else pd.DataFrame()
    
    for h in horarios:
        c1, c2 = st.columns(2)
        for i, v in enumerate(["Vaga 1", "Vaga 2"]):
            res = df_hoje[(df_hoje['Turno'] == h) & (df_hoje['Vaga'] == v)]
            col = [c1, c2][i]
            if not res.empty:
                nome_reserva = res.iloc[0]['Nome']
                carro_reserva = usuarios.get(nome_reserva, "")
                # Exibindo o nome em destaque e o carro/placa logo abaixo
                col.error(f"🚫 {h}\n\n**{nome_reserva}**\n\n🚗 {carro_reserva}")
            else:
                col.success(f"✅ {h}\n\nLivre")
except Exception:
    st.info("Agenda pronta para o primeiro registro.")

# --- PAINEL DE OCORRÊNCIAS (NOVO) ---
st.divider()
st.subheader("🚨 Reportar Uso Indevido")
st.write("Alguém estacionou na vaga errada ou fora do horário? Registre aqui.")

with st.form("form_ocorrencia"):
    reportador = st.selectbox("Seu nome (Quem está reportando):", [""] + list(usuarios.keys()))
    turno_invadido = st.selectbox("Em qual turno ocorreu?", horarios)
    vaga_invadida = st.radio("Em qual vaga?", ["Vaga 1", "Vaga 2"], horizontal=True)
    infrator = st.text_input("Placa ou descrição do carro (ex: BYD Branco placa XYZ):")
    
    if st.form_submit_button("Registrar Ocorrência"):
        if reportador == "":
            st.warning("⚠️ Por favor, selecione seu nome para reportar.")
        elif infrator == "":
            st.warning("⚠️ Por favor, descreva o carro ou a placa do infrator.")
        else:
            try:
                df_oc = conn.read(worksheet="ocorrencias", ttl=0)
                if df_oc is None or df_oc.empty:
                    df_oc = pd.DataFrame(columns=["Data", "Reportado_por", "Vaga", "Turno", "Infrator"])
                
                nova_oc = pd.DataFrame([{
                    "Data": hoje, 
                    "Reportado_por": reportador, 
                    "Vaga": vaga_invadida, 
                    "Turno": turno_invadido, 
                    "Infrator": infrator
                }])
                conn.update(worksheet="ocorrencias", data=pd.concat([df_oc, nova_oc], ignore_index=True))
                st.success("✅ Ocorrência registrada e enviada à administração!")
            except Exception:
                st.error("⚠️ ERRO: Crie uma aba chamada 'ocorrencias' na sua planilha do Google antes de usar esta função.")

# --- PAINEL DE ADMINISTRAÇÃO ---
st.divider()
with st.expander("⚙️ Administração"):
    st.warning("Esta ação limpará a agenda do dia manualmente.")
    if st.button("🗑️ Limpar Fila Agora"):
        df_vazio = pd.DataFrame(columns=["Nome", "Vaga", "Turno", "Data"])
        conn.update(worksheet="fila", data=df_vazio)
        st.success("Fila limpa com sucesso!")
        st.rerun()

