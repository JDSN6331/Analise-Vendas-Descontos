"""
Script Principal - Cooxupé Sales Analytics
Executa todas as análises e gera relatórios
"""

import sys
import os
from datetime import datetime

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from data_loader import load_data, get_summary_stats
from analysis.sales_performance import analyze_sales_performance, generate_sales_report
from analysis.branch_analysis import analyze_branches, generate_branch_report
from analysis.product_analysis import analyze_products, generate_abc_report
from analysis.customer_analysis import analyze_customers, generate_customer_report
from analysis.seller_analysis import analyze_sellers, generate_seller_report
from analysis.campaign_analysis import analyze_campaigns, generate_campaign_report
from analysis.time_analysis import analyze_time, generate_time_report
from analysis.financial_analysis import analyze_financial, generate_financial_report
from analysis.region_analysis import analyze_regions, load_mesoregiao_mapping
from dashboard.generator import generate_dashboard_html


def format_currency(value):
    """Formata valor para moeda brasileira."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def run_all_analyses(df):
    """Executa todas as análises e retorna os resultados."""
    print("\n" + "="*60)
    print("📊 EXECUTANDO ANÁLISES")
    print("="*60)
    
    results = {}
    
    print("\n1️⃣  Análise de Performance de Vendas...")
    results['sales'] = analyze_sales_performance(df)
    
    print("2️⃣  Análise de Performance por Filial...")
    results['branches'] = analyze_branches(df)
    
    print("3️⃣  Análise de Portfólio de Produtos (Curva ABC)...")
    results['products'] = analyze_products(df)
    
    print("4️⃣  Análise de Clientes (RFM)...")
    results['customers'] = analyze_customers(df)
    
    print("5️⃣  Análise de Vendedores...")
    results['sellers'] = analyze_sellers(df)
    
    print("6️⃣  Análise de Campanhas...")
    results['campaigns'] = analyze_campaigns(df)
    
    print("7️⃣  Análise Temporal...")
    results['time'] = analyze_time(df)
    
    print("8️⃣  Análise Financeira...")
    results['financial'] = analyze_financial(df)
    
    print("9️⃣  Análise por Mesoregião...")
    results['regions'] = analyze_regions(df)
    
    print("\n✅ Todas as análises concluídas!")
    
    return results


def generate_excel_report(results, df, output_path):
    """Gera relatório consolidado em Excel."""
    print("\n📝 Gerando relatório Excel...")
    
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#2E7D32', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        money_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
        pct_format = workbook.add_format({'num_format': '0.00%'})
        
        # === ABA: RESUMO EXECUTIVO ===
        summary_data = [
            ['RESUMO EXECUTIVO - COOXUPÉ SALES ANALYTICS', ''],
            ['', ''],
            ['Período de Análise', f"{results['time']['stats']['periodo_inicio']} a {results['time']['stats']['periodo_fim']}"],
            ['Total de Dias', results['time']['stats']['total_dias']],
            ['', ''],
            ['INDICADORES DE VENDAS', ''],
            ['Faturamento Total', results['sales']['kpis']['faturamento_total']],
            ['Total de Transações', results['sales']['kpis']['total_transacoes']],
            ['Total de Pedidos Únicos', results['sales']['kpis']['total_pedidos']],
            ['Ticket Médio por Pedido', results['sales']['kpis']['ticket_medio_pedido']],
            ['', ''],
            ['INDICADORES DE CLIENTES', ''],
            ['Total de Clientes', results['customers']['stats']['total_clientes']],
            ['Clientes Ativos (30 dias)', results['customers']['stats']['clientes_ativos_30d']],
            ['Clientes em Risco', results['customers']['stats']['at_risk']],
            ['Champions', results['customers']['stats']['champions']],
            ['', ''],
            ['INDICADORES DE PRODUTOS', ''],
            ['Total de Produtos', results['products']['stats']['total_produtos']],
            ['Produtos Classe A', results['products']['stats']['produtos_classe_a']],
            ['Produtos Classe B', results['products']['stats']['produtos_classe_b']],
            ['Produtos Classe C', results['products']['stats']['produtos_classe_c']],
            ['', ''],
            ['INDICADORES FINANCEIROS', ''],
            ['Total de Descontos', results['financial']['desconto_stats']['total_desconto']],
            ['% Desconto/Faturamento', f"{results['financial']['desconto_stats']['pct_desconto_total']:.2f}%"],
            ['Pedidos com Desconto', results['financial']['desconto_stats']['pedidos_com_desconto']],
        ]
        df_summary = pd.DataFrame(summary_data, columns=['Indicador', 'Valor'])
        df_summary.to_excel(writer, sheet_name='Resumo Executivo', index=False)
        
        # === ABA: VENDAS MENSAIS ===
        results['time']['evolucao_mensal'].to_excel(writer, sheet_name='Vendas Mensais', index=False)
        
        # === ABA: RANKING FILIAIS ===
        results['branches']['ranking_filiais'].to_excel(writer, sheet_name='Ranking Filiais', index=False)
        
        # === ABA: CURVA ABC PRODUTOS ===
        results['products']['curva_abc'].head(100).to_excel(writer, sheet_name='Curva ABC Produtos', index=False)
        
        # === ABA: RESUMO ABC ===
        results['products']['resumo_abc'].to_excel(writer, sheet_name='Resumo ABC', index=False)
        
        # === ABA: TOP CLIENTES ===
        results['customers']['top_20_clientes'].to_excel(writer, sheet_name='Top Clientes', index=False)
        
        # === ABA: SEGMENTAÇÃO RFM ===
        results['customers']['segmento_resumo'].to_excel(writer, sheet_name='Segmentação RFM', index=False)
        
        # === ABA: CLIENTES EM RISCO ===
        results['customers']['clientes_risco'].to_excel(writer, sheet_name='Clientes em Risco', index=False)
        
        # === ABA: RANKING VENDEDORES ===
        results['sellers']['ranking_vendedores'].to_excel(writer, sheet_name='Ranking Vendedores', index=False)
        
        # === ABA: CAMPANHAS ===
        results['campaigns']['analise_campanhas'].to_excel(writer, sheet_name='Análise Campanhas', index=False)
        
        # === ABA: CONDIÇÕES PAGAMENTO ===
        results['campaigns']['condicoes_pagamento'].to_excel(writer, sheet_name='Condições Pagamento', index=False)
        
        # === ABA: ANÁLISE FINANCEIRA ===
        generate_financial_report(results['financial']).to_excel(writer, sheet_name='Análise Financeira', index=False)
        
        # === ABA: DESCONTOS POR FILIAL ===
        results['financial']['desconto_por_filial'].to_excel(writer, sheet_name='Descontos por Filial', index=False)
        
        # === ABA: SAZONALIDADE ===
        results['time']['sazonalidade_mes'].to_excel(writer, sheet_name='Sazonalidade', index=False)
        
        # === ABA: DIA DA SEMANA ===
        results['time']['analise_dia_semana'].to_excel(writer, sheet_name='Análise Dia Semana', index=False)
        
    print(f"✅ Relatório salvo: {output_path}")


def generate_dashboard_data(results, df):
    """Gera dados JSON para o dashboard com suporte a filtragem por mês."""
    import json
    from analysis.time_analysis import analyze_time
    from analysis.sales_performance import analyze_sales_performance
    from analysis.branch_analysis import analyze_branches
    from analysis.product_analysis import analyze_products
    from analysis.customer_analysis import analyze_customers
    from analysis.seller_analysis import analyze_sellers
    from analysis.campaign_analysis import analyze_campaigns
    from analysis.financial_analysis import analyze_financial
    
    def generate_period_data(period_df, period_results=None, df_mesoregiao=None):
        """Gera dados para um período específico."""
        # Se não tiver results, calcular
        if period_results is None:
            period_results = {
                'sales': analyze_sales_performance(period_df),
                'branches': analyze_branches(period_df),
                'products': analyze_products(period_df),
                'customers': analyze_customers(period_df),
                'sellers': analyze_sellers(period_df),
                'time': analyze_time(period_df),
                'campaigns': analyze_campaigns(period_df),
                'financial': analyze_financial(period_df),
            }
            # Adicionar análise regional se df_mesoregiao estiver disponível
            if df_mesoregiao is not None:
                try:
                    period_results['regions'] = analyze_regions(period_df, df_mesoregiao)
                except:
                    period_results['regions'] = {}
        
        # Dados de dia da semana
        dia_semana_map = {
            'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        dia_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        dia_semana = period_df.groupby('dia_semana').agg({
            'preco_total': 'sum',
            'num_pedido': 'nunique'
        }).reset_index()
        dia_semana['dia'] = dia_semana['dia_semana'].map(dia_semana_map)
        dia_semana = dia_semana[['dia', 'preco_total', 'num_pedido']]
        dia_semana.columns = ['dia', 'faturamento', 'qtd_pedidos']
        
        # Dados de dia do mês
        period_df_copy = period_df.copy()
        period_df_copy['dia_mes'] = period_df_copy['data_pedido'].dt.day
        vendas_dia_mes = period_df_copy.groupby('dia_mes').agg({
            'preco_total': 'sum',
            'num_pedido': 'nunique'
        }).reset_index()
        vendas_dia_mes.columns = ['dia', 'faturamento', 'qtd_pedidos']
        
        # Produtos da curva ABC separados por classe
        curva_abc = period_results['products']['curva_abc']
        produtos_curva_a = curva_abc[curva_abc['curva'] == 'A'].head(10)[['produto', 'faturamento', 'qtd_pedidos']].to_dict('records')
        produtos_curva_b = curva_abc[curva_abc['curva'] == 'B'].head(10)[['produto', 'faturamento', 'qtd_pedidos']].to_dict('records')
        produtos_curva_c = curva_abc[curva_abc['curva'] == 'C'].head(10)[['produto', 'faturamento', 'qtd_pedidos']].to_dict('records')
        
        # Dados de descontos
        desconto_stats = period_results['financial']['desconto_stats']
        vendedor_alcada = period_results['financial'].get('vendedor_alcada', None)
        filial_alcada = period_results['financial'].get('filial_alcada', None)
        alcada_detalhada = period_results['financial'].get('alcada_detalhada', None)
        alcada_com_desconto = period_results['financial'].get('alcada_com_desconto', None)
        top_motivos_desconto = period_results['financial'].get('top_motivos_desconto', None)
        pct_medio_geral = period_results['financial'].get('pct_medio_geral', 0)
        loja_top_por_alcada = period_results['financial'].get('loja_top_por_alcada', {})
        faixas_por_alcada = period_results['financial'].get('faixas_por_alcada', {})
        desconto_por_grupo = period_results['financial'].get('desconto_por_grupo', None)
        desconto_por_grupo_ajustado = period_results['financial'].get('desconto_por_grupo_ajustado', None)
        desconto_por_grupo_impacto = period_results['financial'].get('desconto_por_grupo_impacto', None)
        
        # Dados regionais (se disponível)
        regions_data = {}
        if 'regions' in period_results:
            regions_data = {
                'top_regioes': period_results['regions'].get('top_regioes', None),
                'analista_analysis': period_results['regions'].get('analista_analysis', None),
                'desconto_regiao': period_results['regions'].get('desconto_regiao', None),
                'region_stats': period_results['regions'].get('stats', {'total_regioes': 0, 'total_analistas': 0}),
            }
        
        vendedores_por_filial = {}
        top_filiais = period_results['branches']['top_10_filiais'][['filial', 'faturamento', 'qtd_pedidos']]
        if len(period_df) > 0 and len(top_filiais) > 0:
            # Preencher vendedores nulos para não perder dados no groupby
            # Tratamento robusto: primeiro converte vazios para NaN
            period_df['vendedor_01'] = period_df['vendedor_01'].replace(r'^\s*$', np.nan, regex=True)
            period_df['vendedor_01'] = period_df['vendedor_01'].fillna('Não Informado')
            
            # Garantir que filial_nome não tenha espaços extras que quebrem o match
            period_df['filial_nome'] = period_df['filial_nome'].str.strip()
            
            # Calcular qtd_pedidos com desconto (> 0)
            def count_discount_orders(x):
                return x[period_df.loc[x.index, 'valor_desconto_manual'] > 0].nunique()

            vendedores_filial_df = period_df.groupby(['filial_nome', 'vendedor_01']).agg({
                'preco_total': 'sum',
                'num_pedido': ['nunique', count_discount_orders],
                'valor_desconto_manual': 'sum'
            }).reset_index()
            
            # Ajustar colunas após agregação complexa
            vendedores_filial_df.columns = ['filial', 'vendedor', 'faturamento', 'qtd_pedidos', 'qtd_pedidos_desconto', 'total_desconto']
            
            # CRITICAL FIX: Gerar dados para TODAS as filiais do período, não apenas o Top 10 de Faturamento.
            # Isso garante que se uma filial aparecer no Top 10 de Descontos (mas não for Top Faturamento),
            # o modal ainda funcionará.
            all_filiais = vendedores_filial_df['filial'].unique()
            
            for filial in all_filiais:
                df_filial = vendedores_filial_df[vendedores_filial_df['filial'] == filial].sort_values('faturamento', ascending=False)
                vendedores_por_filial[filial] = df_filial[['vendedor', 'faturamento', 'qtd_pedidos', 'qtd_pedidos_desconto', 'total_desconto']].to_dict('records')

        # Gerar lista de TODOS os pedidos (não apenas com desconto) para modais
        df_todos_pedidos = period_df.groupby('num_pedido').agg({
            'data_pedido': 'first',
            'nome_conta': 'first',
            'vendedor_01': 'first',
            'filial_nome': 'first',
            'preco_total': 'sum',
            'ano_mes': 'first'
        }).reset_index()
        
        todos_os_pedidos = []
        for _, row in df_todos_pedidos.iterrows():
            todos_os_pedidos.append({
                'data': row['data_pedido'].strftime('%d/%m/%Y') if pd.notna(row['data_pedido']) else '',
                'pedido': str(row['num_pedido']),
                'cliente': str(row['nome_conta']),
                'vendedor': str(row['vendedor_01']),
                'filial': str(row['filial_nome']),
                'valor_total': float(row['preco_total']),
                'ano_mes': str(row['ano_mes'])
            })

        return {
            'kpis': {
                'faturamento_total': float(period_results['sales']['kpis']['faturamento_total']),
                'total_pedidos': int(period_results['sales']['kpis']['total_pedidos']),
                'ticket_medio': float(period_results['sales']['kpis']['ticket_medio_pedido']),
                'total_clientes': int(period_results['customers']['stats']['total_clientes']),
                'total_produtos': int(period_results['products']['stats']['total_produtos']),
                'total_filiais': int(period_results['branches']['stats']['total_filiais']),
                'total_vendedores': int(period_results['sellers']['stats']['total_vendedores']),
                'total_desconto': float(desconto_stats['total_desconto']),
            },
            'top_filiais': top_filiais.to_dict('records'),
            'top_produtos': period_results['products']['top_20_produtos'][['produto', 'faturamento', 'curva']].head(10).to_dict('records'),
            'top_vendedores': period_results['sellers']['top_20_vendedores'][['vendedor', 'faturamento', 'qtd_pedidos']].head(10).to_dict('records'),
            'segmentos_clientes': period_results['customers']['segmento_resumo'][['segmento', 'qtd_clientes', 'faturamento']].to_dict('records'),
            'resumo_abc': period_results['products']['resumo_abc'].to_dict('records'),
            'status_pedidos': period_results['sales']['status_pedidos'][['status', 'valor_total', 'qtd_pedidos']].to_dict('records'),
            'dia_semana': dia_semana.to_dict('records'),
            'dia_mes': vendas_dia_mes.to_dict('records'),
            'campanhas': period_results['campaigns']['top_10_campanhas'][['campanha', 'faturamento', 'qtd_pedidos']].head(5).to_dict('records'),
            'produtos_curva_a': produtos_curva_a,
            'produtos_curva_b': produtos_curva_b,
            'produtos_curva_c': produtos_curva_c,
            # Dados de descontos
            'desconto_stats': {
                'total_desconto': float(desconto_stats['total_desconto']),
                'pct_desconto_total': float(desconto_stats['pct_desconto_total']),
                'pct_pedidos_com_desconto': float(desconto_stats['pct_pedidos_com_desconto']),
                'desconto_medio': float(desconto_stats['desconto_medio']),
                'maior_desconto': float(desconto_stats['maior_desconto']),
                'pedidos_com_desconto': int(desconto_stats['pedidos_com_desconto']),
            },
            'vendedor_alcada': vendedor_alcada[['vendedor', 'total_desconto', 'qtd_pedidos', 'pct_medio']].head(10).to_dict('records') if vendedor_alcada is not None else [],
            'filial_alcada': filial_alcada[['filial', 'total_desconto', 'qtd_pedidos', 'pct_medio']].head(10).to_dict('records') if filial_alcada is not None else [],
            'alcada_detalhada': alcada_detalhada[['alcada', 'pct_medio', 'qtd_pedidos', 'faturamento']].to_dict('records') if alcada_detalhada is not None else [],
            'alcada_com_desconto': alcada_com_desconto[['alcada', 'qtd_pedidos', 'total_desconto']].to_dict('records') if alcada_com_desconto is not None else [],
            'top_motivos_desconto': top_motivos_desconto[['motivo', 'valor_total', 'qtd_pedidos']].head(5).to_dict('records') if top_motivos_desconto is not None else [],
            'pct_medio_geral': float(pct_medio_geral),
            'loja_top_por_alcada': loja_top_por_alcada,
            'faixas_por_alcada': faixas_por_alcada,
            'desconto_por_grupo': desconto_por_grupo[['grupo_produto', 'total_desconto', 'qtd_pedidos', 'pct_do_total', 'faturamento']].to_dict('records') if desconto_por_grupo is not None else [],
            'desconto_por_grupo_ajustado': desconto_por_grupo_ajustado[['grupo_produto', 'total_desconto', 'qtd_pedidos', 'pct_do_total', 'faturamento']].to_dict('records') if desconto_por_grupo_ajustado is not None else [],
            'desconto_por_grupo_impacto': desconto_por_grupo_impacto if desconto_por_grupo_impacto is not None else {},
            'vendedores_por_filial': vendedores_por_filial,
            'todos_os_pedidos': todos_os_pedidos,
            # Dados regionais
            'top_regioes': regions_data.get('top_regioes', None)[['mesoregiao', 'faturamento', 'pct_faturamento', 'qtd_pedidos', 'qtd_clientes', 'total_desconto', 'pct_medio']].to_dict('records') if regions_data.get('top_regioes') is not None and len(regions_data.get('top_regioes')) > 0 else [],
            'analista_analysis': regions_data.get('analista_analysis', None)[['analista', 'faturamento', 'pct_faturamento', 'qtd_pedidos', 'qtd_clientes']].head(10).to_dict('records') if regions_data.get('analista_analysis') is not None and len(regions_data.get('analista_analysis')) > 0 else [],
            'desconto_regiao': regions_data.get('desconto_regiao', None)[['mesoregiao', 'total_desconto', 'qtd_pedidos_desconto', 'pct_medio']].head(10).to_dict('records') if regions_data.get('desconto_regiao') is not None and len(regions_data.get('desconto_regiao')) > 0 else [],
            'region_stats': regions_data.get('region_stats', {'total_regioes': 0, 'total_analistas': 0}),
        }
    
    # Obter lista de meses disponíveis
    meses_disponiveis = sorted(df['ano_mes'].unique().tolist())
    
    # Nomes dos meses em português
    meses_pt = {
        '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
        '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
        '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
    }
    
    meses_info = []
    for mes in meses_disponiveis:
        ano, num_mes = mes.split('-')
        nome_mes = meses_pt.get(num_mes, num_mes)
        meses_info.append({
            'valor': mes,
            'label': f'{nome_mes}/{ano}'
        })
    
    # Carregar mapeamento de mesoregiões para usar na análise por mês
    try:
        from analysis.region_analysis import load_mesoregiao_mapping
        df_mesoregiao = load_mesoregiao_mapping()
    except:
        df_mesoregiao = None
    
    # Gerar dados para todo o período (usando results já calculados)
    dados_por_mes = {
        'todos': generate_period_data(df, results, df_mesoregiao)
    }
    
    # Gerar dados para cada mês
    print("   Gerando dados por mês para o dashboard...")
    for mes in meses_disponiveis:
        df_mes = df[df['ano_mes'] == mes]
        if len(df_mes) > 0:
            dados_por_mes[mes] = generate_period_data(df_mes, df_mesoregiao=df_mesoregiao)
    
    # Dados que não mudam com filtro (evolução mensal)
    dashboard_data = {
        'generated_at': datetime.now().isoformat(),
        'meses_disponiveis': meses_info,
        'evolucao_mensal': results['time']['evolucao_mensal'][['periodo', 'faturamento', 'qtd_pedidos']].to_dict('records'),
        'dados_por_mes': dados_por_mes,
    }
    
    return dashboard_data


def print_summary(results):
    """Imprime resumo das análises no console."""
    print("\n" + "="*60)
    print("📈 RESUMO EXECUTIVO")
    print("="*60)
    
    kpis = results['sales']['kpis']
    print(f"\n💰 FATURAMENTO")
    print(f"   Total: {format_currency(kpis['faturamento_total'])}")
    print(f"   Ticket Médio: {format_currency(kpis['ticket_medio_pedido'])}")
    
    print(f"\n📦 TRANSAÇÕES")
    print(f"   Total de Transações: {kpis['total_transacoes']:,}")
    print(f"   Pedidos Únicos: {kpis['total_pedidos']:,}")
    
    cust = results['customers']['stats']
    print(f"\n👥 CLIENTES")
    print(f"   Total: {cust['total_clientes']:,}")
    print(f"   Ativos (30d): {cust['clientes_ativos_30d']:,}")
    print(f"   Champions: {cust['champions']:,}")
    print(f"   Em Risco: {cust['at_risk']:,}")
    
    prod = results['products']['stats']
    print(f"\n📋 PRODUTOS")
    print(f"   Total: {prod['total_produtos']:,}")
    print(f"   Classe A: {prod['produtos_classe_a']:,} ({prod['produtos_classe_a']/prod['total_produtos']*100:.1f}%)")
    print(f"   Classe B: {prod['produtos_classe_b']:,}")
    print(f"   Classe C: {prod['produtos_classe_c']:,}")
    
    branch = results['branches']['stats']
    print(f"\n🏪 FILIAIS")
    print(f"   Total: {branch['total_filiais']:,}")
    print(f"   Top: {branch['filial_top']}")
    
    seller = results['sellers']['stats']
    print(f"\n👤 VENDEDORES")
    print(f"   Total: {seller['total_vendedores']:,}")
    print(f"   Top: {seller['vendedor_top']}")
    
    fin = results['financial']['desconto_stats']
    print(f"\n💸 FINANCEIRO")
    print(f"   Total Descontos: {format_currency(fin['total_desconto'])}")
    print(f"   % Descontos: {fin['pct_desconto_total']:.2f}%")


def main():
    """Função principal."""
    print("\n" + "="*60)
    print("🌾 COOXUPÉ SALES ANALYTICS")
    print("   Sistema de Análise de Vendas")
    print("="*60)
    
    # Carregar dados (agora usando CSV)
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'Pedidos - Completo.csv')
    df = load_data(data_file)
    
    # Estatísticas básicas
    stats = get_summary_stats(df)
    print(f"\n📊 Dataset carregado:")
    print(f"   Registros: {stats['total_registros']:,}")
    print(f"   Período: {stats['periodo_inicio'].strftime('%d/%m/%Y')} a {stats['periodo_fim'].strftime('%d/%m/%Y')}")
    
    # Executar análises
    results = run_all_analyses(df)
    
    # Imprimir resumo
    print_summary(results)
    
    # Gerar relatório Excel
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    excel_path = os.path.join(output_dir, f'Relatorio_Analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    generate_excel_report(results, df, excel_path)
    
    # Gerar dados do dashboard
    dashboard_data = generate_dashboard_data(results, df)
    
    # Salvar dados JSON para dashboard (backup)
    import json
    json_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    # Gerar dashboard HTML com dados embutidos
    html_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'dashboard.html')
    generate_dashboard_html(results, html_path, df=df, dashboard_data=dashboard_data)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"\n📁 Arquivos gerados:")
    print(f"   • {excel_path}")
    print(f"   • {html_path}")
    
    return results, df


if __name__ == "__main__":
    results, df = main()
