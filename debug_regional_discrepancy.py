
import pandas as pd
import sys
import os

# Add directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics.data_loader import load_data
from analytics.analysis.region_analysis import load_mesoregiao_mapping


def investigate_regional_discrepancy():
    print("📂 Loading data...")
    try:
        # Tentar caminho relativo na pasta data
        df = load_data("data/Pedidos - Completo.csv")
    except FileNotFoundError:
        # Tentar caminho absoluto
        df = load_data(r"C:\Users\joseduque\Documents\Documentos\Python\Análise Vendas-Descontos\data\Pedidos - Completo.csv")
    
    # Global Total Discount (Financial Logic - Exact Match)
    # financial_analysis.py sums discounts per order, then takes only positive order totals
    pedidos_net_desconto = df.groupby('num_pedido')['valor_desconto_manual'].sum()
    total_desconto_global = pedidos_net_desconto[pedidos_net_desconto > 0].sum()
    print(f"💰 Global Total Discount (Matched Logic): R$ {total_desconto_global:,.2f}")

    # Regional Logic
    print("\n🗺️ Loading Region Mapping...")
    df_mesoregiao = load_mesoregiao_mapping()
    
    # Merge logic from region_analysis.py
    df_com_regiao = df.merge(
        df_mesoregiao[['filial_codigo', 'mesoregiao', 'analista']], 
        on='filial_codigo', 
        how='left'
    )
    
    # Fill NAs logic from region_analysis.py
    # df_com_regiao['mesoregiao'] = df_com_regiao['mesoregiao'].fillna('Não Classificado')
    
    # Check for unmapped branches
    unmapped = df_com_regiao[df_com_regiao['mesoregiao'].isna()]
    
    if not unmapped.empty:
        total_desconto_unmapped = unmapped[unmapped['valor_desconto_manual'] > 0]['valor_desconto_manual'].sum()
        print(f"⚠️ Found {len(unmapped)} orders with unmapped regions.")
        print(f"⚠️ Total Discount in unmapped regions: R$ {total_desconto_unmapped:,.2f}")
        
        print("\nUnmapped Branches:")
        print(unmapped['filial_codigo'].unique())
    else:
        print("✅ No unmapped regions found (before fillna).")

    # simulate the fillna
    df_com_regiao['mesoregiao'] = df_com_regiao['mesoregiao'].fillna('Não Classificado')
    
    # Group by
    regiao_analysis = df_com_regiao.groupby('mesoregiao').agg(
        total_desconto=('valor_desconto_manual', 'sum')
    ).reset_index().sort_values('total_desconto', ascending=False)
    
    print("\n🗺️  All Regions (Top 20 by Total Discount):")
    print(regiao_analysis.head(20))
    
    total_desconto_regional = regiao_analysis['total_desconto'].sum()
    print(f"\n∑ Regional Total Discount (Sum of groupby): R$ {total_desconto_regional:,.2f}")
    
    diff = total_desconto_global - total_desconto_regional
    print(f"\n📉 Discrepancy: R$ {diff:,.2f}")

    # Check if there are negative discounts affecting the sum
    total_desconto_raw = df['valor_desconto_manual'].sum()
    print(f"raw total sum: {total_desconto_raw}")

if __name__ == "__main__":
    investigate_regional_discrepancy()
