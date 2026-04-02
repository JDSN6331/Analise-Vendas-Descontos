"""
Análise de Performance de Vendedores
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_sellers(df: pd.DataFrame) -> dict:
    """
    Realiza análise completa de performance de vendedores.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === RANKING DE VENDEDORES (Vendedor 01) ===
    # Filtrar vendedores válidos
    df_vendedores = df[df['vendedor_01'].str.strip() != ''].copy()
    
    ranking = df_vendedores.groupby(['cod_vendedor_01', 'vendedor_01']).agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    ranking.columns = ['codigo', 'vendedor', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    ranking['ticket_medio'] = ranking['faturamento'] / ranking['qtd_pedidos']
    ranking = ranking.sort_values('faturamento', ascending=False).reset_index(drop=True)
    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['participacao'] = (ranking['faturamento'] / ranking['faturamento'].sum() * 100).round(2)
    ranking['participacao_acum'] = ranking['participacao'].cumsum().round(2)
    
    # Produtividade
    ranking['pedidos_por_cliente'] = (ranking['qtd_pedidos'] / ranking['qtd_clientes']).round(2)
    
    results['ranking_vendedores'] = ranking
    
    # === TOP 20 VENDEDORES ===
    results['top_20_vendedores'] = ranking.head(20)
    
    # === ESTATÍSTICAS ===
    results['stats'] = {
        'total_vendedores': len(ranking),
        'media_faturamento': ranking['faturamento'].mean(),
        'mediana_faturamento': ranking['faturamento'].median(),
        'vendedor_top': ranking.iloc[0]['vendedor'] if len(ranking) > 0 else 'N/A',
        'faturamento_top': ranking.iloc[0]['faturamento'] if len(ranking) > 0 else 0,
        'media_clientes_por_vendedor': ranking['qtd_clientes'].mean(),
        'media_pedidos_por_vendedor': ranking['qtd_pedidos'].mean(),
    }
    
    # === ANÁLISE DE QUARTIS ===
    q1 = ranking['faturamento'].quantile(0.25)
    q2 = ranking['faturamento'].quantile(0.50)
    q3 = ranking['faturamento'].quantile(0.75)
    
    def classificar_vendedor(valor):
        if valor >= q3:
            return 'Top Performers'
        elif valor >= q2:
            return 'Acima da Média'
        elif valor >= q1:
            return 'Abaixo da Média'
        else:
            return 'Precisa Melhorar'
    
    ranking['categoria'] = ranking['faturamento'].apply(classificar_vendedor)
    
    categoria_resumo = ranking.groupby('categoria').agg({
        'codigo': 'count',
        'faturamento': 'sum',
        'qtd_clientes': 'sum'
    }).reset_index()
    categoria_resumo.columns = ['categoria', 'qtd_vendedores', 'faturamento', 'qtd_clientes']
    results['categoria_vendedores'] = categoria_resumo
    
    # === ANÁLISE DE DUPLAS (Vendedor 01 + Vendedor 02) ===
    df_duplas = df[(df['vendedor_01'].str.strip() != '') & (df['vendedor_02'].str.strip() != '')].copy()
    if len(df_duplas) > 0:
        duplas = df_duplas.groupby(['vendedor_01', 'vendedor_02']).agg({
            'preco_total': 'sum',
            'num_pedido': 'nunique'
        }).reset_index()
        duplas.columns = ['vendedor_01', 'vendedor_02', 'faturamento', 'qtd_pedidos']
        duplas = duplas.sort_values('faturamento', ascending=False).head(20)
        results['top_duplas'] = duplas
    else:
        results['top_duplas'] = pd.DataFrame()
    
    # === EVOLUÇÃO MENSAL TOP 5 VENDEDORES ===
    top_5 = ranking.head(5)['codigo'].tolist()
    df_top5 = df_vendedores[df_vendedores['cod_vendedor_01'].isin(top_5)]
    evolucao = df_top5.groupby(['ano_mes', 'vendedor_01']).agg({
        'preco_total': 'sum'
    }).reset_index()
    evolucao.columns = ['periodo', 'vendedor', 'faturamento']
    results['evolucao_top5'] = evolucao
    
    # === VENDEDORES POR FILIAL ===
    vendedor_filial = df_vendedores.groupby(['filial_nome', 'vendedor_01']).agg({
        'preco_total': 'sum'
    }).reset_index()
    vendedor_filial.columns = ['filial', 'vendedor', 'faturamento']
    vendedor_filial = vendedor_filial.sort_values(['filial', 'faturamento'], ascending=[True, False])
    results['vendedores_por_filial'] = vendedor_filial
    
    # === CARTEIRA DE VENDEDORES ===
    carteira_analysis = df_vendedores.groupby('carteira').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'cod_vendedor_01': 'nunique'
    }).reset_index()
    carteira_analysis.columns = ['carteira', 'faturamento', 'qtd_pedidos', 'qtd_vendedores']
    carteira_analysis = carteira_analysis.sort_values('faturamento', ascending=False)
    results['analise_carteira'] = carteira_analysis
    
    return results


def generate_seller_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório de vendedores formatado.
    """
    top = results['top_20_vendedores'].copy()
    top['faturamento_fmt'] = top['faturamento'].apply(lambda x: f"R$ {x:,.2f}")
    top['ticket_medio_fmt'] = top['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
    top['participacao_fmt'] = top['participacao'].apply(lambda x: f"{x:.1f}%")
    
    return top[['posicao', 'codigo', 'vendedor', 'faturamento_fmt', 
                'qtd_pedidos', 'qtd_clientes', 'participacao_fmt']]
