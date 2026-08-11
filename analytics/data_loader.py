"""
Módulo de carregamento e preparação de dados para análises.
Cooxupé Sales Analytics
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def _read_csv_with_fallback(filepath: str, sep: str = ';') -> pd.DataFrame:
    """
    Lê CSV tentando encodings comuns de exportações Windows/Excel.
    """
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']
    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding, sep=sep)
            print(f"   Encoding detectado: {encoding}")
            return df
        except UnicodeDecodeError as exc:
            last_error = exc

    raise last_error


def _extract_filial_codigo(value) -> str:
    """Extrai o código da filial/organização antes do separador ':'."""
    value = '' if pd.isna(value) else str(value).strip()
    return value.split(':')[0].strip() if ':' in value else value


def load_data(filepath: str) -> pd.DataFrame:
    """
    Carrega e prepara os dados do arquivo Excel ou CSV (suporta .csv.gz).
    
    Args:
        filepath: Caminho para o arquivo Excel (.xlsx) ou CSV (.csv/.csv.gz)
        
    Returns:
        DataFrame preparado para análises
    """
    print("📂 Carregando dados...")
    
    if not os.path.exists(filepath):
        if os.path.exists(filepath + '.gz'):
            filepath = filepath + '.gz'
        elif filepath.endswith('.gz') and os.path.exists(filepath[:-3]):
            filepath = filepath[:-3]
    
    # Detectar tipo de arquivo e carregar
    if filepath.lower().endswith('.csv') or filepath.lower().endswith('.csv.gz'):
        df = _read_csv_with_fallback(filepath, sep=';')
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
    df['filial_codigo'] = df['filial'].apply(_extract_filial_codigo)
    
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
        filepath: Caminho para o arquivo CSV ou Excel de grupos de produtos
        
    Returns:
        DataFrame com mapeamento cod_produto -> grupo_produto
    """
    import os
    from pathlib import Path
    
    if filepath is None:
        data_dir = Path(__file__).parent.parent / 'data'
        excel_path = data_dir / 'Produtos e Grupo de Produtos.xlsx'
        if excel_path.exists():
            filepath = excel_path
        else:
            files = [f for f in os.listdir(data_dir) if 'Grupo de Produtos' in f and f.endswith('.csv')]
            if not files:
                print("⚠️ Arquivo de Grupo de Produtos não encontrado")
                return None
            filepath = data_dir / files[0]
    
    print(f"📂 Carregando grupos de produtos de {filepath.name}...")
    if str(filepath).lower().endswith('.xlsx'):
        df_grupo = pd.read_excel(filepath)
    else:
        df_grupo = _read_csv_with_fallback(filepath, sep=';')
    
    # Renomear colunas para facilitar uso
    df_grupo.columns = ['cod_produto', 'nome_produto', 'ativo', 'cod_grupo', 'grupo_produto']
    
    # Converter cod_produto para numérico (para matching)
    df_grupo['cod_produto'] = pd.to_numeric(df_grupo['cod_produto'], errors='coerce').fillna(0).astype(int)
    
    # Manter apenas colunas necessárias (cod_produto e grupo_produto)
    df_grupo = df_grupo[['cod_produto', 'grupo_produto']].drop_duplicates()
    
    print(f"✅ Grupos de produtos carregados: {df_grupo['grupo_produto'].nunique()} grupos, {len(df_grupo)} produtos")
    
    return df_grupo


def load_estoque_critico(data_dir: str = None) -> pd.DataFrame:
    """
    Consolida itens vencidos e a vencer em até 60 dias.

    Returns:
        DataFrame deduplicado por produto + filial com a criticidade máxima.
    """
    import os
    from pathlib import Path

    if data_dir is None:
        data_dir = Path(__file__).parent.parent / 'data'
    else:
        data_dir = Path(data_dir)

    file_configs = [
        {
            'keyword': 'ESTOQUE VENCIDO',
            'status_validade': 'vencido',
            'dias_janela': 0,
            'criticidade': 3,
        },
        {
            'keyword': 'ESTOQUE A VENCER EM 30 DIAS',
            'status_validade': 'vence_30',
            'dias_janela': 30,
            'criticidade': 2,
        },
        {
            'keyword': 'ESTOQUE A VENCER EM 60 DIAS',
            'status_validade': 'vence_60',
            'dias_janela': 60,
            'criticidade': 1,
        },
    ]

    frames = []
    for config in file_configs:
        files = [
            f for f in os.listdir(data_dir)
            if config['keyword'] in f.upper() and f.lower().endswith('.xlsx')
        ]
        if not files:
            continue

        filepath = data_dir / files[0]
        df_raw = pd.read_excel(filepath)
        columns = list(df_raw.columns)

        if len(columns) >= 10:
            rename_map = {
                columns[0]: 'organizacao',
                columns[1]: 'cod_produto',
                columns[2]: 'produto',
                columns[3]: 'unidade',
                columns[4]: 'grupo_estoque',
                columns[5]: 'quantidade_critica',
                columns[6]: 'lote_estoque',
                columns[7]: 'data_expiracao_lote',
                columns[8]: 'custo_unitario',
                columns[9]: 'custo_total',
            }
        elif len(columns) >= 9:
            rename_map = {
                columns[0]: 'organizacao',
                columns[1]: 'cod_produto',
                columns[2]: 'produto',
                columns[3]: 'unidade',
                columns[4]: 'quantidade_critica',
                columns[5]: 'lote_estoque',
                columns[6]: 'data_expiracao_lote',
                columns[7]: 'custo_unitario',
                columns[8]: 'custo_total',
            }
        else:
            print(f"⚠️ Estrutura inesperada no arquivo de estoque crítico: {filepath.name}")
            continue

        df_temp = df_raw.rename(columns=rename_map)
        if 'grupo_estoque' not in df_temp.columns:
            df_temp['grupo_estoque'] = np.nan

        keep_cols = [
            'organizacao', 'cod_produto', 'produto', 'unidade', 'grupo_estoque',
            'quantidade_critica', 'lote_estoque', 'data_expiracao_lote',
            'custo_unitario', 'custo_total'
        ]
        df_temp = df_temp[keep_cols].copy()
        df_temp['status_validade'] = config['status_validade']
        df_temp['dias_janela'] = config['dias_janela']
        df_temp['criticidade'] = config['criticidade']
        frames.append(df_temp)

    if not frames:
        print("⚠️ Arquivos de estoque crítico não encontrados")
        return None

    df_estoque = pd.concat(frames, ignore_index=True)
    df_estoque['cod_produto'] = pd.to_numeric(df_estoque['cod_produto'], errors='coerce').fillna(0).astype(int)
    df_estoque = df_estoque[df_estoque['cod_produto'] > 0].copy()
    df_estoque['organizacao'] = df_estoque['organizacao'].fillna('').astype(str).str.strip()
    df_estoque['filial_codigo'] = df_estoque['organizacao'].apply(_extract_filial_codigo)
    df_estoque['produto'] = df_estoque['produto'].fillna('').astype(str).str.strip()
    df_estoque['data_expiracao_lote'] = pd.to_datetime(df_estoque['data_expiracao_lote'], errors='coerce')

    numeric_cols = ['quantidade_critica', 'custo_unitario', 'custo_total']
    for col in numeric_cols:
        df_estoque[col] = pd.to_numeric(df_estoque[col], errors='coerce').fillna(0)

    df_estoque = df_estoque.sort_values(
        ['cod_produto', 'filial_codigo', 'criticidade', 'data_expiracao_lote'],
        ascending=[True, True, False, True]
    )
    df_estoque = df_estoque.drop_duplicates(
        subset=['cod_produto', 'filial_codigo'],
        keep='first'
    ).reset_index(drop=True)

    print(
        "✅ Estoque crítico carregado: "
        f"{len(df_estoque):,} combinações produto/filial, "
        f"{df_estoque['cod_produto'].nunique()} produtos"
    )

    return df_estoque


if __name__ == "__main__":
    # Teste do módulo
    df = load_data("../Pedidos - Completo.xlsx")
    stats = get_summary_stats(df)
    print("\n📊 Estatísticas:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
