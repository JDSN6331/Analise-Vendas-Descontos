"""
Análise de Campanhas e Condições de Pagamento
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_campaigns(df: pd.DataFrame) -> dict:
    """
    Realiza análise de campanhas e condições de pagamento.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === ANÁLISE DE CAMPANHAS ===
    df_campanhas = df[df['campanha'].str.strip() != ''].copy()
    
    # Calculo correto de desconto (desduplicado por pedido)
    descontos_campanha = df_campanhas.groupby(['campanha', 'num_pedido'])['valor_desconto_manual'].max().reset_index().groupby('campanha')['valor_desconto_manual'].sum()
    
    campanha_analysis = df_campanhas.groupby('campanha').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    
    campanha_analysis.columns = ['campanha', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    # Mapear descontos de volta
    campanha_analysis['total_desconto'] = campanha_analysis['campanha'].map(descontos_campanha).fillna(0)
    
    campanha_analysis['ticket_medio'] = (campanha_analysis['faturamento'] / campanha_analysis['qtd_pedidos']).round(2)
    campanha_analysis['desconto_medio_pct'] = (campanha_analysis['total_desconto'] / campanha_analysis['faturamento'] * 100).round(2)
    campanha_analysis = campanha_analysis.sort_values('faturamento', ascending=False).reset_index(drop=True)
    campanha_analysis['participacao'] = (campanha_analysis['faturamento'] / campanha_analysis['faturamento'].sum() * 100).round(2)
    results['analise_campanhas'] = campanha_analysis
    
    # === TOP 10 CAMPANHAS ===
    results['top_10_campanhas'] = campanha_analysis.head(10)
    
    # === CONDIÇÕES DE PAGAMENTO ===
    cond_pagamento = df.groupby('cond_pagamento').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    cond_pagamento.columns = ['condicao', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    cond_pagamento['ticket_medio'] = (cond_pagamento['faturamento'] / cond_pagamento['qtd_pedidos']).round(2)
    cond_pagamento = cond_pagamento.sort_values('faturamento', ascending=False).reset_index(drop=True)
    cond_pagamento['participacao'] = (cond_pagamento['faturamento'] / cond_pagamento['faturamento'].sum() * 100).round(2)
    results['condicoes_pagamento'] = cond_pagamento
    
    # === ANÁLISE DE CARTEIRA ===
    carteira_analysis = df.groupby('carteira').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    carteira_analysis.columns = ['carteira', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    carteira_analysis = carteira_analysis.sort_values('faturamento', ascending=False)
    carteira_analysis['participacao'] = (carteira_analysis['faturamento'] / carteira_analysis['faturamento'].sum() * 100).round(2)
    results['analise_carteira'] = carteira_analysis
    
    # === ESTATÍSTICAS ===
    results['stats'] = {
        'total_campanhas': len(campanha_analysis),
        'campanha_top': campanha_analysis.iloc[0]['campanha'] if len(campanha_analysis) > 0 else 'N/A',
        'faturamento_campanha_top': campanha_analysis.iloc[0]['faturamento'] if len(campanha_analysis) > 0 else 0,
        'total_condicoes_pagamento': len(cond_pagamento),
        'condicao_mais_usada': cond_pagamento.iloc[0]['condicao'] if len(cond_pagamento) > 0 else 'N/A',
        'pedidos_a_vista': len(df[df['cond_pagamento'].str.contains('VISTA', case=False, na=False)]),
        'pedidos_a_prazo': len(df[~df['cond_pagamento'].str.contains('VISTA', case=False, na=False)]),
    }
    
    # === EVOLUÇÃO DE CAMPANHAS NO TEMPO ===
    evolucao_campanha = df_campanhas.groupby(['ano_mes', 'campanha']).agg({
        'preco_total': 'sum'
    }).reset_index()
    evolucao_campanha.columns = ['periodo', 'campanha', 'faturamento']
    results['evolucao_campanhas'] = evolucao_campanha
    
    # === ANÁLISE À VISTA vs A PRAZO ===
    df['tipo_pagamento'] = df['cond_pagamento'].apply(
        lambda x: 'À Vista' if 'VISTA' in str(x).upper() else 'A Prazo'
    )
    tipo_pag = df.groupby('tipo_pagamento').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    tipo_pag.columns = ['tipo', 'faturamento', 'qtd_pedidos']
    tipo_pag['participacao'] = (tipo_pag['faturamento'] / tipo_pag['faturamento'].sum() * 100).round(2)
    results['vista_vs_prazo'] = tipo_pag
    
    return results


def generate_campaign_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório de campanhas formatado.
    """
    camp = results['top_10_campanhas'].copy()
    camp['faturamento_fmt'] = camp['faturamento'].apply(lambda x: f"R$ {x:,.2f}")
    camp['ticket_medio_fmt'] = camp['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
    camp['participacao_fmt'] = camp['participacao'].apply(lambda x: f"{x:.1f}%")
    
    return camp[['campanha', 'faturamento_fmt', 'qtd_pedidos', 
                 'qtd_clientes', 'ticket_medio_fmt', 'participacao_fmt']]
