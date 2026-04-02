
import sys
import os
import pandas as pd

# Add analytics directory to path
sys.path.insert(0, os.path.abspath('analytics'))

from data_loader import load_data
from analysis.financial_analysis import analyze_financial

def check_discrepancy():
    # Load data
    data_file = os.path.join('data', 'Pedidos - Completo.csv')
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        return

    df = load_data(data_file)
    
    # Run analysis
    results = analyze_financial(df)
    
    # Check "Análise Detalhada por Alçada" (Panel)
    alcada_detalhada = results['alcada_detalhada']
    print("\n=== Análise Detalhada por Alçada (Panel) ===")
    print(alcada_detalhada[['alcada', 'qtd_pedidos', 'total_desconto']])
    
    # Check Modal Data (Faixas por Alçada)
    faixas_por_alcada = results['faixas_por_alcada']
    print("\n=== Faixas por Alçada (Modal) ===")
    
    for alcada, faixas in faixas_por_alcada.items():
        print(f"\nAlçada: {alcada}")
        total_qtd = sum(f['qtd_pedidos'] for f in faixas)
        total_val = sum(f['total_desconto'] for f in faixas)
        print(f"Total Qtd: {total_qtd}")
        print(f"Total Valor: {total_val:,.2f}")
        
        # Calculate difference
        panel_row = alcada_detalhada[alcada_detalhada['alcada'] == alcada]
        if not panel_row.empty:
            panel_qtd = panel_row.iloc[0]['qtd_pedidos']
            panel_val = panel_row.iloc[0]['total_desconto']
            
            diff_qtd = panel_qtd - total_qtd
            diff_val = panel_val - total_val
            
            if diff_qtd != 0 or abs(diff_val) > 0.01:
                print(f"⚠️ DISCREPANCY FOUND for {alcada}!")
                print(f"Panel Qtd: {panel_qtd} | Modal Qtd: {total_qtd} | Diff: {diff_qtd}")
                print(f"Panel Val: {panel_val:,.2f} | Modal Val: {total_val:,.2f} | Diff: {diff_val:,.2f}")
                
                # Identify the problematic orders
                # Re-implement logic to find them
                
                # 1. Prepare df_pedidos as in financial_analysis.py
                df_pedidos = df.groupby('num_pedido').agg({
                    'valor_desconto_manual': 'sum',
                    'preco_total': 'sum',
                    'desconto_manual_pct': 'max',
                    'valor_pedido': 'first',
                    'tem_desconto': 'max'
                }).reset_index()
                df_pedidos = df_pedidos.rename(columns={'desconto_manual_pct': 'max_desconto_pct'})
                
                # 2. Add alcada
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
                
                # 3. Filter for current alcada and discount > 0
                df_alcada = df_pedidos[(df_pedidos['alcada'] == alcada) & (df_pedidos['valor_desconto_manual'] > 0)]
                
                # 4. Check get_faixa_desconto
                def get_faixa_desconto(pct):
                    if pct <= 0:
                        return None
                    elif pct <= 0.5:
                        return '0,01% a 0,50%'
                    elif pct <= 1.0:
                        return '0,51% a 1,00%'
                    elif pct <= 2.0:
                        return '1,01% a 2,00%'
                    elif pct <= 3.0:
                        return '2,01% a 3,00%'
                    elif pct <= 4.0:
                        return '3,01% a 4,00%'
                    elif pct <= 5.0:
                        return '4,01% a 5,00%'
                    elif pct <= 6.0:
                        return '5,01% a 6,00%'
                    elif pct <= 7.0:
                        return '6,01% a 7,00%'
                    elif pct <= 8.0:
                        return '7,01% a 8,00%'
                    elif pct <= 9.0:
                        return '8,01% a 9,00%'
                    elif pct <= 10.0:
                        return '9,01% a 10,00%'
                    else:
                        return 'Acima de 10%'
                
                df_alcada = df_alcada.copy()
                df_alcada['faixa_desconto'] = df_alcada['max_desconto_pct'].apply(get_faixa_desconto)
                
                # 5. Find None
                missing = df_alcada[df_alcada['faixa_desconto'].isnull()]
                if not missing.empty:
                    print(f"\n✅ FOUND ROOT CAUSE:")
                    print(f"Alçada '{alcada}' has {len(missing)} orders with positive discount value but max_desconto_pct <= 0.")
                    print(f"These orders are included in the Panel (Total: {panel_qtd}) but excluded from Modal (Total: {total_qtd}).")
                    print(f"Discrepancy: {panel_qtd} - {total_qtd} = {diff_qtd} (Should match {len(missing)})")
                    
                    print("\nSample of problematic orders:")
                    print(missing[['num_pedido', 'valor_desconto_manual', 'max_desconto_pct', 'preco_total']].head())
            else:
                print("✅ No discrepancy found.")

if __name__ == "__main__":
    check_discrepancy()
