import sys
import os
import json
import pandas as pd
from data_loader import load_data
from main import generate_period_data, run_all_analyses

# Carregar dados
data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'Pedidos - Completo.csv')
df = load_data(data_file)
results = run_all_analyses(df)
dados_todos = generate_period_data(df, results, None)

alpi = dados_todos['vendedores_por_filial'].get('Loja Alpinópolis', [])
print(f"Total de vendedores na Loja Alpinópolis: {len(alpi)}")
for v in alpi:
    if v['total_desconto'] > 0:
        print(f"Vendedor: {v['vendedor']}, Total Desconto: {v['total_desconto']}")
