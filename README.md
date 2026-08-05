# Pipeline de ETL & Analytics

Projeto de portfólio estruturado com um fluxo completo de engenharia de dados: extração de dados brutos relacionais, limpeza e tratamento avançado em Python (pandas), persistência otimizada em formato Apache Parquet, e exibição de indicadores em um painel interativo em Streamlit.

# Objetivo

Centralizar, limpar e estruturar dados de clientes e transações de comércio eletrônico para análise de comportamento de compra, perfil demográfico, indicadores de receita e métricas de engajamento.

# Fonte dos dados

Os dados têm origem do KAGGLE, compostos por duas bases relacionais principais unificadas por chave única (Customer ID):

    Base de Clientes (customer.csv): Informações demográficas, geográficas, faixas etárias, gênero e status de assinatura.

    Base de Itens (item.csv): Histórico de produtos comprados, categorias, avaliações (Review Rating), formas de pagamento, tipos de envio e valores transacionados.

## Extração e Engenharia de Dados

O processamento inicial e a validação de regras de negócio foram estruturados iterativamente em ambiente Jupyter Notebook (main.ipynb), cobrindo as seguintes etapas de qualidade:

    Identificação de Anomalias: Varredura por valores ausentes (NaN), idades inconsistentes, transações negativas e avaliações fora da escala padrão (1.0 a 5.0).

    Tratamento e Limpeza (Python / Pandas):

        Preenchimento de nulos em variáveis categóricas sem perda de registros (.fillna()).

        Filtros lógicos para remoção de registros inconsistentes e tratamento de IDs duplicados.

        Padronização de strings de texto com .capitalize().

    Transformações e Colunas Calculadas:

        Conversão de moedas (conversão de USD para BRL).

        Criação de faixas etárias segmentadas (pd.cut) e variáveis binárias de engajamento (Is_Subscriber).

        Agrupamentos relacionais (groupby e merge) para calcular o gasto total acumulado e o ticket médio por cliente.

    Carga Otimizada (Apache Parquet):

    Os DataFrames tratados foram exportados para o formato columnar Parquet (utilizando a engine pyarrow), garantindo alta compressão, preservação estrita de tipos e alta performance de leitura.

## Dashboard Interativo (Streamlit)

Para a camada de visualização, foi desenvolvida uma aplicação web em Python utilizando Streamlit, permitindo análises dinâmicas através de filtros laterais e abas temáticas:

    Métricas Principais (KPIs): Total de itens vendidos, clientes únicos alcançados, receita total consolidada, ticket médio e avaliação média de produtos.

    Abas Analíticas:

        Por Categoria: Desempenho de vendas, receita gerada e satisfação por tipo de produto.

        Perfil Demográfico: Comportamento de compra cruzado por faixa etária e gênero.

        Pagamento e Envio: Análise de preferências de meios de transação e modalidades logísticas.

        Por Localização: Distribuição geográfica de clientes e volume financeiro por região.


<img width="1857" height="697" alt="Screenshot 2026-08-04 225329" src="https://github.com/user-attachments/assets/af13e959-769b-4e83-b02e-0bd46493c203" />

