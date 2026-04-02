"""
Módulo de carregamento e preparação de dados para análises.
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def load_data(filepath: str) -> pd.DataFrame:
    """
    Carrega e prepara os dados do arquivo Excel ou CSV.
    
    Args:
        filepath: Caminho para o arquivo Excel (.xlsx) ou CSV (.csv)
        
    Returns:
        DataFrame preparado para análises
    """
    print("📂 Carregando dados...")
    
    # Detectar tipo de arquivo e carregar
    if filepath.lower().endswith('.csv'):
        df = pd.read_csv(filepath, encoding='utf-8', sep=';')
    else:
        df = pd.read_excel(filepath)
    
    # Renomear colunas para facilitar manipulação
    df.columns = [
        'data_pedido', 'hora_pedido', 'num_pedido', 'num_pedido_erp',
        'modalidade_venda', 'matricula_cooperado', 'nome_conta', 'filial',
        'cod_vendedor_01', 'vendedor_01', 'cod_vendedor_02', 'vendedor_02',
        'carteira', 'campanha', 'cond_pagamento', 'cat_limite_credito',
        'cod_produto', 'produto', 'quantidade', 'preco_total',
        'desconto_manual_pct', 'valor_desconto_manual', 'motivo_desconto', 'status', 'valor_pedido'
    ]
    
    print("🔧 Preparando dados...")
    
    # Converter data para datetime
    df['data_pedido'] = pd.to_datetime(df['data_pedido'], dayfirst=True, errors='coerce')
    
    # Extrair componentes de data
    df['ano'] = df['data_pedido'].dt.year
    df['mes'] = df['data_pedido'].dt.month
    df['mes_nome'] = df['data_pedido'].dt.strftime('%b/%Y')
    df['trimestre'] = df['data_pedido'].dt.quarter
    df['dia_semana'] = df['data_pedido'].dt.day_name()
    df['ano_mes'] = df['data_pedido'].dt.to_period('M').astype(str)
    
    # Converter valores numéricos
    numeric_cols = ['quantidade', 'preco_total', 'desconto_manual_pct', 
                    'valor_desconto_manual', 'valor_pedido']
    for col in numeric_cols:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Limpar strings
    string_cols = ['nome_conta', 'filial', 'vendedor_01', 'vendedor_02', 
                   'produto', 'campanha', 'status', 'carteira']
    for col in string_cols:
        df[col] = df[col].fillna('').astype(str).str.strip()
    
    # Extrair nome da filial (remover código)
    df['filial_nome'] = df['filial'].apply(lambda x: x.split(':')[-1].strip() if ':' in str(x) else str(x))
    
    # Extrair código da filial (para matching com mesoregião)
    df['filial_codigo'] = df['filial'].apply(lambda x: x.split(':')[0].strip() if ':' in str(x) else str(x))
    
    # Criar flag de desconto
    df['tem_desconto'] = df['valor_desconto_manual'] > 0
    
    print(f"✅ Dados carregados: {len(df):,} registros")
    
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Retorna estatísticas resumidas do dataset.
    """
    return {
        'total_registros': len(df),
        'total_pedidos': df['num_pedido'].nunique(),
        'total_cooperados': df['matricula_cooperado'].nunique(),
        'total_produtos': df['cod_produto'].nunique(),
        'total_filiais': df['filial'].nunique(),
        'total_vendedores': df['vendedor_01'].nunique(),
        'faturamento_total': df['preco_total'].sum(),
        'periodo_inicio': df['data_pedido'].min(),
        'periodo_fim': df['data_pedido'].max()
    }


def load_classe_cooperado(filepath: str = None) -> pd.DataFrame:
    """
    Carrega a tabela de segmentação comercial de cooperados.
    
    Args:
        filepath: Caminho para o arquivo Excel de segmentação
        
    Returns:
        DataFrame com mapeamento matricula -> classe comercial
    """
    import os
    from pathlib import Path
    
    if filepath is None:
        # Caminho padrão - encontrar o arquivo automaticamente
        data_dir = Path(__file__).parent.parent / 'data'
        files = [f for f in os.listdir(data_dir) if 'CLASSE' in f.upper() and f.endswith('.xlsx')]
        if not files:
            return None
        filepath = data_dir / files[0]
    
    df_classe = pd.read_excel(filepath)
    
    # Renomear colunas para facilitar uso
    df_classe = df_classe.rename(columns={
        'Matrícula': 'matricula_cooperado',
        'Classe': 'classe_comercial',
        'Cooperado': 'nome_cooperado'
    })
    
    # Converter matrícula para inteiro (para matching)
    df_classe['matricula_cooperado'] = pd.to_numeric(df_classe['matricula_cooperado'], errors='coerce').fillna(0).astype(int)
    
    # Manter apenas colunas necessárias
    df_classe = df_classe[['matricula_cooperado', 'classe_comercial']].drop_duplicates()
    
    return df_classe


def load_grupo_produtos(filepath: str = None) -> pd.DataFrame:
    """
    Carrega a tabela de grupos de produtos.
    
    Args:
        filepath: Caminho para o arquivo CSV de grupos de produtos
        
    Returns:
        DataFrame com mapeamento cod_produto -> grupo_produto
    """
    import os
    from pathlib import Path
    
    if filepath is None:
        data_dir = Path(__file__).parent.parent / 'data'
        files = [f for f in os.listdir(data_dir) if 'Grupo de Produtos' in f and f.endswith('.csv')]
        if not files:
            print("⚠️ Arquivo de Grupo de Produtos não encontrado")
            return None
        filepath = data_dir / files[0]
    
    print("📂 Carregando grupos de produtos...")
    df_grupo = pd.read_csv(filepath, sep=';', encoding='utf-8')
    
    # Renomear colunas para facilitar uso
    df_grupo.columns = ['cod_produto', 'nome_produto', 'ativo', 'cod_grupo', 'grupo_produto']
    
    # Converter cod_produto para numérico (para matching)
    df_grupo['cod_produto'] = pd.to_numeric(df_grupo['cod_produto'], errors='coerce').fillna(0).astype(int)
    
    # Manter apenas colunas necessárias (cod_produto e grupo_produto)
    df_grupo = df_grupo[['cod_produto', 'grupo_produto']].drop_duplicates()
    
    print(f"✅ Grupos de produtos carregados: {df_grupo['grupo_produto'].nunique()} grupos, {len(df_grupo)} produtos")
    
    return df_grupo


if __name__ == "__main__":
    # Teste do módulo
    df = load_data("../Pedidos - Completo.xlsx")
    stats = get_summary_stats(df)
    print("\n📊 Estatísticas:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
