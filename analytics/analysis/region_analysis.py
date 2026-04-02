"""
Análise por Mesoregião
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_mesoregiao_mapping(filepath: str = None) -> pd.DataFrame:
    """
    Carrega o mapeamento de filiais para mesoregiões.
    
    Args:
        filepath: Caminho para o arquivo Excel de mapeamento
        
    Returns:
        DataFrame com mapeamento filial -> mesoregião
    """
    if filepath is None:
        # Caminho padrão
        filepath = Path(__file__).parent.parent.parent / 'data' / 'FILIAL - MESOREGIAO v1.xlsx'
    
    df_meso = pd.read_excel(filepath, dtype=str)
    
    # Renomear colunas para facilitar uso
    df_meso.columns = ['filial_codigo', 'mesoregiao', 'analista']
    
    # Extrair apenas o código da filial (antes do ':' se houver)
    df_meso['filial_codigo'] = df_meso['filial_codigo'].apply(
        lambda x: str(x).split(':')[0].strip() if ':' in str(x) else str(x).strip()
    )
    
    return df_meso


def analyze_regions(df: pd.DataFrame, df_mesoregiao: pd.DataFrame = None) -> dict:
    """
    Realiza análise por mesoregião.
    
    Args:
        df: DataFrame com dados de vendas
        df_mesoregiao: DataFrame com mapeamento de mesoregiões
        
    Returns:
        Dicionário com resultados da análise regional
    """
    results = {}
    
    # Carregar mapeamento se não fornecido
    if df_mesoregiao is None:
        df_mesoregiao = load_mesoregiao_mapping()
    
    # Fazer merge dos dados com as mesoregiões usando filial_codigo
    df_com_regiao = df.merge(
        df_mesoregiao[['filial_codigo', 'mesoregiao', 'analista']], 
        on='filial_codigo', 
        how='left'
    )
    
    # Preencher valores nulos
    df_com_regiao['mesoregiao'] = df_com_regiao['mesoregiao'].fillna('Não Classificado')
    df_com_regiao['analista'] = df_com_regiao['analista'].fillna('-')
    
    # === ESTATÍSTICAS GERAIS ===
    total_regioes = df_com_regiao['mesoregiao'].nunique()
    results['stats'] = {
        'total_regioes': total_regioes,
        'total_analistas': df_com_regiao['analista'].nunique()
    }
    
    # === ANÁLISE POR MESOREGIÃO ===
    # Primeiro, calcular métricas básicas
    regiao_analysis_base = df_com_regiao.groupby('mesoregiao').agg(
        faturamento=('preco_total', 'sum'),
        qtd_pedidos=('num_pedido', 'nunique'),
        qtd_clientes=('matricula_cooperado', 'nunique'),
        ticket_medio=('preco_total', 'mean')
    ).reset_index()

    # Calcular Total de Descontos usando a mesma lógica do Financeiro (apenas pedidos com saldo positivo de desconto)
    # Agrupar por Mesoregião e Pedido para ver saldo do pedido
    pedidos_por_regiao = df_com_regiao.groupby(['mesoregiao', 'num_pedido'])['valor_desconto_manual'].sum().reset_index()
    
    # Filtrar apenas descontos positivos
    descontos_validos = pedidos_por_regiao[pedidos_por_regiao['valor_desconto_manual'] > 0]
    
    # Somar por região
    total_descontos_regiao = descontos_validos.groupby('mesoregiao')['valor_desconto_manual'].sum().reset_index()
    total_descontos_regiao.columns = ['mesoregiao', 'total_desconto']
    
    # Merge com a análise base
    regiao_analysis = pd.merge(regiao_analysis_base, total_descontos_regiao, on='mesoregiao', how='left')
    regiao_analysis['total_desconto'] = regiao_analysis['total_desconto'].fillna(0) # Preencher Zero se não houver descontos

    # Calcular percentuais
    total_faturamento = regiao_analysis['faturamento'].sum()
    regiao_analysis['pct_faturamento'] = (regiao_analysis['faturamento'] / total_faturamento * 100).round(2)
    
    # Calcular % Médio de Desconto (Ponderado: Total Desconto / Faturamento)
    regiao_analysis['pct_medio'] = (regiao_analysis['total_desconto'] / regiao_analysis['faturamento'] * 100).round(2)
    regiao_analysis['pct_medio'] = regiao_analysis['pct_medio'].fillna(0)
    
    # Ordenar por faturamento
    regiao_analysis = regiao_analysis.sort_values('faturamento', ascending=False)
    results['regiao_analysis'] = regiao_analysis
    
    # === TOP REGIÕES ===
    results['top_regioes'] = regiao_analysis.head(10)
    
    # === ANÁLISE POR ANALISTA ===
    analista_analysis = df_com_regiao.groupby('analista').agg(
        faturamento=('preco_total', 'sum'),
        qtd_pedidos=('num_pedido', 'nunique'),
        qtd_clientes=('matricula_cooperado', 'nunique'),
        total_desconto=('valor_desconto_manual', 'sum')
    ).reset_index()
    
    analista_analysis['pct_faturamento'] = (analista_analysis['faturamento'] / total_faturamento * 100).round(2)
    analista_analysis = analista_analysis.sort_values('faturamento', ascending=False)
    results['analista_analysis'] = analista_analysis
    
    # === EVOLUÇÃO MENSAL POR REGIÃO ===
    df_com_regiao['mes'] = df_com_regiao['data_pedido'].dt.to_period('M').astype(str)
    evolucao_regiao = df_com_regiao.groupby(['mes', 'mesoregiao']).agg(
        faturamento=('preco_total', 'sum'),
        qtd_pedidos=('num_pedido', 'nunique')
    ).reset_index()
    results['evolucao_regiao'] = evolucao_regiao
    
    # === DESCONTOS POR REGIÃO ===
    desconto_regiao = df_com_regiao[df_com_regiao['valor_desconto_manual'] > 0].groupby('mesoregiao').agg(
        total_desconto=('valor_desconto_manual', 'sum'),
        qtd_pedidos_desconto=('num_pedido', 'nunique'),
        faturamento=('preco_total', 'sum')
    ).reset_index()
    
    # Calcular % Médio Ponderado (Total Desconto / Faturamento Bruto)
    # Faturamento Bruto = Faturamento Líquido + Total Desconto
    desconto_regiao['pct_medio'] = (desconto_regiao['total_desconto'] / 
                                   (desconto_regiao['faturamento'] + desconto_regiao['total_desconto']) * 100).round(2)
    
    desconto_regiao = desconto_regiao.sort_values('total_desconto', ascending=False)
    results['desconto_regiao'] = desconto_regiao
    
    return results


def generate_region_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório de análise regional formatado.
    """
    regiao = results['regiao_analysis']
    
    report_data = []
    for _, row in regiao.iterrows():
        report_data.append([
            row['mesoregiao'],
            f"R$ {row['faturamento']:,.2f}",
            f"{row['pct_faturamento']:.1f}%",
            f"{int(row['qtd_pedidos']):,}",
            f"{int(row['qtd_clientes']):,}",
            f"R$ {row['total_desconto']:,.2f}"
        ])
    
    return pd.DataFrame(report_data, columns=[
        'Mesoregião', 'Faturamento', '% Part.', 'Pedidos', 'Clientes', 'Descontos'
    ])
