#!/usr/bin/env python3
"""
Dashboard Streamlit para análise de estoque Clipper
Visualiza dados, métricas e inconsistências
Execução: streamlit run app_dashboard.py
"""

import sys
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DATABASE_PATH
from core.database import db_manager
from core.business_rules import estoque_calc
from core.logger import logger

# Configuração da página
st.set_page_config(
    page_title="Dashboard Estoque Clipper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
        }
        .error-card {
            background-color: #ffebee;
            border-left-color: #e53935;
        }
        .success-card {
            background-color: #e8f5e9;
            border-left-color: #43a047;
        }
        .header-div {
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_manager():
    """Retorna instância do gerenciador de banco"""
    return db_manager


@st.cache_data(ttl=300)
def carregar_dados():
    """Carrega dados do banco com cache"""
    try:
        # Carregar dados no calculador
        estoque_calc.carregar_dados()
        
        return {
            "estoque_inicial": estoque_calc.estoque_inicial,
            "movimentos": estoque_calc.movimentos
        }
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None


@st.cache_data(ttl=300)
def get_comparacao():
    """Obtém comparação de estoques com cache"""
    try:
        return estoque_calc.comparar_estoques()
    except Exception as e:
        st.error(f"Erro ao comparar estoques: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_inconsistencias(limiar):
    """Obtém inconsistências com cache"""
    try:
        return estoque_calc.detectar_inconsistencias(limiar_erro=limiar)
    except Exception as e:
        st.error(f"Erro ao detectar inconsistências: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_consumo():
    """Obtém dados de consumo com cache"""
    try:
        return estoque_calc.calcular_consumo_por_produto()
    except Exception as e:
        st.error(f"Erro ao calcular consumo: {e}")
        return pd.DataFrame()


def render_header():
    """Renderiza cabeçalho da página"""
    st.markdown("""
        <div class="header-div">
            <h1>📊 Dashboard de Análise de Estoque Clipper</h1>
            <p>Sistema de visualização e auditoria de inconsistências de estoque</p>
        </div>
    """, unsafe_allow_html=True)


def render_resumo():
    """Renderiza resumo executivo"""
    st.header("📈 Resumo Executivo")
    
    # Carregar dados
    dados = carregar_dados()
    if not dados:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        db_tables = db_manager.get_tables()
        st.metric(
            "Tabelas Carregadas",
            len(db_tables),
            "arquivos DBF"
        )
    
    with col2:
        estoque_inicial = dados["estoque_inicial"]
        if not estoque_inicial.empty:
            try:
                col_qtd = [c for c in estoque_inicial.columns 
                          if 'QTD' in c.upper() or 'ESTOQUE' in c.upper()][0]
                total_est = estoque_inicial[col_qtd].sum()
                st.metric("Estoque Sistema", f"{total_est:,.0f}", "unidades")
            except:
                st.metric("Estoque Sistema", "N/A")
        else:
            st.metric("Estoque Sistema", "N/A")
    
    with col3:
        comparacao = get_comparacao()
        if not comparacao.empty:
            total_calc = comparacao['QUANTIDADE_CALC'].sum()
            st.metric("Estoque Calculado", f"{total_calc:,.0f}", "unidades")
        else:
            st.metric("Estoque Calculado", "N/A")
    
    with col4:
        inconsistencias = get_inconsistencias(limiar_erro=5.0)
        st.metric(
            "Inconsistências",
            len(inconsistencias),
            "produtos com erro"
        )


def render_comparacao():
    """Renderiza aba de comparação de estoques"""
    st.header("🔍 Comparação de Estoques")
    
    comparacao = get_comparacao()
    
    if comparacao.empty:
        st.warning("Sem dados de comparação disponível")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Estatísticas Gerais")
    
    with col2:
        limpar_filtros = st.button("🔄 Limpar Filtros")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_produto = st.text_input("🔎 Filtrar Produto")
    
    with col2:
        min_erro = st.slider("Erro Mínimo (%)", 0.0, 100.0, 0.0)
    
    with col3:
        max_erro = st.slider("Erro Máximo (%)", 0.0, 100.0, 100.0)
    
    # Aplicar filtros
    df_filtrado = comparacao.copy()
    
    if filtro_produto:
        df_filtrado = df_filtrado[
            df_filtrado['PRODUTO'].astype(str).str.contains(
                filtro_produto.upper(), 
                case=False, 
                na=False
            )
        ]
    
    df_filtrado = df_filtrado[
        (df_filtrado['PERCENTUAL_ERRO'].abs() >= min_erro) &
        (df_filtrado['PERCENTUAL_ERRO'].abs() <= max_erro)
    ]
    
    # Exibir tabela
    st.dataframe(
        df_filtrado.style.format({
            'QUANTIDADE_CALC': '{:,.0f}',
            'QUANTIDADE_SISTEMA': '{:,.0f}',
            'DIFERENCA': '{:,.0f}',
            'PERCENTUAL_ERRO': '{:.2f}%'
        }),
        use_container_width=True,
        height=400
    )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Maiores Diferenças")
        top10 = df_filtrado.nlargest(10, 'DIFERENCA')
        
        if not top10.empty:
            fig = px.bar(
                top10,
                x='DIFERENCA',
                y='PRODUTO',
                orientation='h',
                color='DIFERENCA',
                color_continuous_scale='Reds'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribuição de Erros (%)")
        
        if not df_filtrado.empty:
            fig = px.histogram(
                df_filtrado,
                x='PERCENTUAL_ERRO',
                nbins=20,
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(
                xaxis_title="% de Erro",
                yaxis_title="Quantidade de Produtos",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)


def render_inconsistencias():
    """Renderiza aba de inconsistências"""
    st.header("⚠️ Detecção de Inconsistências")
    
    col1, col2 = st.columns(2)
    
    with col1:
        limiar_erro = st.slider(
            "Limiar de Erro para Flagging (%)",
            1.0, 50.0, 5.0, 0.5
        )
    
    with col2:
        st.write("")  # Espaço
    
    inconsistencias = get_inconsistencias(limiar_erro)
    
    if inconsistencias.empty:
        st.success(f"✓ Nenhuma inconsistência encontrada (limiar: {limiar_erro}%)")
        return
    
    # Resumo por criticidade
    col1, col2, col3, col4 = st.columns(4)
    
    criticas = len(inconsistencias[inconsistencias['CRITICIDADE'] == 'CRÍTICA'])
    altas = len(inconsistencias[inconsistencias['CRITICIDADE'] == 'ALTA'])
    medias = len(inconsistencias[inconsistencias['CRITICIDADE'] == 'MÉDIA'])
    baixas = len(inconsistencias[inconsistencias['CRITICIDADE'] == 'BAIXA'])
    
    with col1:
        st.metric("🔴 Crítica", criticas)
    
    with col2:
        st.metric("🟠 Alta", altas)
    
    with col3:
        st.metric("🟡 Média", medias)
    
    with col4:
        st.metric("🟢 Baixa", baixas)
    
    # Tabela de inconsistências
    st.subheader("Produtos com Inconsistências")
    
    st.dataframe(
        inconsistencias.style.format({
            'QUANTIDADE_CALC': '{:,.0f}',
            'QUANTIDADE_SISTEMA': '{:,.0f}',
            'DIFERENCA': '{:,.0f}',
            'PERCENTUAL_ERRO': '{:.2f}%'
        }).background_gradient(
            subset=['CRITICIDADE'],
            cmap='RdYlGn_r'
        ),
        use_container_width=True,
        height=500
    )
    
    # Gráfico de criticidade
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição por Criticidade")
        
        dados_criticos = inconsistencias['CRITICIDADE'].value_counts()
        cores = {'CRÍTICA': '#e53935', 'ALTA': '#fb8c00', 
                'MÉDIA': '#fdd835', 'BAIXA': '#43a047'}
        
        fig = px.pie(
            values=dados_criticos.values,
            names=dados_criticos.index,
            color=dados_criticos.index,
            color_discrete_map=cores
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Scatter: Sistema vs Calculado")
        
        fig = px.scatter(
            inconsistencias,
            x='QUANTIDADE_SISTEMA',
            y='QUANTIDADE_CALC',
            color='CRITICIDADE',
            hover_name='PRODUTO',
            color_discrete_map=cores
        )
        
        # Adicionar linha de perfeição
        max_val = max(
            inconsistencias['QUANTIDADE_SISTEMA'].max(),
            inconsistencias['QUANTIDADE_CALC'].max()
        )
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='Perfeição',
                line=dict(dash='dash', color='gray')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_consumo():
    """Renderiza aba de consumo"""
    st.header("📉 Análise de Consumo")
    
    consumo = get_consumo()
    
    if consumo.empty:
        st.warning("Sem dados de consumo disponível")
        return
    
    # Filtro
    top_n = st.slider("Exibir Top N Produtos", 5, 50, 15)
    
    top_consumo = consumo.nlargest(top_n, 'CONSUMO_TOTAL')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Top {top_n} Produtos por Consumo Total")
        
        fig = px.bar(
            top_consumo,
            x='CONSUMO_TOTAL',
            y='PRODUTO',
            orientation='h',
            color='CONSUMO_TOTAL',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Consumo Médio vs Total")
        
        fig = px.scatter(
            top_consumo,
            x='CONSUMO_MEDIO',
            y='CONSUMO_TOTAL',
            size='NUM_SAIDAS',
            hover_name='PRODUTO',
            color='NUM_SAIDAS',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela
    st.subheader("Detalhes de Consumo")
    st.dataframe(
        consumo.style.format({
            'CONSUMO_TOTAL': '{:,.0f}',
            'NUM_SAIDAS': '{:,}',
            'CONSUMO_MEDIO': '{:,.2f}'
        }),
        use_container_width=True,
        height=400
    )


def render_dados_brutos():
    """Renderiza aba de dados brutos"""
    st.header("📋 Dados Brutos")
    
    # Seletor de tabela
    tabelas = sorted(db_manager.get_tables())
    
    if not tabelas:
        st.warning("Nenhuma tabela disponível")
        return
    
    tabela_selecionada = st.selectbox("Selecionar Tabela", tabelas)
    
    # Carregar dados
    try:
        with db_manager.get_session() as session:
            df = pd.read_sql(f"SELECT * FROM {tabela_selecionada}", session.bind)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Linhas", len(df))
        
        with col2:
            st.metric("Colunas", len(df.columns))
        
        with col3:
            st.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Filtros
        st.subheader("Filtros")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Busca de texto
            texto_busca = st.text_input("🔍 Buscar Texto")
        
        with col2:
            # Limite de linhas
            limit_linhas = st.number_input("Máximo de Linhas", 10, 1000, 100)
        
        with col3:
            st.write("")  # Espaço
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if texto_busca:
            mask = df.astype(str).apply(
                lambda x: x.str.contains(texto_busca, case=False, na=False).any(),
                axis=1
            )
            df_filtrado = df_filtrado[mask]
        
        df_filtrado = df_filtrado.head(limit_linhas)
        
        # Exibir dados
        st.dataframe(df_filtrado, use_container_width=True, height=500)
        
        # Download
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{tabela_selecionada}.csv",
            mime="text/csv"
        )
    
    except Exception as e:
        st.error(f"Erro ao carregar tabela: {e}")


def main():
    """Função principal"""
    
    render_header()
    
    # Verificar se banco existe
    if not DATABASE_PATH.exists():
        st.error("❌ Banco de dados não encontrado!")
        st.info("Execute primeiro: `python etl_dbf.py`")
        return
    
    # Abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Resumo",
        "🔍 Comparação",
        "⚠️ Inconsistências",
        "📉 Consumo",
        "📋 Dados"
    ])
    
    with tab1:
        render_resumo()
    
    with tab2:
        render_comparacao()
    
    with tab3:
        render_inconsistencias()
    
    with tab4:
        render_consumo()
    
    with tab5:
        render_dados_brutos()
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: gray; font-size: 12px;">
            <p>Clipper DBF Analytics Dashboard | Desenvolvido com Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
