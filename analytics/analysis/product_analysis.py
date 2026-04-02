"""
Análise de Portfólio de Produtos (Curva ABC)
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_products(df: pd.DataFrame) -> dict:
    """
    Realiza análise completa de produtos incluindo Curva ABC.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === CURVA ABC DE PRODUTOS ===
    produto_ranking = df.groupby(['cod_produto', 'produto']).agg({
        'preco_total': 'sum',
        'quantidade': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    produto_ranking.columns = ['codigo', 'produto', 'faturamento', 'quantidade', 'qtd_pedidos']
    produto_ranking = produto_ranking.sort_values('faturamento', ascending=False).reset_index(drop=True)
    
    # Calcular percentuais
    total_faturamento = produto_ranking['faturamento'].sum()
    produto_ranking['percentual'] = (produto_ranking['faturamento'] / total_faturamento * 100).round(4)
    produto_ranking['percentual_acum'] = produto_ranking['percentual'].cumsum().round(4)
    
    # Classificação ABC
    def classificar_abc(pct_acum):
        if pct_acum <= 80:
            return 'A'
        elif pct_acum <= 95:
            return 'B'
        else:
            return 'C'
    
    produto_ranking['curva'] = produto_ranking['percentual_acum'].apply(classificar_abc)
    produto_ranking['posicao'] = range(1, len(produto_ranking) + 1)
    results['curva_abc'] = produto_ranking
    
    # === RESUMO DA CURVA ABC ===
    resumo_abc = produto_ranking.groupby('curva').agg({
        'codigo': 'count',
        'faturamento': 'sum',
        'quantidade': 'sum'
    }).reset_index()
    resumo_abc.columns = ['curva', 'qtd_produtos', 'faturamento', 'quantidade']
    resumo_abc['pct_produtos'] = (resumo_abc['qtd_produtos'] / resumo_abc['qtd_produtos'].sum() * 100).round(1)
    resumo_abc['pct_faturamento'] = (resumo_abc['faturamento'] / resumo_abc['faturamento'].sum() * 100).round(1)
    results['resumo_abc'] = resumo_abc
    
    # === TOP 20 PRODUTOS ===
    results['top_20_produtos'] = produto_ranking.head(20)
    
    # === ANÁLISE POR CATEGORIA ===
    categoria_analysis = df.groupby('cat_limite_credito').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'cod_produto': 'nunique'
    }).reset_index()
    categoria_analysis.columns = ['categoria', 'faturamento', 'qtd_pedidos', 'qtd_produtos']
    categoria_analysis['participacao'] = (categoria_analysis['faturamento'] / categoria_analysis['faturamento'].sum() * 100).round(2)
    categoria_analysis = categoria_analysis.sort_values('faturamento', ascending=False)
    results['analise_categoria'] = categoria_analysis
    
    # === PRODUTOS SEM MOVIMENTAÇÃO RECENTE ===
    data_corte = df['data_pedido'].max() - pd.Timedelta(days=90)
    produtos_recentes = df[df['data_pedido'] >= data_corte]['cod_produto'].unique()
    todos_produtos = df['cod_produto'].unique()
    produtos_sem_mov = [p for p in todos_produtos if p not in produtos_recentes]
    
    results['stats'] = {
        'total_produtos': len(todos_produtos),
        'produtos_classe_a': len(produto_ranking[produto_ranking['curva'] == 'A']),
        'produtos_classe_b': len(produto_ranking[produto_ranking['curva'] == 'B']),
        'produtos_classe_c': len(produto_ranking[produto_ranking['curva'] == 'C']),
        'produtos_sem_mov_90d': len(produtos_sem_mov),
        'ticket_medio_produto': df['preco_total'].mean(),
        'produto_mais_vendido': produto_ranking.iloc[0]['produto'] if len(produto_ranking) > 0 else 'N/A',
        'faturamento_produto_top': produto_ranking.iloc[0]['faturamento'] if len(produto_ranking) > 0 else 0,
    }
    
    # === EVOLUÇÃO MENSAL TOP 5 PRODUTOS ===
    top_5_produtos = produto_ranking.head(5)['codigo'].tolist()
    df_top5 = df[df['cod_produto'].isin(top_5_produtos)]
    evolucao = df_top5.groupby(['ano_mes', 'produto']).agg({
        'preco_total': 'sum'
    }).reset_index()
    results['evolucao_top5'] = evolucao
    
    return results


def generate_abc_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório da Curva ABC formatado.
    """
    abc = results['curva_abc'].head(50).copy()
    abc['faturamento_fmt'] = abc['faturamento'].apply(lambda x: f"R$ {x:,.2f}")
    abc['percentual_fmt'] = abc['percentual'].apply(lambda x: f"{x:.2f}%")
    abc['percentual_acum_fmt'] = abc['percentual_acum'].apply(lambda x: f"{x:.2f}%")
    
    return abc[['posicao', 'codigo', 'produto', 'faturamento_fmt', 
                'quantidade', 'percentual_fmt', 'percentual_acum_fmt', 'curva']]
