
import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analytics import data_loader
from analytics.analysis import financial_analysis

def debug_discounts():
    print("📂 Carregando dados...")
    try:
        # Caminho relativo considerando execução da raiz
        filepath = os.path.join(os.getcwd(), 'data', 'Pedidos - Completo.csv')
        if not os.path.exists(filepath):
            # Tentar outro caminho
            filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'Pedidos - Completo.csv')
            
        print(f"Lendo arquivo: {filepath}")
        df = data_loader.load_data(filepath)
        print(f"✅ Dados carregados: {len(df)} registros")
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return

    # 1. KPI Calculation Logic
    total_desconto_kpi = df['valor_desconto_manual'].sum()
    print(f"\n--- KPI Total de Descontos ---")
    print(f"Soma direta do dataframe (KPI): R$ {total_desconto_kpi:,.2f}")

    # Check for negative discounts
    negativos = df[df['valor_desconto_manual'] < 0]
    if not negativos.empty:
        print(f"⚠️ AVISO: Existem {len(negativos)} linhas com desconto negativo! Soma: R$ {negativos['valor_desconto_manual'].sum():,.2f}")

    # 2. Replicate Financial Analysis Logic
    print(f"\n--- Lógica da Análise Financeira ---")
    
    # Logic from financial_analysis.py
    df_pedidos = df.groupby('num_pedido').agg({
        'valor_desconto_manual': 'sum',
        'preco_total': 'sum',
        'valor_pedido': 'first',
        'desconto_manual_pct': 'max',
    }).reset_index()
    
    print(f"Pedidos únicos: {len(df_pedidos)}")
    print(f"Soma desconto dos pedidos: R$ {df_pedidos['valor_desconto_manual'].sum():,.2f}")
    
    # Classificar Alçada (Copied from financial_analysis.py)
    df_pedidos = df_pedidos.rename(columns={'desconto_manual_pct': 'max_desconto_pct'})
    
    def classificar_alcada(row):
        if row['valor_desconto_manual'] <= 0:
            return 'Sem Desconto'
        elif row['max_desconto_pct'] <= 0.5:
            return 'Vendedor (≤0,5%)'
        elif row['max_desconto_pct'] <= 3.0:
            return 'Gerente (0,51-3%)'
        else:
            return 'Comercial (>3%)'
            
    df_pedidos['alcada'] = df_pedidos.apply(classificar_alcada, axis=1)
    
    # Analysis Table Logic
    df_pedidos_com_desconto = df_pedidos[df_pedidos['valor_desconto_manual'] > 0]
    print(f"Pedidos classificados 'com desconto' (>0): {len(df_pedidos_com_desconto)}")
    
    alcada_detalhada = df_pedidos_com_desconto.groupby('alcada').agg({
        'valor_desconto_manual': 'sum'
    }).reset_index()
    
    print("\n--- Tabela Análise Detalhada por Alçada ---")
    table_sum = 0
    for _, row in alcada_detalhada.iterrows():
        print(f"{row['alcada']}: R$ {row['valor_desconto_manual']:,.2f}")
        table_sum += row['valor_desconto_manual']
        
    print(f"\nSoma Total da Tabela: R$ {table_sum:,.2f}")
    print(f"Diferença (KPI - Tabela): R$ {total_desconto_kpi - table_sum:,.2f}")
    
    # Check for 'Sem Desconto' having positive values?
    sem_desconto = df_pedidos[df_pedidos['alcada'] == 'Sem Desconto']
    sum_sem = sem_desconto['valor_desconto_manual'].sum()
    print(f"\nSoma da categoria 'Sem Desconto': R$ {sum_sem:,.2f} (Deveria ser <= 0)")
    
    # Check for mismatched logic
    # Are there orders with value > 0 but max_pct <= 0?
    weird_orders = df_pedidos[(df_pedidos['valor_desconto_manual'] > 0) & (df_pedidos['max_desconto_pct'] <= 0)]
    if not weird_orders.empty:
        print(f"\n⚠️ AVISO: {len(weird_orders)} pedidos com valor > 0 mas % <= 0")
        print(f"Soma desses pedidos: R$ {weird_orders['valor_desconto_manual'].sum():,.2f}")

    # ... (previous code) ...
    
    # 3. New Hypothesis: Mixed Signs in Orders
    print(f"\n--- Investigação de Linhas vs Pedidos ---")
    
    # Calculate what I implemented in the "Fix"
    kpi_fix = df[df['valor_desconto_manual'] > 0]['valor_desconto_manual'].sum()
    print(f"KPI Atual (Soma linhas > 0): R$ {kpi_fix:,.2f}")
    
    # Calculate what the Table uses
    # The table sums 'valor_desconto_manual' of ORDERS where 'valor_desconto_manual' > 0
    
    # Re-aggregate to be sure
    df_pedidos_check = df.groupby('num_pedido')['valor_desconto_manual'].sum().reset_index()
    table_logic_sum = df_pedidos_check[df_pedidos_check['valor_desconto_manual'] > 0]['valor_desconto_manual'].sum()
    print(f"Logica Tabela (Soma de Pedidos Liquidos > 0): R$ {table_logic_sum:,.2f}")
    
    diff = kpi_fix - table_logic_sum
    print(f"Diferença encontrada: R$ {diff:,.2f}")

    # Find the culprits
    # Orders that have positive discounts but also some negative lines?
    input_mixed = []
    for pid, group in df.groupby('num_pedido'):
        vals = group['valor_desconto_manual']
        has_pos = (vals > 0).any()
        has_neg = (vals < 0).any()
        if has_pos and has_neg:
            input_mixed.append({
                'pedido': pid,
                'pos_sum': vals[vals > 0].sum(),
                'net_sum': vals.sum(),
                'diff': vals[vals > 0].sum() - vals.sum()
            })
            
    if input_mixed:
        print(f"\n⚠️ Encontrados {len(input_mixed)} pedidos com linhas mistas (+ e -):")
        mixed_df = pd.DataFrame(input_mixed)
        print(f"Soma das diferenças nesses pedidos: R$ {mixed_df['diff'].sum():,.2f}")
        print("Exemplos:")
        print(mixed_df.head())
    else:
        print("\nNenhum pedido com linhas mistas encontrado.")

if __name__ == "__main__":
    debug_discounts()
