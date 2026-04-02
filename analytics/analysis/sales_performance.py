"""
Análise de Performance de Vendas
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_sales_performance(df: pd.DataFrame) -> dict:
    """
    Realiza análise completa de performance de vendas.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === KPIs GERAIS ===
    results['kpis'] = {
        'faturamento_total': df['preco_total'].sum(),
        'total_transacoes': len(df),
        'total_pedidos': df['num_pedido'].nunique(),
        'ticket_medio_transacao': df['preco_total'].mean(),
        'ticket_medio_pedido': df['preco_total'].sum() / df['num_pedido'].nunique(),
        'valor_medio_item': df['preco_total'].mean(),
        'quantidade_media': df['quantidade'].mean(),
    }
    
    # === FATURAMENTO POR PERÍODO ===
    # Por mês
    fat_mensal = df.groupby('ano_mes').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    fat_mensal.columns = ['periodo', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    fat_mensal['ticket_medio'] = fat_mensal['faturamento'] / fat_mensal['qtd_pedidos']
    results['faturamento_mensal'] = fat_mensal
    
    # Por trimestre
    fat_trimestral = df.groupby(['ano', 'trimestre']).agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    fat_trimestral['periodo'] = fat_trimestral['ano'].astype(str) + '-Q' + fat_trimestral['trimestre'].astype(str)
    results['faturamento_trimestral'] = fat_trimestral
    
    # === STATUS DOS PEDIDOS ===
    status_analysis = df.groupby('status').agg({
        'preco_total': ['sum', 'count'],
        'num_pedido': 'nunique'
    }).reset_index()
    status_analysis.columns = ['status', 'valor_total', 'qtd_itens', 'qtd_pedidos']
    status_analysis['percentual'] = (status_analysis['valor_total'] / status_analysis['valor_total'].sum() * 100).round(2)
    results['status_pedidos'] = status_analysis
    
    # === MODALIDADE DE VENDA ===
    modalidade_analysis = df.groupby('modalidade_venda').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    modalidade_analysis.columns = ['modalidade', 'faturamento', 'qtd_pedidos']
    results['modalidade_venda'] = modalidade_analysis
    
    # === ANÁLISE POR DIA DA SEMANA ===
    dia_semana_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dia_semana_pt = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
                     'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    
    dia_analysis = df.groupby('dia_semana').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    dia_analysis['dia_pt'] = dia_analysis['dia_semana'].map(dia_semana_pt)
    results['vendas_dia_semana'] = dia_analysis
    
    # === TOP 10 MAIORES PEDIDOS ===
    top_pedidos = df.groupby(['num_pedido', 'data_pedido', 'nome_conta', 'filial_nome']).agg({
        'valor_pedido': 'first'
    }).reset_index().nlargest(10, 'valor_pedido')
    results['top_pedidos'] = top_pedidos
    
    # === EVOLUÇÃO DIÁRIA (últimos 30 dias) ===
    df_recent = df[df['data_pedido'] >= df['data_pedido'].max() - pd.Timedelta(days=30)]
    evolucao_diaria = df_recent.groupby(df_recent['data_pedido'].dt.date).agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    evolucao_diaria.columns = ['data', 'faturamento', 'qtd_pedidos']
    results['evolucao_diaria'] = evolucao_diaria
    
    return results


def generate_sales_report(results: dict) -> pd.DataFrame:
    """
    Gera um resumo formatado para relatório.
    """
    kpis = results['kpis']
    
    report_data = [
        ['Faturamento Total', f"R$ {kpis['faturamento_total']:,.2f}"],
        ['Total de Transações', f"{kpis['total_transacoes']:,}"],
        ['Total de Pedidos Únicos', f"{kpis['total_pedidos']:,}"],
        ['Ticket Médio por Pedido', f"R$ {kpis['ticket_medio_pedido']:,.2f}"],
        ['Valor Médio por Item', f"R$ {kpis['valor_medio_item']:,.2f}"],
        ['Quantidade Média por Item', f"{kpis['quantidade_media']:.2f}"],
    ]
    
    return pd.DataFrame(report_data, columns=['Métrica', 'Valor'])
