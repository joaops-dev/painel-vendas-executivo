"""
Painel de Vendas Executivo - Build 1.5.0
Desenvolvido por: João Pedro
Descrição: Dashboard interativo para análise de faturamento, metas e performance de vendedores.
"""
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime
import time

# -----------------------------------------------------------------------------
# 1. SETUP E CONSTANTES
# -----------------------------------------------------------------------------
# Definição das paletas de cores fixas para o Theme Engine do painel
PALETAS = {
    'StarDreamer (Neon)': ['#00D4FF', '#9D50BB', '#6E48AA'],
    'Cyberpunk (Vibrante)': ['#00FF99', '#FF0055', '#0099FF'],
    'Corporate (Sóbrio)': ['#1F77B4', '#FF7F0E', '#2CA02C']
}

# Configurações globais da página (Renderização em Widescreen)
st.set_page_config(page_title = 'Vendas', layout = 'wide')
st.title('Painel de Vendas')

# -----------------------------------------------------------------------------
# 2. EXTRAÇÃO DE DADOS (ETL - Extract)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados():
    """
    Conecta ao banco SQLite local, extrai os dados de vendas
    e converte a coluna de data para o formato datetime.
    Armazenado em cache para otimizar a performance.
    """
    conn = sqlite3.connect('vendas_empresa_teste.db')
    query = 'SELECT * FROM vendas'
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Converte textos para objetos 'datetime', essencial para permitir os cálculos matemáticos do filtro de período (maior/menor que).
    df['data'] = pd.to_datetime(df['data'])
    return df

df = carregar_dados()

# -----------------------------------------------------------------------------
# 3. TRANSFORMAÇÃO E FILTROS (ETL - Transform)
# -----------------------------------------------------------------------------
with st.sidebar.expander('Filtros'):

    data_minima = df['data'].min()
    data_maxima = df['data'].max()

    filtro_data = st.date_input('Período', [data_minima, data_maxima])

    # Garante que o usuário selecionou início e fim antes de aplicar o corte
    if len(filtro_data) == 2:
        data_inicial = filtro_data[0]
        data_final = filtro_data[1]
        df_filtrado = df[(df['data'] >= pd.to_datetime(data_inicial)) & (df['data'] <= pd.to_datetime(data_final))]
    else:
        df_filtrado = df

    opcoes_regiao = df_filtrado['regiao'].unique().tolist()
    filtro_regiao = st.multiselect('Regiões', opcoes_regiao)
    if filtro_regiao:
        df_filtrado = df_filtrado[df_filtrado['regiao'].isin(filtro_regiao)]

    opcoes_produto = df_filtrado['produto'].unique().tolist()
    filtro_produto = st.multiselect('Produtos', opcoes_produto)
    if filtro_produto:
        df_filtrado = df_filtrado[df_filtrado['produto'].isin(filtro_produto)]

    opcoes_vendedor = df_filtrado['vendedor'].unique().tolist()
    filtro_vendedor = st.multiselect('Vendedores', opcoes_vendedor)
    if filtro_vendedor:
        df_filtrado = df_filtrado[df_filtrado['vendedor'].isin(filtro_vendedor)]

# -----------------------------------------------------------------------------
# 4. REGRAS DE NEGÓCIO E KPIs
# -----------------------------------------------------------------------------
# Cálculo dos indicadores principais baseados no DataFrame filtrado
faturamento = df_filtrado['valor'].sum()
quantidade = len(df_filtrado)
ticket_medio = faturamento / quantidade if quantidade > 0 else 0

with st.sidebar.expander('Configurações do Painel'):
    # 4.1 Processar a Tabela de Metas (Invisível, só na memória)
    df_metas = pd.read_csv('metas_equipe.csv')
    vendas_reais = df_filtrado.groupby('vendedor')['valor'].sum().reset_index()
    resultado = pd.merge(vendas_reais, df_metas, on = 'vendedor')
    resultado['porcentagem'] = (resultado['valor'] / resultado['meta_faturamento']) * 100
    resultado_limpo = resultado[['vendedor', 'valor', 'meta_faturamento', 'porcentagem']]

    modo_comparacao = st.radio('Comparar Faturamento com:', ['Meta da Planilha', 'Outro Período'])

    # Lógica 1: Comparação dinâmica baseada na tabela externa de metas.
    if modo_comparacao == 'Meta da Planilha':
        meta_faturamento_global = resultado_limpo['meta_faturamento'].sum()

        porcentagem_global = (faturamento / meta_faturamento_global) * 100 if meta_faturamento_global > 0 else 0

        diferenca_faturamento = faturamento - meta_faturamento_global
        diferenca_quantidade = diferenca_ticket_medio = 0

    # Lógica 2: Comparação Histórica (Período vs Período)     
    else:
        filtro_comparacao = st.date_input('Período de Comparação', [data_minima, data_maxima])

        if len(filtro_comparacao) == 2:
            data_inicial_comp = filtro_comparacao[0]
            data_final_comp = filtro_comparacao[1]

            # Recria o corte temporal para o período do passado
            df_comparacao = df[(df['data'] >= pd.to_datetime(data_inicial_comp)) & (df['data'] <= pd.to_datetime(data_final_comp))]

            # Replica os filtros categóricos atuais para não comparar "laranjas com maçãs"
            if filtro_regiao:
                df_comparacao = df_comparacao[df_comparacao['regiao'].isin(filtro_regiao)]
            if filtro_produto:
                df_comparacao = df_comparacao[df_comparacao['produto'].isin(filtro_produto)]
            if filtro_vendedor:
                df_comparacao = df_comparacao[df_comparacao['vendedor'].isin(filtro_vendedor)]

            # Cálculos do período passado
            faturamento_comparacao = df_comparacao['valor'].sum()
            quantidade_comparacao = len(df_comparacao)
            # Prevenção de divisão por zero caso o passado não tenha vendas
            ticket_medio_comparacao = faturamento_comparacao / quantidade_comparacao if quantidade_comparacao > 0 else 0

            # Geração dos Deltas
            diferenca_faturamento = faturamento - faturamento_comparacao
            diferenca_quantidade = quantidade - quantidade_comparacao
            diferenca_ticket_medio = ticket_medio - ticket_medio_comparacao
        else:
            diferenca_faturamento = diferenca_quantidade = diferenca_ticket_medio = 0

# -----------------------------------------------------------------------------
# 5. RENDERIZAÇÃO DA INTERFACE VISUAL
# -----------------------------------------------------------------------------
# Menu de UX/UI (Renderizado na Sidebar)
with st.sidebar.expander('Personalização'):
    # Uso do sorted() para organizar os nomes dos temas em ordem alfabética
    tema_escolhido = st.selectbox('Paleta de Cores', sorted(list(PALETAS.keys())))

cor_atual = PALETAS[tema_escolhido]

with st.sidebar.expander('Exportar Dados'):
    csv_dados = df_filtrado.to_csv(index = False).encode('utf-8-sig')
    st.download_button('Baixar Planilha', csv_dados, 'relatorio_vendas.csv', 'text/csv')

# Renderização do Topo (Métricas Executivas)
col_kpi_faturamento, col_kpi_qtd, col_kpi_ticket = st.columns(3)
col_kpi_faturamento.metric('Faturamento Total', f'R$ {faturamento:,.2f}', delta = f'{diferenca_faturamento:,.2f}')
col_kpi_qtd.metric('Qntd. de Vendas', quantidade, delta = f'{diferenca_quantidade:,.2f}')
col_kpi_ticket.metric('Ticket Médio', f'R$ {ticket_medio:,.2f}', delta = f'{diferenca_ticket_medio:,.2f}')

if modo_comparacao == 'Meta da Planilha':
    st.markdown('### 🏆 Progresso da Meta Global')

    progresso_visual = min(porcentagem_global, 100)

    barra_html = f'''
        <div style = "background-color: #2e2e2e; border-radius: 10px; width: 100%; height: 25px;">
            <div  style = "background-color: {cor_atual[1]}; width: {progresso_visual}%; height: 25px; border-radius: 10px; text-align: center; color: white; font-weight: bold; line-height: 25px;">
                {porcentagem_global:.1f}%
            </div>
        </div>
        <br>
    '''
    
    st.markdown(barra_html, unsafe_allow_html = True)

st.markdown('---')

# Renderização do Gráfico Principal (Temporal Nativo)
st.subheader('Faturamento ao longo do tempo')
faturamento_por_data = df_filtrado.groupby('data')['valor'].sum()
st.line_chart(faturamento_por_data, color = cor_atual[0])

# Criação de colunas virtuais para otimizar o espaço em telas Widescreen e evitar rolagem excessiva da página.
col_graf_vendedor_qtd, col_graf_vendedor = st.columns(2)

col_graf_vendedor_qtd.subheader('Quantidade por Vendedor')
tabela_qtd_vendedores = df_filtrado['vendedor'].value_counts().reset_index(name = 'quantidade').sort_values(by = 'quantidade', ascending = True)
fig_qtd_vendedores = px.bar(tabela_qtd_vendedores, x = 'quantidade', y = 'vendedor', orientation = 'h', color_discrete_sequence = [cor_atual[2]])
col_graf_vendedor_qtd.plotly_chart(fig_qtd_vendedores, width = 'stretch')

col_graf_vendedor.subheader('Faturamento por Vendedor')
tabela_vendedores = df_filtrado.groupby('vendedor')['valor'].sum().reset_index().sort_values(by = 'valor', ascending = True)
fig_vendedores = px.bar(tabela_vendedores, x =  'valor', y = 'vendedor', orientation = 'h', color_discrete_sequence = [cor_atual[2]])
col_graf_vendedor.plotly_chart(fig_vendedores, width = 'stretch')

# Nova Linha do Grid
col_graf_regiao, col_graf_produto = st.columns(2)

col_graf_regiao.subheader('Faturamento por Regiões')
tabela_regioes = df_filtrado.groupby('regiao')['valor'].sum().reset_index()
fig_regioes = px.pie(tabela_regioes, values = 'valor', names = 'regiao', hole = 0.4, color_discrete_sequence = cor_atual)
col_graf_regiao.plotly_chart(fig_regioes, width = 'stretch')

col_graf_produto.subheader('Faturamento por Produtos')
tabela_produtos = df_filtrado.groupby('produto')['valor'].sum().reset_index().sort_values(by = 'valor', ascending = True)
fig_produtos = px.bar(tabela_produtos, x = 'valor', y = 'produto', orientation = 'h', color_discrete_sequence = [cor_atual[2]])
col_graf_produto.plotly_chart(fig_produtos, width = 'stretch')

st.markdown('---')
with st.expander('Acompanhamento de Metas'):
    st.dataframe(
        resultado_limpo,
        width = 'stretch',
        column_config = {
            'vendedor': 'Vendedor',
            'valor': st.column_config.NumberColumn('Faturamento Real', format = 'R$ %.2f'),
            'meta_faturamento': st.column_config.NumberColumn('Meta', format = 'R$ %.2f'),
            'porcentagem': st.column_config.ProgressColumn(
                'Progresso da Meta',
                format = '%.1f%%',
                min_value = 0,
                max_value = 100
            )
        },
        hide_index = True
    )

# Oculta a tabela bruta em um expander para manter a interface limpa, servindo apenas para auditoria de dados pelo usuário.
with st.expander('Visualizar Tabela de Dados Completa'):
    st.subheader(f'Mostrando {len(df_filtrado)} Vendas')
    st.dataframe(df_filtrado, width = 'stretch', hide_index = True)

st.sidebar.markdown('---')
senha_gestor = st.sidebar.text_input('Modo Gestor (Senha):', type = 'password')

if senha_gestor == st.secrets['senha_admin']:
    with st.sidebar.expander('Registrar Nova Venda'):
        with st.form('form_nova_venda'):
            # 1. Aqui entram os campos de preenchimento (ex: st.text_input, st.number_input)
            nova_data = st.date_input('Escolha a Data:', datetime.date.today())

            lista_vendedores = df['vendedor'].unique().tolist()
            novo_vendedor = st.selectbox('Escolha o Vendedor:', lista_vendedores)

            lista_produtos = df['produto'].unique().tolist()
            novo_produto = st.selectbox('Escolha o Produto:', lista_produtos)

            lista_regioes = df['regiao'].unique().tolist()
            nova_regiao = st.selectbox('Escolha a Região:', lista_regioes)

            novo_valor = st.number_input('Escolha o Valor:', min_value = 0.0, step = 100.0, format = '%.2f')

            # 2. O botão de envio do formulário
            botao_salvar = st.form_submit_button('Salvar Venda')

            if botao_salvar:
                conn_form = sqlite3.connect('vendas_empresa_teste.db')
                cursor_form = conn_form.cursor()

                query_form = 'INSERT INTO vendas (data, vendedor, produto, valor, regiao) VALUES (?, ?, ?, ?, ?)'
                valores_form = (nova_data, novo_vendedor, novo_produto, novo_valor, nova_regiao)

                cursor_form.execute(query_form, valores_form)
                conn_form.commit()

                conn_form.close()
                st.success('Venda registrada com sucesso!')

                time.sleep(1.5)

                carregar_dados.clear()
                st.rerun()

    with st.expander('Área do Gestor: Gerenciar Vendas'):
        st.subheader('Auditoria de Vendas Suspeitas')
        st.markdown('---')
        st.subheader('Excluir Registro')

        id_da_venda = st.number_input('Digite o ID da Venda:', min_value = 1, step = 1)
        botao_deletar = st.button('Cancelar Venda')

        if botao_deletar:
            conn_deletar = sqlite3.connect('vendas_empresa_teste.db')
            cursor_deletar = conn_deletar.cursor()

            query_deletar = 'DELETE FROM vendas WHERE id_venda = ?'
            valores_deletar = (id_da_venda, )

            cursor_deletar.execute(query_deletar, valores_deletar)
            conn_deletar.commit()

            conn_deletar.close()
            st.success('Venda cancelada com sucesso!')

            time.sleep(1.5)

            carregar_dados.clear()
            st.rerun()
elif senha_gestor != '':
    st.sidebar.error('Senha Não Reconhecida')
else:
    st.sidebar.info('Insira a senha para habilitar a edição de dados.')

# Rodapé do Sistema
st.sidebar.markdown('---')
st.sidebar.caption('🛠️ Build v1.5.0 | Dev: João Pedro')