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
