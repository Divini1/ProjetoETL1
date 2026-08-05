from pathlib import Path
import pandas as pd
import streamlit as st


# CONFIGURAÇÕES E CAMINHOS


CUSTOMER_PARQUET_PATH = Path(r"C:\Users\Divini\Documents\projetos\projeto etl1\output data\customer_clean.parquet")
ITEM_PARQUET_PATH = Path(r"C:\Users\Divini\Documents\projetos\projeto etl1\output data\item_clean.parquet")



# FUNÇÕES DE CARREGAMENTO E FORMATAÇÃO

@st.cache_data(show_spinner="Lendo e cruzando dados...")
def load_data() -> pd.DataFrame:
    # Lê os dois arquivos Parquet usando as constantes definidas acima
    df_customer = pd.read_parquet(CUSTOMER_PARQUET_PATH)
    df_item = pd.read_parquet(ITEM_PARQUET_PATH)
    
    # Garante conversão da chave de junção para string
    df_customer["Customer ID"] = df_customer["Customer ID"].astype(str)
    df_item["Customer ID"] = df_item["Customer ID"].astype(str)
    
    # Faz o cruzamento usando o ID do Cliente
    df_merged = pd.merge(df_item, df_customer, on="Customer ID", how="inner")
    
    # TRADUÇÃO DOS NOMES DAS COLUNAS
    df_merged = df_merged.rename(columns={
        "Category": "Categoria",
        "Gender": "Gênero",
        "Season": "Estação"
    })
    
    # TRADUÇÃO DOS ITENS 
    # Traduzindo Categorias de Produtos
    
    mapa_categorias = {
        "ACCESSORIES": "Acessórios",
        "CLOTHING": "Roupas",
        "FOOTWEAR": "Calçados",
        "OUTERWEAR": "Casacos / Roupas de Frio",
        "ELECTRONICS": "Eletrônicos"
    }
    df_merged["Categoria"] = df_merged["Categoria"].replace(mapa_categorias)

    # Traduzindo Gênero
    mapa_genero = {
        "Male": "Masculino",
        "Female": "Feminino",
        "Other": "Outro"
    }
    df_merged["Gênero"] = df_merged["Gênero"].replace(mapa_genero)

    # Traduzindo Estações do Ano
    mapa_estacoes = {
        "Spring": "Primavera",
        "Summer": "Verão",
        "Autumn": "Outono",
        "Fall": "Outono",
        "Winter": "Inverno"
    }
    df_merged["Estação"] = df_merged["Estação"].replace(mapa_estacoes)
    
    return df_merged

def format_currency(value: float) -> str:
    # Formata para padrão brasileiro: R$ 1.234,56
    value_str = f"{value:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"R$ {value_str}"

def format_int(value: int) -> str:
    return f"{value:,}".replace(",", ".")



# BARRA LATERAL (FILTROS)

def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros Analíticos")

    # Filtro de Faixa Etária
    faixa_options = sorted(df["Faixa Etaria"].dropna().unique().tolist())
    selected_faixas = st.sidebar.multiselect(
        "Faixa Etária",
        options=faixa_options,
        default=faixa_options,
    )

    # Filtro de Categoria
    category_options = sorted(df["Categoria"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Categoria de Produto",
        options=category_options,
        default=category_options,
    )

    # Filtro de Gênero
    gender_options = sorted(df["Gênero"].dropna().unique().tolist())
    selected_genders = st.sidebar.multiselect(
        "Gênero do Cliente",
        options=gender_options,
        default=gender_options,
    )
    
    # Filtro de Estação do Ano
    season_options = sorted(df["Estação"].dropna().unique().tolist())
    selected_seasons = st.sidebar.multiselect(
        "Estação do Ano",
        options=season_options,
        default=season_options,
    )

    # Aplicação dos filtros com as colunas corrigidas
    filtered_df = df[
        df["Faixa Etaria"].isin(selected_faixas)
        & df["Categoria"].isin(selected_categories)
        & df["Gênero"].isin(selected_genders)
        & df["Estação"].isin(selected_seasons)
    ]
    
    return filtered_df



# APLICATIVO PRINCIPAL 

def main() -> None:
    st.set_page_config(
        page_title="Dashboard Varejo - ETL",
        page_icon="🛍️",
        layout="wide",
    )

    st.title("🛍️ Dashboard Analítico de Varejo")
    st.markdown(
        """
        Análise interativa cruzando dados demográficos de clientes e histórico de compras.
        """
    )

    # Carrega e filtra
    try:
        df = load_data()
    except FileNotFoundError:
        st.error(f"Arquivos Parquet não encontrados. Verifique os caminhos configurados.")
        st.stop()
        
    filtered_df = filter_data(df)

    if filtered_df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        st.stop()

    # MÉTRICAS GERAIS 
    st.subheader("Resumo Geral")
    col1, col2, col3, col4, col5 = st.columns(5)

    total_items = len(filtered_df)
    unique_customers = filtered_df["Customer ID"].nunique()
    total_revenue = float(filtered_df["Purchase Amount (BRL)"].sum())
    avg_ticket = total_revenue / unique_customers if unique_customers > 0 else 0
    avg_rating = float(filtered_df["Review Rating"].mean())

    col1.metric("Itens Vendidos", format_int(total_items))
    col2.metric("Clientes Únicos", format_int(unique_customers))
    col3.metric("Receita Total", format_currency(total_revenue))
    col4.metric("Ticket Médio/Cliente", format_currency(avg_ticket))
    col5.metric("Avaliação Média", f"{avg_rating:.1f} ⭐")

    # ABAS ANALÍTICAS
    tab_categoria, tab_demografico, tab_pagamento, tab_local = st.tabs(
        ["Por Categoria", "Perfil Demográfico", "Pagamento e Envio", "Por Localização"]
    )

    # ABA 1: Categoria
    with tab_categoria:
        cat_df = (
            filtered_df.groupby("Categoria", as_index=True) # <-- CORRIGIDO
            .agg(
                itens_vendidos=("Item Purchased", "count"),
                receita_total=("Purchase Amount (BRL)", "sum"),
                avaliacao_media=("Review Rating", "mean"),
            )
            .sort_values(by="receita_total", ascending=False)
            .round(2)
        )
        
        c1, c2 = st.columns(2)
        c1.bar_chart(cat_df["receita_total"], use_container_width=True)
        c2.dataframe(cat_df, use_container_width=True)

    # ABA 2: Demográfico
    with tab_demografico:
        dem_df = (
            filtered_df.groupby("Faixa Etaria", as_index=True, observed=True)
            .agg(
                quantidade_compras=("Customer ID", "count"),
                receita=("Purchase Amount (BRL)", "sum"),
            )
        )
        
        c1, c2 = st.columns(2)
        c1.bar_chart(dem_df["quantidade_compras"], use_container_width=True)
        
        # Agrupamento por Gênero
        gender_df = filtered_df.groupby("Gênero")["Purchase Amount (BRL)"].sum() # <-- CORRIGIDO
        c2.bar_chart(gender_df, use_container_width=True)

    # ABA 3: Pagamentos
    with tab_pagamento:
        pay_df = (
            filtered_df.groupby("Payment Method", as_index=True)
            .agg(
                transacoes=("Customer ID", "count"),
                receita_gerada=("Purchase Amount (BRL)", "sum"),
            )
            .sort_values(by="transacoes", ascending=False)
        )
        
        st.bar_chart(pay_df["transacoes"], use_container_width=True)
        st.dataframe(pay_df, use_container_width=True)

    # ABA 4: Localização
    with tab_local:
        loc_df = (
            filtered_df.groupby("Location", as_index=True)
            .agg(
                clientes_unicos=("Customer ID", "nunique"),
                receita_estado=("Purchase Amount (BRL)", "sum"),
            )
            .sort_values(by="receita_estado", ascending=False)
        )
        
        st.dataframe(loc_df, use_container_width=True)


if __name__ == "__main__":
    main()