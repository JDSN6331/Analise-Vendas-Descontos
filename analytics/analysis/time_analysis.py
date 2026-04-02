"""
Análise Temporal e Sazonalidade
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np


def analyze_time(df: pd.DataFrame) -> dict:
    """
    Realiza análise temporal e de sazonalidade.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === EVOLUÇÃO MENSAL ===
    mensal = df.groupby('ano_mes').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique',
        'cod_produto': 'nunique'
    }).reset_index()
    mensal.columns = ['periodo', 'faturamento', 'qtd_pedidos', 'qtd_clientes', 'qtd_produtos']
    mensal['ticket_medio'] = (mensal['faturamento'] / mensal['qtd_pedidos']).round(2)
    
    # Variação mês a mês
    mensal['var_faturamento'] = mensal['faturamento'].pct_change() * 100
    mensal['var_pedidos'] = mensal['qtd_pedidos'].pct_change() * 100
    
    results['evolucao_mensal'] = mensal
    
    # === EVOLUÇÃO TRIMESTRAL ===
    df['trimestre_label'] = df['ano'].astype(str) + '-Q' + df['trimestre'].astype(str)
    trimestral = df.groupby('trimestre_label').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    trimestral.columns = ['periodo', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
    results['evolucao_trimestral'] = trimestral
    
    # === ANÁLISE POR DIA DA SEMANA ===
    dia_semana_map = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dia_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    dia_semana = df.groupby('dia_semana').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    dia_semana['dia_pt'] = dia_semana['dia_semana'].map(dia_semana_map)
    dia_semana.columns = ['dia_en', 'faturamento', 'qtd_pedidos', 'dia']
    dia_semana['ticket_medio'] = (dia_semana['faturamento'] / dia_semana['qtd_pedidos']).round(2)
    dia_semana['participacao'] = (dia_semana['faturamento'] / dia_semana['faturamento'].sum() * 100).round(2)
    results['analise_dia_semana'] = dia_semana
    
    # === ANÁLISE POR DIA DA SEMANA - MÊS MAIS RECENTE ===
    # Filtrar pelo mês mais recente nos dados
    mes_mais_recente = df['ano_mes'].max()
    df_mes_atual = df[df['ano_mes'] == mes_mais_recente]
    
    dia_semana_mes = df_mes_atual.groupby('dia_semana').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    dia_semana_mes['dia_pt'] = dia_semana_mes['dia_semana'].map(dia_semana_map)
    dia_semana_mes.columns = ['dia_en', 'faturamento', 'qtd_pedidos', 'dia']
    dia_semana_mes['ticket_medio'] = (dia_semana_mes['faturamento'] / dia_semana_mes['qtd_pedidos']).round(2)
    dia_semana_mes['participacao'] = (dia_semana_mes['faturamento'] / dia_semana_mes['faturamento'].sum() * 100).round(2)
    results['analise_dia_semana_mes_atual'] = dia_semana_mes
    results['mes_atual_referencia'] = mes_mais_recente
    
    # === VENDAS POR DIA DO MÊS (MÊS MAIS RECENTE) ===
    df_mes_atual['dia_mes'] = df_mes_atual['data_pedido'].dt.day
    vendas_dia_mes = df_mes_atual.groupby('dia_mes').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    vendas_dia_mes.columns = ['dia', 'faturamento', 'qtd_pedidos']
    vendas_dia_mes = vendas_dia_mes.sort_values('dia')
    results['vendas_dia_mes'] = vendas_dia_mes
    
    # === ANÁLISE POR HORA ===
    df['hora'] = pd.to_datetime(df['hora_pedido'], format='%H:%M', errors='coerce').dt.hour
    hora_analysis = df.groupby('hora').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    hora_analysis.columns = ['hora', 'faturamento', 'qtd_pedidos']
    hora_analysis['participacao'] = (hora_analysis['faturamento'] / hora_analysis['faturamento'].sum() * 100).round(2)
    results['analise_hora'] = hora_analysis
    
    # === ANÁLISE POR MÊS DO ANO (SAZONALIDADE) ===
    meses_pt = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    
    sazonalidade = df.groupby('mes').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    sazonalidade['mes_nome'] = sazonalidade['mes'].map(meses_pt)
    sazonalidade.columns = ['mes', 'faturamento', 'qtd_pedidos', 'mes_nome']
    sazonalidade['participacao'] = (sazonalidade['faturamento'] / sazonalidade['faturamento'].sum() * 100).round(2)
    results['sazonalidade_mes'] = sazonalidade
    
    # === ESTATÍSTICAS ===
    results['stats'] = {
        'periodo_inicio': df['data_pedido'].min().strftime('%d/%m/%Y'),
        'periodo_fim': df['data_pedido'].max().strftime('%d/%m/%Y'),
        'total_dias': (df['data_pedido'].max() - df['data_pedido'].min()).days,
        'media_diaria_faturamento': df.groupby(df['data_pedido'].dt.date)['preco_total'].sum().mean(),
        'melhor_mes': mensal.loc[mensal['faturamento'].idxmax(), 'periodo'] if len(mensal) > 0 else 'N/A',
        'pior_mes': mensal.loc[mensal['faturamento'].idxmin(), 'periodo'] if len(mensal) > 0 else 'N/A',
        'melhor_dia_semana': dia_semana.loc[dia_semana['faturamento'].idxmax(), 'dia'] if len(dia_semana) > 0 else 'N/A',
    }
    
    # === COMPARATIVO ANO A ANO ===
    if df['ano'].nunique() > 1:
        yoy = df.groupby('ano').agg({
            'preco_total': 'sum',
            'num_pedido': 'nunique',
            'matricula_cooperado': 'nunique'
        }).reset_index()
        yoy.columns = ['ano', 'faturamento', 'qtd_pedidos', 'qtd_clientes']
        results['comparativo_anual'] = yoy
    
    return results


def generate_time_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório temporal formatado.
    """
    mensal = results['evolucao_mensal'].copy()
    mensal['faturamento_fmt'] = mensal['faturamento'].apply(lambda x: f"R$ {x:,.2f}")
    mensal['ticket_medio_fmt'] = mensal['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
    mensal['var_fmt'] = mensal['var_faturamento'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else '-')
    
    return mensal[['periodo', 'faturamento_fmt', 'qtd_pedidos', 'qtd_clientes', 'ticket_medio_fmt', 'var_fmt']]
