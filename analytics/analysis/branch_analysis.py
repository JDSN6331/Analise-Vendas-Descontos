"""
Análise de Performance por Filial
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_branches(df: pd.DataFrame) -> dict:
    """
    Realiza análise completa de performance por filial.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === RANKING DE FILIAIS ===
    ranking = df.groupby('filial_nome').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    ranking.columns = ['filial', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    ranking['ticket_medio'] = ranking['faturamento'] / ranking['qtd_pedidos']
    ranking = ranking.sort_values('faturamento', ascending=False).reset_index(drop=True)
    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['participacao'] = (ranking['faturamento'] / ranking['faturamento'].sum() * 100).round(2)
    ranking['participacao_acum'] = ranking['participacao'].cumsum().round(2)
    results['ranking_filiais'] = ranking
    
    # === TOP 10 FILIAIS ===
    results['top_10_filiais'] = ranking.head(10)
    
    # === ESTATÍSTICAS GERAIS ===
    results['stats'] = {
        'total_filiais': len(ranking),
        'media_faturamento': ranking['faturamento'].mean(),
        'mediana_faturamento': ranking['faturamento'].median(),
        'desvio_padrao': ranking['faturamento'].std(),
        'filial_top': ranking.iloc[0]['filial'],
        'faturamento_top': ranking.iloc[0]['faturamento'],
    }
    
    # === ANÁLISE POR CATEGORIA DE FILIAL ===
    # Classificar filiais por performance
    q1 = ranking['faturamento'].quantile(0.25)
    q2 = ranking['faturamento'].quantile(0.50)
    q3 = ranking['faturamento'].quantile(0.75)
    
    def classificar_filial(valor):
        if valor >= q3:
            return 'Top Performers'
        elif valor >= q2:
            return 'Acima da Média'
        elif valor >= q1:
            return 'Abaixo da Média'
        else:
            return 'Baixa Performance'
    
    ranking['categoria'] = ranking['faturamento'].apply(classificar_filial)
    results['filiais_por_categoria'] = ranking.groupby('categoria').agg({
        'filial': 'count',
        'faturamento': 'sum'
    }).reset_index()
    results['filiais_por_categoria'].columns = ['categoria', 'qtd_filiais', 'faturamento_total']
    
    # === EVOLUÇÃO MENSAL POR FILIAL (TOP 5) ===
    top_5_filiais = ranking.head(5)['filial'].tolist()
    df_top5 = df[df['filial_nome'].isin(top_5_filiais)]
    evolucao = df_top5.groupby(['ano_mes', 'filial_nome']).agg({
        'preco_total': 'sum'
    }).reset_index()
    evolucao.columns = ['periodo', 'filial', 'faturamento']
    results['evolucao_top5'] = evolucao
    
    # === MIX DE PRODUTOS POR FILIAL ===
    mix_categoria = df.groupby(['filial_nome', 'cat_limite_credito']).agg({
        'preco_total': 'sum'
    }).reset_index()
    mix_categoria.columns = ['filial', 'categoria', 'faturamento']
    results['mix_categoria_filial'] = mix_categoria
    
    return results


def generate_branch_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório formatado de filiais.
    """
    ranking = results['ranking_filiais'].copy()
    ranking['faturamento_fmt'] = ranking['faturamento'].apply(lambda x: f"R$ {x:,.2f}")
    ranking['ticket_medio_fmt'] = ranking['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
    ranking['participacao_fmt'] = ranking['participacao'].apply(lambda x: f"{x:.1f}%")
    
    return ranking[['posicao', 'filial', 'faturamento_fmt', 'qtd_pedidos', 
                    'qtd_clientes', 'ticket_medio_fmt', 'participacao_fmt']]
