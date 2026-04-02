
import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_data
from analysis.branch_analysis import analyze_branches

def debug():
    # Load data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'Pedidos - Completo.csv')
    df = load_data(data_file)
    
    print(f"Data range: {df['data_pedido'].min()} to {df['data_pedido'].max()}")
    
    # Filter for 2026
    df_2026 = df[df['data_pedido'].dt.year == 2026].copy()
    
    # Problematic branches
    targets = [
        'Loja Araguari', 
        'Unidade Avançada Santo Antonio do Amparo', 
        'Loja Campos Gerais', 
        'Loja Campestre'
    ]
    
    print("\n--- CHECKING RAW DATA (2026) ---")
    for target in targets:
        # Fuzzy match to find what it actually looks like
        matches = [f for f in df_2026['filial_nome'].unique() if target.lower() in f.lower()]
        print(f"\nTarget: '{target}'")
        print(f"Matches in DB: {matches}")
        
        for match in matches:
            # Check monthly data
            df_branch = df_2026[df_2026['filial_nome'] == match]
            print(f"  Branch: '{match}' (Length: {len(match)})")
            
            # Check Jan/Feb specific
            for month in [1, 2]:
                df_m = df_branch[df_branch['data_pedido'].dt.month == month]
                print(f"    Month {month}: {len(df_m)} records")
                if len(df_m) > 0:
                    sellers = df_m['vendedor_01'].unique()
                    print(f"      Sellers: {sellers}")
                    # Check for empty/whitespace
                    empty = df_m[df_m['vendedor_01'].str.strip() == '']
                    nan = df_m[df_m['vendedor_01'].isna()]
                    print(f"      Empty strings: {len(empty)}")
                    print(f"      NaNs: {len(nan)}")
                    print(f"      'Não Informado': {len(df_m[df_m['vendedor_01'] == 'Não Informado'])}")

    print("\n--- CHECKING TOP 10 GENERATION ---")
    # Simulate what main.py does for Jan 2026
    df_jan = df_2026[df_2026['data_pedido'].dt.month == 1].copy()
    results_jan = analyze_branches(df_jan)
    top_10_jan = results_jan['top_10_filiais']
    
    print("\nTop 10 Jan 2025:")
    print(top_10_jan[['filial', 'faturamento']])
    
    # Check if targets are in Top 10 but have mismatch
    for target in targets:
        in_top = target in top_10_jan['filial'].values
        print(f"'{target}' in Top 10 Jan? {in_top}")
        if not in_top:
            # Check partial match in top 10
            matches = [f for f in top_10_jan['filial'] if target.lower() in f.lower()]
            print(f"  Matches in Top 10: {matches}")

if __name__ == "__main__":
    debug()
