"""
Gerador de Dashboard HTML
Cooxupé Sales Analytics
"""

from datetime import datetime
import json
import pandas as pd


def generate_dashboard_html(results, output_path, df=None, dashboard_data=None):
    """
    Gera o dashboard HTML com dados embutidos.
    
    Args:
        results: Resultados das análises
        output_path: Caminho para salvar o HTML
        df: DataFrame com os dados (opcional)
        dashboard_data: Dados do dashboard com informações por mês (opcional)
    """
    
    # Extrair dados
    kpis = results['sales']['kpis']
    branches = results['branches']['top_10_filiais']
    products = results['products']['top_20_produtos'].head(10)
    sellers = results['sellers']['top_20_vendedores'].head(10)
    campaigns = results['campaigns']['top_10_campanhas'].head(5)
    abc = results['products']['resumo_abc']
    segments = results['customers']['segmento_resumo']
    evolucao_mensal = results['time']['evolucao_mensal']
    
    # Dados das curvas ABC
    curva_abc = results['products']['curva_abc']
    produtos_curva_a = curva_abc[curva_abc['curva'] == 'A'].head(10)
    produtos_curva_b = curva_abc[curva_abc['curva'] == 'B'].head(10)
    produtos_curva_c = curva_abc[curva_abc['curva'] == 'C'].head(10)
    
    # Para vendas por dia da semana do mês atual, usar os dados filtrados se disponíveis
    dia_semana_mes_atual = results['time'].get('analise_dia_semana_mes_atual', results['time']['analise_dia_semana'])
    
    # Vendas por dia do mês
    vendas_dia_mes = results['time'].get('vendas_dia_mes', None)
    
    # Período de análise
    periodo_inicio = results['time']['stats']['periodo_inicio']
    periodo_fim = results['time']['stats']['periodo_fim']
    
    # Dados de descontos e alçada
    desconto_stats = results['financial']['desconto_stats']
    alcada_analysis = results['financial'].get('alcada_analysis', None)
    alcada_com_desconto = results['financial'].get('alcada_com_desconto', None)
    vendedor_alcada = results['financial'].get('vendedor_alcada', None)
    filial_alcada = results['financial'].get('filial_alcada', None)
    top_descontos = results['financial'].get('top_descontos', None)
    alcada_detalhada = results['financial'].get('alcada_detalhada', None)
    pct_medio_geral = results['financial'].get('pct_medio_geral', 0)
    loja_top_por_alcada = results['financial'].get('loja_top_por_alcada', {})
    faixas_por_alcada = results['financial'].get('faixas_por_alcada', {})
    periodos_descontos = results['financial'].get('periodos_descontos', [])
    top_motivos_desconto = results['financial'].get('top_motivos_desconto', None)
    
    # Dados regionais
    regiao_analysis = results.get('regions', {}).get('regiao_analysis', None)
    top_regioes = results.get('regions', {}).get('top_regioes', None)
    analista_analysis = results.get('regions', {}).get('analista_analysis', None)
    desconto_regiao = results.get('regions', {}).get('desconto_regiao', None)
    region_stats = results.get('regions', {}).get('stats', {'total_regioes': 0, 'total_analistas': 0})
    
    # Formatar valores
    def fmt_money(val):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def fmt_num(val):
        return f"{int(val):,}".replace(",", ".")
    
    # Gerar linhas das tabelas
    def gen_table_rows(data, columns, fmt_col=None):
        rows = ""
        for idx, (_, row) in enumerate(data.iterrows()):
            rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
            cells = f'<td><span class="rank-badge {rank_class}">{idx + 1}</span></td>'
            for col in columns:
                val = row[col]
                if fmt_col and col in fmt_col:
                    val = fmt_col[col](val)
                cells += f'<td>{val}</td>'
            rows += f'<tr>{cells}</tr>\n'
        return rows
    
    vendedores_rows = ""
    for idx, (_, row) in enumerate(sellers.iterrows()):
        rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
        vendedor_nome = str(row['vendedor'])
        vendedor_esc = vendedor_nome.replace("'", "\\'")
        vendedores_rows += f'<tr onclick="openVendedorPedidosModal(\'{vendedor_esc}\', false)" style="cursor: pointer;" title="Clique para ver pedidos deste vendedor"><td><span class="rank-badge {rank_class}">{idx + 1}</span></td><td>{vendedor_nome}</td><td>{fmt_money(row["faturamento"])}</td><td>{fmt_num(row["qtd_pedidos"])}</td></tr>\n'
    
    # Gerar linhas de filiais com clique para abrir modal de vendedores
    filiais_rows = ""
    for idx, (_, row) in enumerate(branches.iterrows()):
        rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
        filial_name = str(row['filial']).replace("'", "\\'")
        filiais_rows += f'''<tr onclick="openVendedoresModal('{filial_name}')" style="cursor: pointer;" title="Clique para ver vendedores desta filial"><td><span class="rank-badge {rank_class}">{idx + 1}</span></td><td>{row['filial']}</td><td>{fmt_money(row['faturamento'])}</td><td>{fmt_num(row['qtd_pedidos'])}</td></tr>\n'''
    
    # Gerar dados de vendedores por filial para o modal
    vendedores_por_filial = {}
    if dashboard_data is not None:
        vendedores_por_filial = dashboard_data.get('dados_por_mes', {}).get('todos', {}).get('vendedores_por_filial', {})
    
    vendedores_por_filial_json = json.dumps(vendedores_por_filial, ensure_ascii=False)
    
    # Produtos Curva A - com curva e pedidos
    produtos_a_rows = ""
    for idx, (_, row) in enumerate(produtos_curva_a.iterrows()):
        rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
        produto_nome = str(row["produto"])
        produtos_a_rows += f'<tr><td><span class="rank-badge {rank_class}">{idx + 1}</span></td><td>{produto_nome}</td><td>{fmt_money(row["faturamento"])}</td><td>{fmt_num(row["qtd_pedidos"])}</td></tr>\n'
    
    # Produtos Curva B
    produtos_b_rows = ""
    for idx, (_, row) in enumerate(produtos_curva_b.iterrows()):
        produto_nome = str(row["produto"])
        produtos_b_rows += f'<tr><td>{idx + 1}</td><td>{produto_nome}</td><td>{fmt_money(row["faturamento"])}</td><td>{fmt_num(row["qtd_pedidos"])}</td></tr>\n'
    
    # Produtos Curva C
    produtos_c_rows = ""
    for idx, (_, row) in enumerate(produtos_curva_c.iterrows()):
        produto_nome = str(row["produto"])
        produtos_c_rows += f'<tr><td>{idx + 1}</td><td>{produto_nome}</td><td>{fmt_money(row["faturamento"])}</td><td>{fmt_num(row["qtd_pedidos"])}</td></tr>\n'
    
    campanhas_rows = gen_table_rows(campaigns, ['campanha', 'faturamento', 'qtd_pedidos'],
                                     {'faturamento': fmt_money, 'qtd_pedidos': lambda x: fmt_num(x)})
    
    # Preparar dados para gráficos em JSON
    abc_chart = {
        'labels': [f"Classe {row['curva']} ({int(row['qtd_produtos'])} prod.)" for _, row in abc.iterrows()],
        'data': [float(row['faturamento']) for _, row in abc.iterrows()]
    }
    
    # Mapeamento de segmentos comerciais para emojis
    seg_emoji_map = {
        'FIEL': '💚 Fiel',
        'FIEL A RETER': '💛 Fiel a Reter',
        'DESAFIO': '🔴 Desafio',
        'POSITIVADO': '✅ Positivado',
        'MANTIDO': '🔵 Mantido',
        'A MANTER': '🟠 A Manter',
        'NÃO CLASSIFICADO': '❓ Não Classificado',
        # Fallback para RFM caso segmentação comercial não esteja disponível
        'Champions': '🏆 Campeões',
        'Loyal Customers': '💎 Leais',
        'At Risk': '⚠️ Em Risco',
        'Potential Loyalists': '⭐ Potenciais',
        'Recent Customers': '🆕 Novos',
        'Hibernating': '😴 Hibernando',
        "Can't Lose Them": '❌ Perdidos',
        'Others': '❓ Outros'
    }
    
    # Ordenar segmentos do maior para menor
    segments_sorted = segments.sort_values('qtd_clientes', ascending=False)
    
    seg_chart = {
        'labels': [f"{seg_emoji_map.get(row['segmento'], row['segmento'])} ({int(row['qtd_clientes'])})" for _, row in segments_sorted.iterrows()],
        'data': [int(row['qtd_clientes']) for _, row in segments_sorted.iterrows()]
    }
    
    # Dia da semana
    dia_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    dia_chart = {'labels': [], 'data': []}
    for dia in dia_order:
        row = dia_semana_mes_atual[dia_semana_mes_atual['dia'] == dia]
        if len(row) > 0:
            dia_chart['labels'].append(dia)
            dia_chart['data'].append(float(row.iloc[0]['faturamento']))
    
    # Vendas por dia do mês - garantir todos os dias do mês (1-31)
    dia_mes_chart = {'labels': [], 'data': []}
    if vendas_dia_mes is not None and len(vendas_dia_mes) > 0:
        # Criar dicionário com os dias que têm dados
        dias_com_dados = {int(row['dia']): float(row['faturamento']) for _, row in vendas_dia_mes.iterrows()}
        # Preencher todos os 31 dias
        for dia in range(1, 32):
            dia_mes_chart['labels'].append(str(dia))
            dia_mes_chart['data'].append(dias_com_dados.get(dia, 0))
    
    # Evolução mensal - converter formato de data
    meses_pt = {
        '01': 'janeiro', '02': 'fevereiro', '03': 'março', '04': 'abril',
        '05': 'maio', '06': 'junho', '07': 'julho', '08': 'agosto',
        '09': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro'
    }
    
    def formatar_periodo(periodo):
        """Converte '2026-01' para 'janeiro/2026'"""
        try:
            ano, mes = str(periodo).split('-')
            return f"{meses_pt.get(mes, mes)}/{ano}"
        except:
            return str(periodo)
    
    evolucao_chart = {
        'labels': [formatar_periodo(row['periodo']) for _, row in evolucao_mensal.iterrows()],
        'data': [float(row['faturamento']) for _, row in evolucao_mensal.iterrows()]
    }
    
    now = datetime.now()
    
    # Converter para JSON seguro
    abc_json = json.dumps(abc_chart, ensure_ascii=False)
    seg_json = json.dumps(seg_chart, ensure_ascii=False)
    dia_json = json.dumps(dia_chart, ensure_ascii=False)
    dia_mes_json = json.dumps(dia_mes_chart, ensure_ascii=False)
    evolucao_json = json.dumps(evolucao_chart, ensure_ascii=False)
    
    # Dados de alçada para gráficos
    alcada_chart = {'labels': [], 'data': [], 'valores': []}
    if alcada_com_desconto is not None:
        for _, row in alcada_com_desconto.iterrows():
            alcada_chart['labels'].append(row['alcada'])
            alcada_chart['data'].append(int(row['qtd_pedidos']))
            alcada_chart['valores'].append(float(row['total_desconto']))
    alcada_json = json.dumps(alcada_chart, ensure_ascii=False)
    
    # Dados de motivos de desconto para gráfico
    motivos_chart = {'labels': [], 'data': [], 'qtd': []}
    if top_motivos_desconto is not None:
        for _, row in top_motivos_desconto.iterrows():
            motivos_chart['labels'].append(str(row['motivo']))
            motivos_chart['data'].append(float(row['valor_total']))
            motivos_chart['qtd'].append(int(row['qtd_pedidos']))
    motivos_json = json.dumps(motivos_chart, ensure_ascii=False)
    
    # Gerar linhas das tabelas de desconto
    def get_alcada_class(alcada):
        if 'Vendedor' in str(alcada):
            return 'vendedor'
        elif 'Gerente' in str(alcada):
            return 'gerente'
        elif 'Comercial' in str(alcada):
            return 'comercial'
        return 'sem'
    
    vendedor_alcada_rows = ""
    if vendedor_alcada is not None:
        for idx, (_, row) in enumerate(vendedor_alcada.iterrows()):
            rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
            vendedor_nome = str(row["vendedor"])
            vendedor_esc = vendedor_nome.replace("'", "\\'")
            vendedor_alcada_rows += f'<tr onclick="openVendedorPedidosModal(\'{vendedor_esc}\', true)" style="cursor: pointer;" title="Clique para ver pedidos deste vendedor"><td><span class="rank-badge {rank_class}">{idx + 1}</span></td><td>{vendedor_nome}</td><td>{fmt_money(row["total_desconto"])}</td><td>{row["qtd_pedidos"]}</td><td>{row["pct_medio"]:.2f}%</td></tr>\n'
    
    filial_alcada_rows = ""
    if filial_alcada is not None:
        for idx, (_, row) in enumerate(filial_alcada.head(10).iterrows()):
            rank_class = "gold" if idx == 0 else ("silver" if idx == 1 else ("bronze" if idx == 2 else ""))
            filial_nome = str(row["filial"])
            filial_esc = filial_nome.replace("'", "\\'")
            filial_alcada_rows += f'<tr onclick="openVendedoresDescontoModal(\'{filial_esc}\')" style="cursor: pointer;" title="Clique para ver vendedores desta filial"><td><span class="rank-badge {rank_class}">{idx + 1}</span></td><td>{filial_nome}</td><td>{fmt_money(row["total_desconto"])}</td><td>{row["qtd_pedidos"]}</td><td>{row["pct_medio"]:.2f}%</td></tr>\n'
    
    # Gerar JSON com todos os descontos para filtragem via JavaScript
    descontos_json = []
    if top_descontos is not None:
        # Mapear categorias para badges coloridos - detectar pelo prefixo
        def get_motivo_badge(categoria, original_text):
            """Retorna o texto original do motivo (sem ícones) e a classe CSS."""
            cat = str(categoria)
            orig = str(original_text)
            
            if cat.startswith('Concorrente:') or cat == 'Acompanhar Mercado':
                return orig, 'motivo-concorrencia'
            if 'Revenda' in cat:
                return orig, 'motivo-revenda'
            if cat.startswith('Prod.'):
                return orig, 'motivo-problema'
            if cat.startswith('Pgto.'):
                return orig, 'motivo-avista'
            if cat in ['Promoção', 'Promoção Empório', 'Campanha Comercial', 'Liquidação Estoque']:
                return orig, 'motivo-promocao'
            if cat.startswith('Aut.') or 'Autorizado' in cat or 'Alinhamento' in cat:
                return orig, 'motivo-autorizado'
            if 'Cooperado' in cat or 'Negociação' in cat or 'Terceiro' in cat:
                return orig, 'motivo-outros'
            if 'Cotação' in cat:
                return orig, 'motivo-outros'
            if cat == 'Funcionário':
                return orig, 'motivo-outros'
            if cat == 'Não informado':
                return orig, 'motivo-naoinformado'
            return orig, 'motivo-outros'
        
        for _, row in top_descontos.iterrows():
            if row['max_desconto_pct'] <= 0.5:
                alcada_class = 'vendedor'
                alcada_text = 'Vendedor'
            elif row['max_desconto_pct'] <= 3.0:
                alcada_class = 'gerente'
                alcada_text = 'Gerente'
            else:
                alcada_class = 'comercial'
                alcada_text = 'Comercial'
            
            motivo_cat = row.get('motivo_categoria', 'Não informado')
            motivo_orig = str(row.get('motivo_desconto', motivo_cat))
            if pd.isna(motivo_orig) or motivo_orig.strip() == '' or motivo_orig == 'nan':
                motivo_orig = motivo_cat
            motivo_text, motivo_class = get_motivo_badge(motivo_cat, motivo_orig)
            
            pct = float(row["max_desconto_pct"])
            if pct <= 0.5:
                faixa_desconto = 'Até 0,50%'
            elif pct <= 1.0:
                faixa_desconto = '0,51% a 1,00%'
            elif pct <= 2.0:
                faixa_desconto = '1,01% a 2,00%'
            elif pct <= 3.0:
                faixa_desconto = '2,01% a 3,00%'
            elif pct <= 4.0:
                faixa_desconto = '3,01% a 4,00%'
            elif pct <= 5.0:
                faixa_desconto = '4,01% a 5,00%'
            elif pct <= 6.0:
                faixa_desconto = '5,01% a 6,00%'
            elif pct <= 7.0:
                faixa_desconto = '6,01% a 7,00%'
            elif pct <= 8.0:
                faixa_desconto = '7,01% a 8,00%'
            elif pct <= 9.0:
                faixa_desconto = '8,01% a 9,00%'
            elif pct <= 10.0:
                faixa_desconto = '9,01% a 10,00%'
            else:
                faixa_desconto = 'Acima de 10%'
            
            descontos_json.append({
                'data': row["data_pedido"].strftime("%d/%m/%Y"),
                'pedido': str(row["num_pedido"]),
                'cliente': str(row["nome_conta"]),
                'vendedor': str(row["vendedor_01"]),
                'valor': float(row["valor_desconto_manual"]),
                'pct': pct,
                'faixa_desconto': faixa_desconto,
                'motivo_text': motivo_text,
                'motivo_class': motivo_class,
                'motivo_categoria': str(motivo_cat),
                'alcada_text': alcada_text,
                'alcada_class': alcada_class,
                'ano_mes': str(row["ano_mes"]),
                'valor_total': float(row["valor_pedido"]) if pd.notna(row["valor_pedido"]) else 0.0,
                'filial': str(row.get('filial_nome', ''))
            })
    
    # Converter para JSON
    descontos_json_str = json.dumps(descontos_json, ensure_ascii=False)
    periodos_json_str = json.dumps(periodos_descontos, ensure_ascii=False)
    
    # Serializar dados de todos os pedidos para modal
    todos_os_pedidos_data = []
    if dashboard_data is not None:
        todos_os_pedidos_data = dashboard_data.get('dados_por_mes', {}).get('todos', {}).get('todos_os_pedidos', [])
    todos_os_pedidos_json = json.dumps(todos_os_pedidos_data, ensure_ascii=False)
    
    # Preparar dados JSON do dashboard por mês (se disponível)
    dados_por_mes_json = "{}"
    meses_disponiveis_json = "[]"
    if dashboard_data is not None:
        dados_por_mes_json = json.dumps(dashboard_data.get('dados_por_mes', {}), ensure_ascii=False, default=str)
        meses_disponiveis_json = json.dumps(dashboard_data.get('meses_disponiveis', []), ensure_ascii=False)

    
    # Gerar linhas da tabela de análise detalhada por alçada (clicáveis para modal)
    alcada_detalhada_rows = ""
    if alcada_detalhada is not None:
        total_desconto_geral = alcada_detalhada['total_desconto'].sum() if 'total_desconto' in alcada_detalhada.columns else 1
        if total_desconto_geral == 0:
            total_desconto_geral = 1
        for _, row in alcada_detalhada.iterrows():
            alcada_nome = row['alcada']
            loja_info = loja_top_por_alcada.get(alcada_nome, {'filial': '-', 'qtd_pedidos': 0})
            alcada_class = 'vendedor' if 'Vendedor' in alcada_nome else ('gerente' if 'Gerente' in alcada_nome else 'comercial')
            pct_do_total = (row['total_desconto'] / total_desconto_geral * 100) if total_desconto_geral > 0 else 0
            # Linha clicável com data-alcada para identificar qual alçada foi clicada
            alcada_detalhada_rows += f'<tr class="alcada-row-clickable" data-alcada="{alcada_nome}" onclick="openFaixasModal(\'{alcada_nome}\')"><td><span class="alcada-badge {alcada_class}">{alcada_nome}</span></td><td><strong>{row["pct_medio"]:.2f}%</strong></td><td>{fmt_num(row["qtd_pedidos"])}</td><td>{fmt_money(row["total_desconto"])}</td><td>{pct_do_total:.1f}%</td><td>{loja_info["filial"]} ({loja_info["qtd_pedidos"]} pedidos)</td></tr>\n'

    
    # Gerar dados JSON das faixas para o JavaScript
    faixas_json = json.dumps(faixas_por_alcada, ensure_ascii=False)
    loja_top_por_alcada_json = json.dumps(loja_top_por_alcada, ensure_ascii=False)
    
    # Gerar linhas da tabela de análise regional
    regioes_rows = ""
    if top_regioes is not None:
        for idx, (_, row) in enumerate(top_regioes.iterrows()):
            regioes_rows += f'<tr><td><span class="rank-badge">{idx + 1}</span></td><td><strong>{row["mesoregiao"]}</strong></td><td>{fmt_money(row["faturamento"])}</td><td>{row["pct_faturamento"]:.1f}%</td><td>{fmt_num(row["qtd_pedidos"])}</td><td>{fmt_money(row["total_desconto"])}</td></tr>\n'
    
    # Gerar linhas da tabela de analistas
    analistas_rows = ""
    if analista_analysis is not None:
        for idx, (_, row) in enumerate(analista_analysis.head(10).iterrows()):
            analistas_rows += f'<tr><td><span class="rank-badge">{idx + 1}</span></td><td>{row["analista"]}</td><td>{fmt_money(row["faturamento"])}</td><td>{row["pct_faturamento"]:.1f}%</td><td>{fmt_num(row["qtd_pedidos"])}</td><td>{fmt_num(row["qtd_clientes"])}</td></tr>\n'
    
    # Gerar linhas da tabela de descontos por região
    desconto_regiao_rows = ""
    if desconto_regiao is not None:
        for idx, (_, row) in enumerate(desconto_regiao.head(10).iterrows()):
            desconto_regiao_rows += f'<tr><td><span class="rank-badge">{idx + 1}</span></td><td>{row["mesoregiao"]}</td><td>{fmt_money(row["total_desconto"])}</td><td>{fmt_num(row["qtd_pedidos_desconto"])}</td><td>{row["pct_medio"]:.2f}%</td></tr>\n'

    
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise de Vendas Salesforce - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* Paleta Verde e Ouro - Cores do Agro */
            --primary: #2E7D32; --primary-dark: #1B5E20; --primary-light: #4CAF50;
            --accent: #D4A017; --accent-light: #F4C430; --accent-dark: #B8860B;
            --secondary: #43A047; --tertiary: #66BB6A;
            --background: #f5f7f5; --card-bg: rgba(255, 255, 255, 0.85);
            --text-primary: #1a2e1a; --text-secondary: #4a5d4a; --border: #c8d6c8;
            --shadow: 0 4px 20px rgba(30, 70, 30, 0.1); --shadow-hover: 0 8px 30px rgba(30, 70, 30, 0.15);
            --glass-bg: rgba(255, 255, 255, 0.7); --glass-border: rgba(255, 255, 255, 0.3);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #e8f5e9 0%, #f5f7f5 50%, #fffde7 100%); color: var(--text-primary); min-height: 100vh; }}
        .page-wrapper {{ min-width: 1200px; }}
        
        /* Header Fixo com Glassmorphism */
        .header {{ 
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 50%, #1a4d1a 100%);
            color: white; padding: 24px 40px; box-shadow: 0 4px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            min-height: 120px;
            position: sticky; top: 0; z-index: 1000;
        }}
        .header-content {{ max-width: 1600px; margin: 0 auto; display: flex; justify-content: space-between; align-items: stretch; height: 100%; }}
        .header-left {{ flex: 1; }}
        .header-right {{ text-align: right; font-size: 11px; opacity: 0.95; display: flex; flex-direction: column; align-items: flex-end; justify-content: flex-start; }}
        .header-filter-container {{ position: relative; z-index: 100; }}
        .header-title {{ font-size: 26px; font-weight: 700; margin-bottom: 12px; }}
        .header-subtitle {{ font-size: 15px; opacity: 0.95; margin-bottom: 6px; }}
        .header-note {{ font-size: 12px; opacity: 0.85; font-style: italic; margin-top: 8px; }}
        
        /* Estilos para o select do filtro de mês no header */
        #filtro-mes-header {{
            padding: 8px 36px 8px 16px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            background: rgba(255,255,255,0.2);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            color: white;
            cursor: pointer;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            transition: all 0.2s ease;
            position: relative;
            z-index: 100;
        }}
        #filtro-mes-header:hover {{
            background-color: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }}
        #filtro-mes-header:focus {{
            outline: none;
            border-color: rgba(255,255,255,0.6);
            box-shadow: 0 0 0 2px rgba(255,255,255,0.2);
            background-color: rgba(255,255,255,0.25);
        }}
        /* Estilos para as opções do select - limitado pelo navegador */
        #filtro-mes-header option {{
            background: #1B5E20;
            color: white;
            padding: 10px;
        }}
        /* Para navegadores que suportam */
        #filtro-mes-header option:checked {{
            background: #2E7D32;
            color: white;
        }}
        #filtro-mes-header option:hover {{
            background: #4CAF50;
        }}
        
        .main-content {{ max-width: 1600px; margin: 0 auto; padding: 32px 40px; min-width: 1200px; }}
        
        /* KPI Cards com Glassmorphism */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px; }}
        .kpi-grid-5 {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 32px; }}
        .kpi-card {{ 
            background: var(--glass-bg); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px; padding: 24px; 
            box-shadow: var(--shadow); 
            transition: all 0.3s ease; 
            border: 1px solid var(--glass-border);
            border-left: 4px solid var(--primary);
        }}
        .kpi-card:hover {{ transform: translateY(-6px); box-shadow: 0 12px 48px rgba(46, 125, 50, 0.35), 0 8px 24px rgba(0,0,0,0.15); background: rgba(255,255,255,0.98); }}
        .kpi-label {{ font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 22px; font-weight: 700; color: var(--primary-dark); white-space: nowrap; }}
        
        /* Chart Cards com Glassmorphism */
        .charts-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 32px; max-width: 100%; overflow: hidden; }}
        .chart-card {{ 
            background: var(--card-bg); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px; padding: 24px; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.08), 0 4px 24px rgba(46, 125, 50, 0.06);
            border: 1px solid rgba(200, 214, 200, 0.5);
            transition: all 0.3s ease;
            min-width: 0;
            overflow: hidden;
        }}
        .chart-card:hover {{ transform: translateY(-6px); box-shadow: 0 12px 48px rgba(46, 125, 50, 0.35), 0 8px 24px rgba(0,0,0,0.15); background: rgba(255,255,255,0.98); }}
        .chart-card.full-width {{ grid-column: span 2; }}
        .chart-title {{ font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }}
        .chart-container {{ position: relative; height: 300px; max-width: 100%; overflow: hidden; }}
        .chart-container.tall {{ height: 350px; }}
        
        /* Table Cards com Glassmorphism */
        .table-card {{ 
            background: var(--card-bg); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px; padding: 24px; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.08), 0 4px 24px rgba(46, 125, 50, 0.06); 
            margin-bottom: 24px;
            border: 1px solid rgba(200, 214, 200, 0.5);
            transition: all 0.3s ease;
        }}
        .table-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 48px rgba(46, 125, 50, 0.35), 0 8px 24px rgba(0,0,0,0.15); background: rgba(255,255,255,0.98); }}
        .table-card.compact {{ padding: 20px; }}
        .table-card.compact td, .table-card.compact th {{ padding: 8px 12px; font-size: 13px; }}
        .table-title {{ font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
        .table-subtitle {{ font-size: 11px; color: var(--text-secondary); margin-top: -12px; margin-bottom: 12px; }}
        table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.5); border-radius: 12px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 600; color: white; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 13px; background: rgba(255,255,255,0.6); }}
        tr:hover td {{ background: rgba(46, 125, 50, 0.1); }}
        
        /* Badges com cores Verde/Ouro */
        .rank-badge {{ display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: var(--primary); color: white; font-weight: 600; font-size: 11px; }}
        .rank-badge.gold {{ background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); color: #333; box-shadow: 0 2px 8px rgba(255,215,0,0.4); }}
        .rank-badge.silver {{ background: linear-gradient(135deg, #E8E8E8 0%, #A0A0A0 100%); color: #333; }}
        .rank-badge.bronze {{ background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); color: white; }}
        .abc-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .abc-badge.a {{ background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); color: #1B5E20; border: 1px solid #A5D6A7; }}
        .abc-badge.b {{ background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%); color: #B8860B; border: 1px solid #FFD54F; }}
        .abc-badge.c {{ background: linear-gradient(135deg, #FBE9E7 0%, #FFCCBC 100%); color: #BF360C; border: 1px solid #FFAB91; }}
        
        /* Badges de Motivo de Desconto - Paleta Verde/Ouro */
        .motivo-badge {{ display: inline-block; padding: 2px 0; font-size: 11px; font-weight: 400; white-space: normal; word-break: break-word; max-width: 250px; }}
        .motivo-concorrencia {{ background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); color: #1565C0; }}
        .motivo-revenda {{ background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); color: #7B1FA2; }}
        .motivo-avista {{ background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); color: #2E7D32; }}
        .motivo-problema {{ background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%); color: #B8860B; }}
        .motivo-promocao {{ background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); color: #E65100; }}
        .motivo-autorizado {{ background: linear-gradient(135deg, #E8F5E9 0%, #A5D6A7 100%); color: #1B5E20; }}
        .motivo-fidelizacao {{ background: linear-gradient(135deg, #FFFDE7 0%, #FFF59D 100%); color: #9E7700; }}
        .motivo-naoinformado {{ background: #F5F5F5; color: #757575; }}
        .motivo-outros {{ background: linear-gradient(135deg, #ECEFF1 0%, #CFD8DC 100%); color: #455A64; }}
        
        .two-columns {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
        .three-columns {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }}
        .section-title {{ font-size: 18px; font-weight: 700; color: var(--primary-dark); margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid var(--accent); }}
        
        /* Footer com Glassmorphism */
        .footer {{ 
            text-align: center; padding: 32px 40px; color: var(--text-secondary); font-size: 13px; 
            border-top: 1px solid var(--border); margin-top: 40px; 
            background: var(--glass-bg); backdrop-filter: blur(10px);
        }}
        .footer-title {{ font-weight: 700; font-size: 15px; color: var(--primary-dark); margin-bottom: 12px; }}
        .footer-line {{ margin-bottom: 8px; }}
        .footer-note {{ margin-top: 16px; font-size: 12px; opacity: 0.7; }}
        
        /* Sistema de Abas com visual Verde/Ouro */
        .tabs-container {{ max-width: 1600px; margin: 0 auto; padding: 0 40px; min-width: 1200px; }}
        .tabs {{ 
            display: flex; gap: 8px; 
            background: var(--glass-bg); 
            backdrop-filter: blur(10px);
            padding: 8px; border-radius: 12px; margin-bottom: 24px; 
            box-shadow: var(--shadow);
            border: 1px solid var(--glass-border);
        }}
        .tab {{ 
            padding: 12px 24px; border-radius: 8px; border: none; 
            background: transparent; font-size: 14px; font-weight: 600; 
            cursor: pointer; transition: all 0.3s ease; color: var(--text-secondary); 
            font-family: 'Inter', sans-serif; 
        }}
        .tab:hover {{ background: rgba(46, 125, 50, 0.1); color: var(--primary-dark); }}
        .tab.active {{ background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; box-shadow: 0 4px 15px rgba(46,125,50,0.3); }}
        .tab-content {{ visibility: hidden; height: 0; overflow: hidden; position: absolute; width: 100%; opacity: 0; pointer-events: none; }}
        .tab-content.active {{ visibility: visible; height: auto; overflow: visible; position: relative; opacity: 1; pointer-events: auto; }}
        
        /* Badges de Alçada - Paleta Verde/Ouro */
        .alcada-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .alcada-badge.vendedor {{ background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); color: #1B5E20; border: 1px solid #A5D6A7; }}
        .alcada-badge.gerente {{ background: linear-gradient(135deg, #FFFDE7 0%, #FFF59D 100%); color: #9E7700; border: 1px solid #FFEB3B; }}
        .alcada-badge.comercial {{ background: linear-gradient(135deg, #FFF3E0 0%, #FFCC80 100%); color: #E65100; border: 1px solid #FFB74D; }}
        .alcada-badge.sem {{ background: #F5F5F5; color: #9E9E9E; }}
        
        /* Linhas clicáveis da tabela de alçada */
        .alcada-row-clickable {{ cursor: pointer; transition: all 0.2s ease; }}
        .alcada-row-clickable:hover {{ background: rgba(46, 125, 50, 0.1) !important; transform: scale(1.01); }}
        .alcada-row-clickable td:first-child::before {{ content: '👆 '; opacity: 0; transition: opacity 0.2s; }}
        .alcada-row-clickable:hover td:first-child::before {{ opacity: 1; }}
        
        /* Modal com Glassmorphism */
        /* Modal Profissional e Limpo */
        .modal-overlay {{ 
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; 
            backdrop-filter: blur(4px); 
        }}
        .modal-overlay.active {{ display: flex; overflow: hidden; }}
        .modal-content {{ 
            background: #ffffff; 
            border-radius: 12px; padding: 0; max-width: 95vw; width: 900px; max-height: 85vh; overflow: hidden;
            min-height: 0; 
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); 
            animation: modalSlideIn 0.3s ease;
            border: none;
            display: flex;
            flex-direction: column;
        }}
        @keyframes modalSlideIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .modal-header {{ 
            padding: 20px 24px; border-bottom: 1px solid #e2e8f0; 
            display: flex; justify-content: space-between; align-items: center; 
            background: #2E7D32;
            flex-shrink: 0;
        }}
        .modal-header h3 {{ margin: 0; font-size: 16px; font-weight: 600; color: #ffffff; }}
        .modal-close {{ 
            background: rgba(255, 255, 255, 0.2); border: none; color: #ffffff; font-size: 20px; 
            cursor: pointer; width: 32px; height: 32px; border-radius: 8px; 
            display: flex; align-items: center; justify-content: center; transition: all 0.2s; 
        }}
        .modal-close:hover {{ background: rgba(255, 255, 255, 0.3); color: #ffffff; }}
        .modal-body {{ padding: 0; flex: 1; overflow: auto; min-height: 0; }}
        .modal-body table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
        .modal-body th {{ 
            background: #f8fafc; padding: 16px 32px; text-align: left; 
            font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;
            border-bottom: 1px solid #e2e8f0; position: sticky; top: 0;
        }}
        .modal-body td {{ 
            padding: 16px 32px; border-bottom: 1px solid #f1f5f9; 
            color: #334155; font-size: 14px;
        }}
        .modal-body tr:last-child td {{ border-bottom: none; }}
        .modal-body tr:hover td {{ background: #f8fafc; }}
        .faixa-badge {{ 
            display: inline-block; padding: 6px 12px; border-radius: 6px; 
            font-size: 13px; font-weight: 500; 
            background: #f0fdf4; color: #15803d; border: 1px solid #dcfce7;
        }}
        @media (max-width: 1400px) {{ .three-columns {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 1200px) {{ .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} .charts-grid {{ grid-template-columns: 1fr; }} .chart-card.full-width {{ grid-column: span 1; }} .two-columns, .three-columns {{ grid-template-columns: 1fr; }} .modal-content {{ max-width: 95vw !important; }} .modal-body td, .modal-body th {{ padding: 10px 16px; font-size: 12px; }} }}
        @media (max-width: 768px) {{ .kpi-grid {{ grid-template-columns: 1fr; }} .main-content {{ padding: 16px; }} .header-content {{ flex-direction: column; }} .header-right {{ text-align: left; margin-top: 16px; }} .tabs {{ flex-wrap: wrap; }} .modal-content {{ max-width: 98vw !important; width: 98vw !important; max-height: 90vh; }} .modal-body td, .modal-body th {{ padding: 8px 10px; font-size: 11px; }} }}
    </style>
</head>
<body>
    <div class="page-wrapper">
    <header class="header">
        <div class="header-content">
            <div class="header-left">
                <h1 class="header-title"><i class="fa-solid fa-chart-line"></i> Análise das Vendas Salesforce</h1>
                <div class="header-subtitle">Período analisado: {periodo_inicio} a {periodo_fim} (ano vigente)</div>
                <div class="header-note">📋 Análise baseada no relatório de vendas do Salesforce. Ou seja, qualquer alteração no pedido dentro do ERP não reflete nesse relatório.</div>
            </div>
            <div class="header-right">
                <div class="header-filter-container">
                    <label for="filtro-mes-header" style="font-size: 13px; font-weight: 600; margin-bottom: 6px; display: block; text-align: right;">Filtrar por mês:</label>
                    <select id="filtro-mes-header" onchange="atualizarDashboardPorMes()" style="min-width: 180px;">
                        <option value="todos">Todo o período</option>
                    </select>
                </div>
            </div>
        </div>
    </header>

    <!-- Navegação por Abas -->
    <div class="tabs-container">
        <div class="tabs">
            <button class="tab active" onclick="showTab('visao-geral', event)"><i class="fa-solid fa-chart-pie"></i> Visão Geral</button>
            <button class="tab" onclick="showTab('descontos', event)"><i class="fa-solid fa-percent"></i> Análise de Descontos</button>
        </div>
    </div>

    <!-- Aba 1: Visão Geral -->
    <main class="main-content tab-content active" id="visao-geral">
        <!-- KPIs Row 1 -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">💰 Faturamento Total</div>
                <div class="kpi-value">{fmt_money(kpis['faturamento_total'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">📦 Total de Pedidos</div>
                <div class="kpi-value">{fmt_num(kpis['total_pedidos'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🎟️ Ticket Médio</div>
                <div class="kpi-value">{fmt_money(kpis['ticket_medio_pedido'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👥 Total de Clientes</div>
                <div class="kpi-value">{fmt_num(results['customers']['stats']['total_clientes'])}</div>
            </div>
        </section>

        <!-- KPIs Row 2 -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">📋 Total de Produtos</div>
                <div class="kpi-value">{fmt_num(results['products']['stats']['total_produtos'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🏪 Total de Filiais</div>
                <div class="kpi-value">{fmt_num(results['branches']['stats']['total_filiais'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👤 Total de Vendedores</div>
                <div class="kpi-value">{fmt_num(results['sellers']['stats']['total_vendedores'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">💸 Total de Descontos</div>
                <div class="kpi-value">{fmt_money(results['financial']['desconto_stats']['total_desconto'])}</div>
            </div>
        </section>

        <!-- Evolução Mensal -->
        <section class="charts-grid">
            <div class="chart-card full-width">
                <h3 class="chart-title">📈 Evolução Mensal de Faturamento</h3>
                <div class="chart-container tall">
                    <canvas id="chartEvolucao"></canvas>
                </div>
            </div>
        </section>

        <!-- Charts Row 1 -->
        <section class="charts-grid">
            <div class="chart-card">
                <h3 class="chart-title">📅 Vendas por Dia do Mês (Mês Atual)</h3>
                <div class="chart-container">
                    <canvas id="chartDiaMes"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3 class="chart-title">📊 Curva ABC - Distribuição de Faturamento</h3>
                <div style="display: flex; gap: 16px; align-items: flex-start;">
                    <div style="flex: 1; min-width: 420px; height: 360px;">
                        <canvas id="chartABC"></canvas>
                    </div>
                    <div style="width: 160px; font-size: 11px; color: var(--text-secondary); line-height: 1.5;">
                        <p style="margin-bottom: 10px;"><strong style="color: var(--primary-dark);">O que é a Curva ABC?</strong></p>
                        <p style="margin-bottom: 8px;">🟢 <strong style="color: #2E7D32;">Classe A:</strong><br>~20% dos produtos,<br>~80% do faturamento.</p>
                        <p style="margin-bottom: 8px;">🟡 <strong style="color: #B8860B;">Classe B:</strong><br>~30% dos produtos,<br>~15% do faturamento.</p>
                        <p>🔴 <strong style="color: #C62828;">Classe C:</strong><br>~50% dos produtos,<br>~5% do faturamento.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Row 2 -->
        <section class="charts-grid">
            <div class="chart-card">
                <h3 class="chart-title">👥 Segmentação de Clientes (Comercial)</h3>
                <p class="table-subtitle" style="margin-top: -16px; margin-bottom: 16px;">Classificação comercial dos cooperados baseada em performance de compras</p>
                <div class="chart-container">
                    <canvas id="chartSegmentos"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3 class="chart-title">📅 Vendas por Dia da Semana (Mês Atual)</h3>
                <div class="chart-container">
                    <canvas id="chartDiaSemana"></canvas>
                </div>
            </div>
        </section>

        <!-- Legenda Segmentação Comercial -->
        <section class="table-card" style="margin-bottom: 32px;">
            <h3 class="table-title">📋 Legenda da Segmentação Comercial</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; font-size: 13px;">
                <div><strong style="color: #2E7D32;">💚 Fiel:</strong> Cooperados com histórico consistente de compras e alta lealdade</div>
                <div><strong style="color: #F9A825;">💛 Fiel a Reter:</strong> Cooperados fieis que precisam de atenção para manter engajamento</div>
                <div><strong style="color: #C62828;">🔴 Desafio:</strong> Cooperados com baixa atividade que demandam ações de recuperação</div>
                <div><strong style="color: #43A047;">✅ Positivado:</strong> Cooperados com primeira compra realizada recentemente</div>
                <div><strong style="color: #1976D2;">🔵 Mantido:</strong> Cooperados ativos que mantêm um padrão regular de compras</div>
                <div><strong style="color: #EF6C00;">🟠 A Manter:</strong> Cooperados que requerem acompanhamento para evitar evasão</div>
            </div>
        </section>

        <!-- Seção Curva ABC Produtos -->
        <h2 class="section-title">📊 Análise Curva ABC - Produtos</h2>
        <section class="three-columns">
            <div class="table-card compact">
                <h3 class="table-title" style="color: #2E7D32;">🟢 Top 10 - Curva A</h3>
                <p class="table-subtitle">~80% do faturamento (alta prioridade)</p>
                <table>
                    <thead><tr><th>#</th><th>Produto</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                    <tbody>{produtos_a_rows}</tbody>
                </table>
            </div>
            <div class="table-card compact">
                <h3 class="table-title" style="color: #E65100;">🟠 Top 10 - Curva B</h3>
                <p class="table-subtitle">~15% do faturamento (atenção moderada)</p>
                <table>
                    <thead><tr><th>#</th><th>Produto</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                    <tbody>{produtos_b_rows}</tbody>
                </table>
            </div>
            <div class="table-card compact">
                <h3 class="table-title" style="color: #C62828;">🔴 Top 10 - Curva C</h3>
                <p class="table-subtitle">~5% do faturamento (baixo giro)</p>
                <table>
                    <thead><tr><th>#</th><th>Produto</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                    <tbody>{produtos_c_rows}</tbody>
                </table>
            </div>
        </section>

        <!-- Vendedores e Filiais -->
        <section class="two-columns">
            <div class="table-card">
                <h3 class="table-title">🏆 Top 10 Vendedores</h3>
                <table>
                    <thead><tr><th>#</th><th>Vendedor</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                    <tbody>{vendedores_rows}</tbody>
                </table>
            </div>
            <div class="table-card">
                <h3 class="table-title">🏪 Top 10 Filiais</h3>
                <table>
                    <thead><tr><th>#</th><th>Filial</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                    <tbody>{filiais_rows}</tbody>
                </table>
            </div>
        </section>

        <!-- Campanhas Table -->
        <section class="table-card">
            <h3 class="table-title">🎯 Top 5 Campanhas</h3>
            <table>
                <thead><tr><th>#</th><th>Campanha</th><th>Faturamento</th><th>Pedidos</th></tr></thead>
                <tbody>{campanhas_rows}</tbody>
            </table>
        </section>

        <!-- Performance por Mesoregião (movido da aba Regional) -->
        <section class="table-card">
            <h3 class="table-title">🗺️ Performance por Mesoregião</h3>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Mesoregião</th>
                        <th>Faturamento</th>
                        <th>% Part.</th>
                        <th>Pedidos</th>
                        <th>Descontos</th>
                    </tr>
                </thead>
                <tbody>{regioes_rows}</tbody>
            </table>
        </section>
    </main>

    <!-- Aba 2: Análise de Descontos -->
    <main class="main-content tab-content" id="descontos">
        <!-- KPIs de Descontos -->
        <section class="kpi-grid-5">
            <div class="kpi-card">
                <div class="kpi-label">💸 Total de Descontos</div>
                <div class="kpi-value">{fmt_money(desconto_stats['total_desconto'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">📊 % DE PEDIDOS COM DESCONTO DO TOTAL</div>
                <div class="kpi-value">{desconto_stats['pct_pedidos_com_desconto']:.1f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🎯 Desconto Médio</div>
                <div class="kpi-value">{fmt_money(desconto_stats['desconto_medio'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">⚠️ Maior Desconto</div>
                <div class="kpi-value">{fmt_money(desconto_stats['maior_desconto'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">📝 Pedidos c/ Desconto</div>
                <div class="kpi-value">{fmt_num(desconto_stats['pedidos_com_desconto'])}</div>
            </div>
        </section>

        <!-- Legenda das Alçadas -->
        <section class="table-card" style="margin-bottom: 24px;">
            <h3 class="table-title">📋 Regras de Alçada</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; font-size: 14px;">
                <div><span class="alcada-badge vendedor">🟢 Vendedor</span> Até 0,50% de desconto</div>
                <div><span class="alcada-badge gerente">🟡 Gerente</span> De 0,51% até 3,00%</div>
                <div><span class="alcada-badge comercial">🔴 Comercial</span> Acima de 3,00%</div>
            </div>
        </section>

        <!-- Análise Detalhada por Alçada -->
        <section class="table-card" style="margin-bottom: 24px;">
            <h3 class="table-title">📊 Análise Detalhada por Alçada</h3>
            <div style="margin-bottom: 16px; font-size: 14px;">
                <strong>% Médio de Desconto Geral:</strong> <span style="font-size: 18px; color: #E65100; font-weight: 700;">{pct_medio_geral:.2f}%</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Alçada</th>
                        <th>% Médio de Desconto</th>
                        <th>Nº de Pedidos</th>
                        <th>Total Descontos</th>
                        <th>% do Total</th>
                        <th>Loja que Mais Solicita</th>
                    </tr>
                </thead>
                <tbody>{alcada_detalhada_rows}</tbody>
            </table>
        </section>

        <!-- Gráficos de Alçada -->
        <section class="charts-grid">
            <div class="chart-card">
                <h3 class="chart-title">📊 Qtd de Pedidos com Desconto por Alçada</h3>
                <div class="chart-container">
                    <canvas id="chartAlcadaPedidos"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3 class="chart-title">💰 Valor de Desconto por Alçada</h3>
                <div class="chart-container">
                    <canvas id="chartAlcadaValor"></canvas>
                </div>
            </div>
        </section>

        <!-- Tabelas de Descontos -->
        <section class="two-columns">
            <div class="table-card">
                <h3 class="table-title">👤 Top 10 Vendedores - Descontos Concedidos</h3>
                <table>
                    <thead><tr><th>#</th><th>Vendedor</th><th>Total Desconto</th><th>Pedidos</th><th>% Médio</th></tr></thead>
                    <tbody>{vendedor_alcada_rows}</tbody>
                </table>
            </div>
            <div class="table-card">
                <h3 class="table-title">🏪 Top 10 Filiais - Descontos Concedidos</h3>
                <table>
                    <thead><tr><th>#</th><th>Filial</th><th>Total Desconto</th><th>Pedidos c/ Desc.</th><th>% Médio</th></tr></thead>
                    <tbody>{filial_alcada_rows}</tbody>
                </table>
            </div>
        </section>

        <!-- Gráfico Top 5 Motivos de Desconto -->
        <section class="table-card" style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 class="table-title" style="margin-bottom: 0;">📊 Top 5 Motivos de Desconto</h3>
                <div id="motivosTotais" style="display: flex; gap: 16px; align-items: center; font-size: 13px; color: var(--text-secondary);">
                    <span>💰 Total: <strong id="motivosTotalValor" style="color: var(--text-primary);">R$ 0,00</strong></span>
                    <span>📦 Pedidos: <strong id="motivosTotalQtd" style="color: var(--text-primary);">0</strong></span>
                </div>
            </div>
            <div style="height: 280px; position: relative;">
                <canvas id="motivosChart"></canvas>
            </div>
        </section>

        <!-- Descontos por Grupo de Produtos -->
        <section class="table-card" style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h3 class="table-title" style="margin-bottom: 4px;">📦 Descontos por Grupo de Produtos x Validade dos Produtos</h3>
                    <div style="font-size: 13px; color: var(--text-secondary);">
                        Comparativo entre a visão completa e a visão ajustada, que desconsidera itens vencidos ou a vencer em até 60 dias.
                    </div>
                </div>
                <div id="grupoProdutosImpacto" style="display: flex; gap: 12px; flex-wrap: wrap; font-size: 12px;">
                    <div style="padding: 10px 12px; border-radius: 10px; background: #fff8e1; border: 1px solid #ffe082;">
                        <div style="color: #8d6e63;">Itens excluídos</div>
                        <strong id="grupoImpactoItens" style="color: #5d4037;">0</strong>
                    </div>
                    <div style="padding: 10px 12px; border-radius: 10px; background: #ffebee; border: 1px solid #ffcdd2;">
                        <div style="color: #b71c1c;">Desconto removido</div>
                        <strong id="grupoImpactoDesconto" style="color: #c62828;">R$ 0,00</strong>
                    </div>
                    <div style="padding: 10px 12px; border-radius: 10px; background: #e8f5e9; border: 1px solid #c8e6c9;">
                        <div style="color: #2e7d32;">Visão ajustada</div>
                        <strong id="grupoImpactoAjustado" style="color: #1b5e20;">R$ 0,00</strong>
                    </div>
                    <div style="padding: 10px 12px; border-radius: 10px; background: #ede7f6; border: 1px solid #d1c4e9;">
                        <div style="color: #5e35b1;">Grupos impactados</div>
                        <strong id="grupoImpactoGrupos" style="color: #4527a0;">0</strong>
                    </div>
                </div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin: -4px 0 12px 0;">
                Selo <strong style="color: #c62828;">Impactado</strong> indica grupos com redução na visão ajustada.
                <span id="grupoImpactoMaior" style="display: none; background: #ffebee; color: #c62828; padding: 2px 8px; border-radius: 6px; font-weight: 700; margin-left: 8px; border: 1px solid #ffcdd2; font-size: 11px; align-items: center; gap: 4px;"></span>
            </div>
            <!-- Barra de controles: toggle de ordenação -->
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap;">
                <span style="font-size: 12px; color: var(--text-secondary); font-weight: 600;">Ordenar por:</span>
                <button id="btnOrdemDesconto" onclick="toggleOrdemGrupos('desconto')" style="padding: 6px 14px; border-radius: 20px; border: 1.5px solid var(--primary); font-size: 12px; font-family: 'Inter', sans-serif; cursor: pointer; font-weight: 600; background: var(--primary); color: #fff; transition: all 0.2s;">💰 Total Desconto</button>
                <button id="btnOrdemPerda" onclick="toggleOrdemGrupos('perda')" style="padding: 6px 14px; border-radius: 20px; border: 1.5px solid #c62828; font-size: 12px; font-family: 'Inter', sans-serif; cursor: pointer; font-weight: 600; background: #fff; color: #c62828; transition: all 0.2s;">📉 Perda de Ajuste</button>
            </div>
            <div class="two-columns">
                <div>
                    <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">Visão completa</div>
                    <div style="height: 300px; position: relative; margin-bottom: 12px;">
                        <canvas id="grupoProdutosChart"></canvas>
                    </div>
                    <div style="max-height: 300px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border);">
                        <table>
                            <thead style="position: sticky; top: 0; z-index: 1;">
                                <tr><th>#</th><th>Grupo de Produto</th><th>Qtd Pedidos</th><th>Total Desconto</th><th>% do Total</th><th>Ajuste</th></tr>
                            </thead>
                            <tbody id="grupo-produtos-tbody">
                                <!-- Preenchido via JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
                <div>
                    <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">Visão ajustada sem vencidos/próximos do vencimento</div>
                    <div style="height: 300px; position: relative; margin-bottom: 12px;">
                        <canvas id="grupoProdutosAjustadoChart"></canvas>
                    </div>
                    <div style="max-height: 300px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border);">
                        <table>
                            <thead style="position: sticky; top: 0; z-index: 1;">
                                <tr><th>#</th><th>Grupo de Produto</th><th>Qtd Pedidos</th><th>Total Desconto</th><th>% do Total</th><th>Ajuste</th></tr>
                            </thead>
                            <tbody id="grupo-produtos-ajustado-tbody">
                                <!-- Preenchido via JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <!-- Top impactados no período -->
            <div style="margin-top: 18px;">
                <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">Ajustes da regra por Grupo</div>
                <div id="grupoTopImpactados" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
                    <div style="padding: 12px; border: 1px dashed var(--border); border-radius: 10px; color: var(--text-secondary); font-size: 12px;">
                        Nenhum impacto calculado.
                    </div>
                </div>
            </div>
            <!-- Ranking mensal de impacto por grupo -->
            <div id="rankingMensalContainer" style="margin-top: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 13px; font-weight: 700; color: var(--text-primary);">📅 Ranking de Impacto por Grupo ao Longo dos Últimos 3 meses</div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">Evolução do desconto removido (R$) por grupo em cada mês disponível</div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Top grupos:</span>
                        <select id="rankingMensalTopN" onchange="atualizarRankingMensal()" style="padding: 4px 10px; border-radius: 8px; border: 1px solid var(--border); font-size: 12px; font-family: 'Inter', sans-serif; background: var(--card-bg); color: var(--text-primary); cursor: pointer;">
                            <option value="5">Top 5</option>
                            <option value="10">Top 10</option>
                            <option value="0">Todos impactados</option>
                        </select>
                    </div>
                </div>
                <div style="height: 320px; position: relative;">
                    <canvas id="rankingMensalChart"></canvas>
                </div>
                <div id="rankingMensalTabela" style="margin-top: 14px; max-height: 260px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border);">
                    <!-- Preenchido via JavaScript -->
                </div>
            </div>
        </section>

        <!-- Pedidos com Descontos Manuais por Período -->
        <section class="table-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 class="table-title" style="margin-bottom: 0;">📋 Pedidos com Descontos Manuais por Período</h3>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span id="total-descontos" style="font-size: 12px; color: var(--text-secondary);">0 pedidos</span>
                    <button onclick="exportarDescontosExcel()" style="padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; font-family: 'Inter', sans-serif; background: var(--card-bg); color: var(--primary); cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px; transition: all 0.2s;" onmouseover="this.style.background='var(--primary)'; this.style.color='white';" onmouseout="this.style.background='var(--card-bg)'; this.style.color='var(--primary)';">
                        <i class="fa-solid fa-file-excel"></i> Exportar Excel
                    </button>
                </div>
            </div>
            <div style="max-height: 500px; overflow-y: auto; border-radius: 8px; border: 1px solid var(--border);">
                <table>
                    <thead style="position: sticky; top: 0; z-index: 1;">
                        <tr><th>#</th><th>Data</th><th>Pedido</th><th>Cliente</th><th>Vendedor</th><th>Valor Desconto</th><th>% Desc.</th><th>Motivo</th><th>Alçada</th></tr>
                    </thead>
                    <tbody id="descontos-tbody">
                        <!-- Preenchido via JavaScript -->
                    </tbody>
                </table>
            </div>
        </section>
    </main>



    <footer class="footer">
        <div class="footer-title">Análise das Vendas Salesforce</div>
        <div class="footer-line">Período analisado: {periodo_inicio} a {periodo_fim}</div>
        <div class="footer-line">Análise baseada no relatório de vendas do Salesforce. Ou seja, qualquer alteração no pedido dentro do ERP não reflete nesse relatório.</div>
        <div class="footer-note">Dashboard gerado automaticamente em {now.strftime('%d/%m/%Y')} às {now.strftime('%H:%M')}</div>
    </footer>

    <script>
        let grupoProdutosChart = null;
        let grupoProdutosAjustadoChart = null;
        let rankingMensalChart = null;
        let ordemAtualGrupos = 'desconto';
        let cacheComparativoGrupos = null;

        Chart.defaults.font.family = 'Inter';
        Chart.defaults.color = '#666';
        
        // Função de navegação por abas
        function showTab(tabId, event) {{
            // Esconder todos os conteúdos
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            // Remover classe active de todos os botões
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            // Mostrar conteúdo selecionado
            document.getElementById(tabId).classList.add('active');
            // Ativar botão selecionado (currentTarget é sempre o botão)
            event.currentTarget.classList.add('active');
        }}
        
        const abcData = {abc_json};
        const segData = {seg_json};
        const diaData = {dia_json};
        const diaMesData = {dia_mes_json};
        const evolucaoData = {evolucao_json};
        const alcadaData = {alcada_json};
        const motivosData = {motivos_json};
        
        // Dados por mês para filtragem
        const dadosPorMes = {dados_por_mes_json};
        const mesesDisponiveis = {meses_disponiveis_json};
        
        // Variáveis globais para os gráficos (para poder atualizá-los)
        let chartEvolucao = null;
        let chartDiaMes = null;
        let chartABC = null;
        let chartSegmentos = null;
        let chartDiaSemana = null;
        let motivosChart = null;

        const leaderLinePlugin = {{
            id: 'leaderLinePlugin',
            afterDatasetsDraw(chart, args, pluginOptions) {{
                const chartId = chart?.canvas?.id;
                if (chartId !== 'chartABC' && chartId !== 'chartAlcadaPedidos') {{
                    return;
                }}
                const meta = chart.getDatasetMeta(0);
                if (!meta || !meta.data || meta.data.length === 0) {{
                    return;
                }}
                const offset = pluginOptions?.offset ?? 18;
                const extra = pluginOptions?.extra ?? 10;
                const lineWidth = pluginOptions?.lineWidth ?? 1;
                const color = pluginOptions?.color ?? '#2f3b2f';
                const ctx = chart.ctx;
                ctx.save();
                ctx.strokeStyle = color;
                ctx.lineWidth = lineWidth;
                meta.data.forEach((arc) => {{
                    if (!arc) {{
                        return;
                    }}
                    const {{ x, y, startAngle, endAngle, outerRadius }} = arc;
                    const angle = (startAngle + endAngle) / 2;
                    const sx = x + Math.cos(angle) * outerRadius;
                    const sy = y + Math.sin(angle) * outerRadius;
                    const ex = x + Math.cos(angle) * (outerRadius + offset + extra);
                    const ey = y + Math.sin(angle) * (outerRadius + offset + extra);
                    ctx.beginPath();
                    ctx.moveTo(sx, sy);
                    ctx.lineTo(ex, ey);
                    ctx.stroke();
                }});
                ctx.restore();
            }}
        }};

        // Desabilitar datalabels globalmente (ativar apenas onde necessário)
        Chart.defaults.plugins.datalabels = {{ display: false }};

        // Variável global para armazenar qtd de motivos atualizada
        let currentMotivosQtd = motivosData.qtd;
        
        // Gráfico de Motivos de Desconto
        if (motivosData.labels.length > 0) {{
            const breakMotivoLabel = (label) => {{
                if (!label || typeof label !== 'string') return label;
                const maxLen = 18;
                if (label.length <= maxLen) return label;
                const slashIdx = label.indexOf('/');
                if (slashIdx > 2 && slashIdx < label.length - 2) {{
                    return [label.slice(0, slashIdx), label.slice(slashIdx + 1)];
                }}
                const before = label.slice(0, maxLen);
                const spaceIdx = before.lastIndexOf(' ');
                if (spaceIdx > 4) {{
                    return [label.slice(0, spaceIdx), label.slice(spaceIdx + 1)];
                }}
                return [label.slice(0, maxLen), label.slice(maxLen)];
            }};

            motivosChart = new Chart(document.getElementById('motivosChart'), {{
                type: 'bar',
                data: {{
                    labels: motivosData.labels,
                    datasets: [{{
                        label: 'Valor Total do Desconto',
                        data: motivosData.data,
                        backgroundColor: [
                            'rgba(244, 67, 54, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)'
                        ],
                        borderRadius: 8,
                        borderWidth: 0,
                        barPercentage: 0.7,
                        categoryPercentage: 0.8
                    }}]
                }},
                plugins: [ChartDataLabels],
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {{ padding: {{ right: 160, left: 10, top: 10 }} }},
                    onClick: function(evt, elements) {{
                        if (elements.length > 0) {{
                            const idx = elements[0].index;
                            const motivo = motivosChart.data.labels[idx];
                            openMotivoPedidosModal(motivo);
                        }}
                    }},
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ enabled: false }},
                        datalabels: {{
                            display: true,
                            color: '#ffffff',
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            borderRadius: 4,
                            padding: 5,
                            font: {{ weight: 'bold', size: 10 }},
                            align: 'end',
                            anchor: 'end',
                            offset: 4,
                            clip: false,
                            formatter: (value, ctx) => {{
                                const valor = (value || 0).toLocaleString('pt-BR', {{ style: 'currency', currency: 'BRL' }});
                                const qtd = currentMotivosQtd[ctx.dataIndex] || 0;
                                return valor + '\\n(' + qtd + ' ped.)';
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ 
                            beginAtZero: true,
                            display: false 
                        }},
                        y: {{
                            type: 'category',
                            display: true,
                            ticks: {{
                                color: '#333333',
                                font: {{ weight: 'bold', size: 11 }},
                                padding: 4,
                                autoSkip: false,
                                callback: function(value) {{
                                    const label = this.getLabelForValue ? this.getLabelForValue(value) : value;
                                    return breakMotivoLabel(label);
                                }}
                            }},
                            grid: {{ display: false }},
                            border: {{ display: false }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Atualizar totais do painel de motivos
        function atualizarMotivosTotal(dados, qtds) {{
            const totalValor = dados.reduce((a, b) => a + b, 0);
            const totalQtd = qtds.reduce((a, b) => a + b, 0);
            const elValor = document.getElementById('motivosTotalValor');
            const elQtd = document.getElementById('motivosTotalQtd');
            if (elValor) elValor.textContent = totalValor.toLocaleString('pt-BR', {{ style: 'currency', currency: 'BRL' }});
            if (elQtd) elQtd.textContent = totalQtd.toLocaleString('pt-BR');
        }}
        atualizarMotivosTotal(motivosData.data, motivosData.qtd);

        // Gráficos de Alçada
        if (alcadaData.labels.length > 0) {{
            new Chart(document.getElementById('chartAlcadaPedidos'), {{
                type: 'doughnut',
                data: {{
                    labels: alcadaData.labels,
                    datasets: [{{ data: alcadaData.data, backgroundColor: ['#4CAF50', '#FFC107', '#F44336'], borderWidth: 0 }}]
                }},
                plugins: [ChartDataLabels],
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    layout: {{
                        padding: {{ top: 20, bottom: 65, left: 30, right: 30 }}
                    }},
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ enabled: false }},
                        datalabels: {{
                            display: true,
                            color: '#000000',
                            backgroundColor: 'transparent',
                            padding: 4,
                            font: {{ weight: 'bold', size: 12 }},
                            textAlign: 'center',
                            anchor: 'end',
                            align: 'end',
                            offset: 18,
                            clip: false,
                            formatter: (value, ctx) => {{
                                const label = ctx.chart.data.labels[ctx.dataIndex];
                                const valueLabel = value.toLocaleString('pt-BR') + ' pedidos';
                                return [label, valueLabel];
                            }}
                        }}
                    }}
                }}
            }});
            
            new Chart(document.getElementById('chartAlcadaValor'), {{
                type: 'bar',
                data: {{
                    labels: alcadaData.labels,
                    datasets: [{{ 
                        label: 'Valor Desconto', 
                        data: alcadaData.valores, 
                        backgroundColor: ['#4CAF50', '#FFC107', '#F44336'],
                        borderRadius: 8
                    }}]
                }},
                plugins: [ChartDataLabels],
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    layout: {{ padding: {{ top: 25 }} }},
                    plugins: {{ 
                        legend: {{ display: false }},
                        tooltip: {{ enabled: false }},
                        datalabels: {{
                            display: true,
                            color: '#ffffff',
                            backgroundColor: '#616161',
                            borderRadius: 6,
                            padding: 6,
                            font: {{ weight: 'bold', size: 11 }},
                            textAlign: 'center',
                            anchor: 'end',
                            align: 'end',
                            offset: 4,
                            formatter: (value) => value.toLocaleString('pt-BR', {{ style: 'currency', currency: 'BRL' }})
                        }}
                    }},
                    scales: {{ 
                        y: {{ display: false, beginAtZero: true }},
                        x: {{ grid: {{ display: false }} }}
                    }}
                }}
            }});
        }}

        // Função para formatar valores monetários
        function formatMoney(value) {{
            return 'R$ ' + value.toLocaleString('pt-BR', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        }}
        
        // Função para formatar números
        function formatNumber(value) {{
            return value.toLocaleString('pt-BR');
        }}
        
        // Função para atualizar cards KPIs
        function atualizarKPIs(dados) {{
            if (!dados || !dados.kpis) return;
            
            const kpis = dados.kpis;
            
            // Atualizar cards da primeira linha
            const kpiCards = document.querySelectorAll('.kpi-card');
            if (kpiCards.length >= 8) {{
                kpiCards[0].querySelector('.kpi-value').textContent = formatMoney(kpis.faturamento_total);
                kpiCards[1].querySelector('.kpi-value').textContent = formatNumber(kpis.total_pedidos);
                kpiCards[2].querySelector('.kpi-value').textContent = formatMoney(kpis.ticket_medio);
                kpiCards[3].querySelector('.kpi-value').textContent = formatNumber(kpis.total_clientes);
                kpiCards[4].querySelector('.kpi-value').textContent = formatNumber(kpis.total_produtos);
                kpiCards[5].querySelector('.kpi-value').textContent = formatNumber(kpis.total_filiais);
                kpiCards[6].querySelector('.kpi-value').textContent = formatNumber(kpis.total_vendedores);
                kpiCards[7].querySelector('.kpi-value').textContent = formatMoney(kpis.total_desconto);
            }}
        }}
        
        // Função para atualizar gráficos quando o filtro de mês mudar
        function atualizarGraficos(dados) {{
            if (!dados) return;
            
            // Atualizar gráfico ABC
            if (chartABC && dados.resumo_abc) {{
                const abcLabels = dados.resumo_abc.map(c => 'Classe ' + c.curva + ' (' + c.qtd_produtos + ' prod.)');
                const abcDataVals = dados.resumo_abc.map(c => c.faturamento);
                chartABC.data.labels = abcLabels;
                chartABC.data.datasets[0].data = abcDataVals;
                chartABC.update();
            }}
            
            // Atualizar gráfico de Segmentos
            if (chartSegmentos && dados.segmentos_clientes) {{
                const segLabels = dados.segmentos_clientes.map(s => {{
                    const emojiMap = {{
                        'FIEL': '💚',
                        'FIEL A RETER': '💛',
                        'DESAFIO': '🔴',
                        'POSITIVADO': '✅',
                        'MANTIDO': '🔵',
                        'A MANTER': '🟠',
                        'NÃO CLASSIFICADO': '❓'
                    }};
                    const emoji = emojiMap[s.segmento] || '❓';
                    return emoji + ' ' + s.segmento.charAt(0) + s.segmento.slice(1).toLowerCase() + ' (' + s.qtd_clientes + ')';
                }});
                const segDataVals = dados.segmentos_clientes.map(s => s.qtd_clientes);
                chartSegmentos.data.labels = segLabels;
                chartSegmentos.data.datasets[0].data = segDataVals;
                chartSegmentos.update();
            }}
            
            // Atualizar gráfico Dia do Mês
            if (chartDiaMes && dados.dia_mes) {{
                const diaMesLabels = [];
                const diaMesDataVals = [];
                const diasComDados = {{}};
                dados.dia_mes.forEach(d => {{ diasComDados[d.dia] = d.faturamento; }});
                for (let dia = 1; dia <= 31; dia++) {{
                    diaMesLabels.push(dia.toString());
                    diaMesDataVals.push(diasComDados[dia] || 0);
                }}
                chartDiaMes.data.labels = diaMesLabels;
                chartDiaMes.data.datasets[0].data = diaMesDataVals;
                chartDiaMes.data.datasets[0].backgroundColor = diaMesDataVals.map(v => v > 0 ? 'rgba(46, 125, 50, 0.7)' : 'rgba(200, 200, 200, 0.3)');
                chartDiaMes.update();
            }}
            
            // Atualizar gráfico Dia da Semana
            if (chartDiaSemana && dados.dia_semana) {{
                const diaOrder = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
                const diaSemanaLabels = [];
                const diaSemanaDataVals = [];
                diaOrder.forEach(dia => {{
                    const found = dados.dia_semana.find(d => d.dia === dia);
                    if (found) {{
                        diaSemanaLabels.push(dia);
                        diaSemanaDataVals.push(found.faturamento);
                    }}
                }});
                chartDiaSemana.data.labels = diaSemanaLabels;
                chartDiaSemana.data.datasets[0].data = diaSemanaDataVals;
                chartDiaSemana.update();
            }}
            
            // Atualizar gráfico de Evolução Mensal
            if (chartEvolucao && dados.evolucao) {{
                chartEvolucao.data.labels = dados.evolucao.map(e => e.mes);
                chartEvolucao.data.datasets[0].data = dados.evolucao.map(e => e.faturamento);
                chartEvolucao.update();
            }}

            // Atualizar gráfico de motivos
            if (dados.top_motivos_desconto && motivosChart) {{
                const normalizedLabels = dados.top_motivos_desconto.map(m => m.motivo);

                const novoMotivosData = dados.top_motivos_desconto.map(m => m.valor_total);
                const novaMotivosQtd = dados.top_motivos_desconto.map(m => m.qtd_pedidos);
                currentMotivosQtd = novaMotivosQtd;
                motivosChart.data.labels = normalizedLabels;
                motivosChart.data.datasets[0].data = novoMotivosData;
                motivosChart.update();
                atualizarMotivosTotal(
                    dados.top_motivos_desconto.map(m => m.valor_total),
                    dados.top_motivos_desconto.map(m => m.qtd_pedidos)
                );
            }}
        }}
        
        // Função auxiliar para encontrar tabela pelo título (em qualquer aba)
        function encontrarTabelaPorTitulo(tituloTexto) {{
            // Procurar em todas as abas
            const abas = ['visao-geral', 'descontos'];
            for (let abaId of abas) {{
                const aba = document.getElementById(abaId);
                if (!aba) continue;
                
                const titulos = aba.querySelectorAll('.table-title');
                for (let titulo of titulos) {{
                    if (titulo.textContent.includes(tituloTexto)) {{
                        const card = titulo.closest('.table-card');
                        if (card) {{
                            return card.querySelector('table tbody');
                        }}
                    }}
                }}
            }}
            return null;
        }}
        
        // Função para atualizar tabelas
        function atualizarTabelas(dados) {{
            if (!dados) return;
            // Atualizar tabela de Top 10 Vendedores
            if (dados.top_vendedores) {{
                const tbody = encontrarTabelaPorTitulo('Top 10 Vendedores');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.top_vendedores.forEach((v, idx) => {{
                        const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                        const row = document.createElement('tr');
                        row.style.cursor = 'pointer';
                        row.title = 'Clique para ver pedidos deste vendedor';

                        row.onclick = function() {{ openVendedorPedidosModal(v.vendedor, false); }};
                        row.innerHTML = `
                            <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                            <td>${{v.vendedor}}</td>
                            <td>${{formatMoney(v.faturamento)}}</td>
                            <td>${{formatNumber(v.qtd_pedidos)}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar tabela de Top 10 Filiais
            if (dados.top_filiais) {{
                const tbody = encontrarTabelaPorTitulo('Top 10 Filiais');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.top_filiais.forEach((f, idx) => {{
                        const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                        const row = document.createElement('tr');
                        row.style.cursor = 'pointer';
                        row.title = 'Clique para ver vendedores desta filial';
                        row.onclick = function() {{ openVendedoresModal(f.filial); }};
                        row.innerHTML = `
                            <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                            <td>${{f.filial}}</td>
                            <td>${{formatMoney(f.faturamento)}}</td>
                            <td>${{formatNumber(f.qtd_pedidos)}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar tabela de Top 5 Campanhas
            if (dados.campanhas) {{
                const tbody = encontrarTabelaPorTitulo('Top 5 Campanhas');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.campanhas.forEach((c, idx) => {{
                        const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                            <td>${{c.campanha}}</td>
                            <td>${{formatMoney(c.faturamento)}}</td>
                            <td>${{formatNumber(c.qtd_pedidos)}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar tabelas de Curva ABC (A, B, C)
            if (dados.produtos_curva_a) {{
                const visaoGeral = document.getElementById('visao-geral');
                if (visaoGeral) {{
                    const threeColumns = visaoGeral.querySelector('.three-columns');
                    if (threeColumns) {{
                        const tabelasABC = threeColumns.querySelectorAll('table tbody');
                        if (tabelasABC.length >= 3) {{
                            // Curva A
                            tabelasABC[0].innerHTML = '';
                            dados.produtos_curva_a.forEach((p, idx) => {{
                                const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                                    <td>${{p.produto}}</td>
                                    <td>${{formatMoney(p.faturamento)}}</td>
                                    <td>${{formatNumber(p.qtd_pedidos)}}</td>
                                `;
                                tabelasABC[0].appendChild(row);
                            }});
                            
                            // Curva B
                            if (dados.produtos_curva_b) {{
                                tabelasABC[1].innerHTML = '';
                                dados.produtos_curva_b.forEach((p, idx) => {{
                                    const row = document.createElement('tr');
                                    row.innerHTML = `
                                        <td>${{idx + 1}}</td>
                                        <td>${{p.produto}}</td>
                                        <td>${{formatMoney(p.faturamento)}}</td>
                                        <td>${{formatNumber(p.qtd_pedidos)}}</td>
                                    `;
                                    tabelasABC[1].appendChild(row);
                                }});
                            }}
                            
                            // Curva C
                            if (dados.produtos_curva_c) {{
                                tabelasABC[2].innerHTML = '';
                                dados.produtos_curva_c.forEach((p, idx) => {{
                                    const row = document.createElement('tr');
                                    row.innerHTML = `
                                        <td>${{idx + 1}}</td>
                                        <td>${{p.produto}}</td>
                                        <td>${{formatMoney(p.faturamento)}}</td>
                                        <td>${{formatNumber(p.qtd_pedidos)}}</td>
                                    `;
                                    tabelasABC[2].appendChild(row);
                                }});
                            }}
                        }}
                    }}
                }}
            }}
        }}
        
        // Função para atualizar aba de Descontos
        function atualizarAbaDescontos(dados) {{
            if (!dados) return;
            
            // Atualizar KPIs de descontos
            if (dados.desconto_stats) {{
                const kpiCardsDescontos = document.querySelectorAll('#descontos .kpi-card');
                if (kpiCardsDescontos.length >= 5) {{
                    kpiCardsDescontos[0].querySelector('.kpi-value').textContent = formatMoney(dados.desconto_stats.total_desconto);
                    kpiCardsDescontos[1].querySelector('.kpi-value').textContent = dados.desconto_stats.pct_pedidos_com_desconto.toFixed(1) + '%';
                    kpiCardsDescontos[2].querySelector('.kpi-value').textContent = formatMoney(dados.desconto_stats.desconto_medio);
                    kpiCardsDescontos[3].querySelector('.kpi-value').textContent = formatMoney(dados.desconto_stats.maior_desconto);
                    kpiCardsDescontos[4].querySelector('.kpi-value').textContent = formatNumber(dados.desconto_stats.pedidos_com_desconto);
                }}
            }}
            
            // Atualizar % médio geral
            if (dados.pct_medio_geral !== undefined) {{
                const pctMedioElement = document.querySelector('#descontos .table-card strong + span');
                if (pctMedioElement) {{
                    pctMedioElement.textContent = dados.pct_medio_geral.toFixed(2) + '%';
                }}
            }}
            
            // Atualizar tabela de vendedores com descontos
            if (dados.vendedor_alcada && dados.vendedor_alcada.length > 0) {{
                const tbody = encontrarTabelaPorTitulo('Top 10 Vendedores - Descontos Concedidos');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.vendedor_alcada.forEach((v, idx) => {{
                        const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                        const row = document.createElement('tr');
                        const vendedorEsc = v.vendedor.replace(/'/g, "\\'");

                        row.onclick = function() {{ openVendedorPedidosModal(v.vendedor, true); }};
                        row.style.cursor = 'pointer';
                        row.title = 'Clique para ver pedidos deste vendedor';
                        row.innerHTML = `
                            <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                            <td>${{v.vendedor}}</td>
                            <td>${{formatMoney(v.total_desconto)}}</td>
                            <td>${{formatNumber(v.qtd_pedidos)}}</td>
                            <td>${{v.pct_medio.toFixed(2)}}%</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar tabela de filiais com descontos
            if (dados.filial_alcada && dados.filial_alcada.length > 0) {{
                const tbody = encontrarTabelaPorTitulo('Top 10 Filiais - Descontos Concedidos');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.filial_alcada.forEach((f, idx) => {{
                        const rankClass = idx === 0 ? 'gold' : (idx === 1 ? 'silver' : (idx === 2 ? 'bronze' : ''));
                        const row = document.createElement('tr');
                        row.style.cursor = 'pointer';
                        row.title = 'Clique para ver vendedores desta filial';
                        row.onclick = function() {{ openVendedoresDescontoModal(f.filial); }};
                        row.innerHTML = `
                            <td><span class="rank-badge ${{rankClass}}">${{idx + 1}}</span></td>
                            <td>${{f.filial}}</td>
                            <td>${{formatMoney(f.total_desconto)}}</td>
                            <td>${{formatNumber(f.qtd_pedidos)}}</td>
                            <td>${{f.pct_medio.toFixed(2)}}%</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar gráfico de motivos de desconto
            if (dados.top_motivos_desconto && dados.top_motivos_desconto.length > 0 && motivosChart) {{
                const normalizedLabels = dados.top_motivos_desconto.map(m => m.motivo);

                const novoMotivosData = dados.top_motivos_desconto.map(m => m.valor_total);
                const novaMotivosQtd = dados.top_motivos_desconto.map(m => m.qtd_pedidos);
                currentMotivosQtd = novaMotivosQtd;
                motivosChart.data.labels = normalizedLabels;
                motivosChart.data.datasets[0].data = novoMotivosData;
                motivosChart.update();
                atualizarMotivosTotal(
                    dados.top_motivos_desconto.map(m => m.valor_total),
                    dados.top_motivos_desconto.map(m => m.qtd_pedidos)
                );
            }}
            
            // Atualizar tabela de Análise Detalhada por Alçada
            if (dados.alcada_detalhada && dados.alcada_detalhada.length > 0) {{
                // Procurar a tabela de alçada detalhada (possui alcada-row-clickable)
                const alcadaTable = document.querySelector('#descontos table tbody');
                if (alcadaTable && alcadaTable.querySelector('.alcada-row-clickable')) {{
                    alcadaTable.innerHTML = '';
                    
                    // Combinar alcada_detalhada (pct_medio) com alcada_com_desconto (total_desconto)
                    const descontoMap = {{}};
                    if (dados.alcada_com_desconto) {{
                        dados.alcada_com_desconto.forEach(a => {{
                            descontoMap[a.alcada] = a.total_desconto;
                        }});
                    }}
                    const lojaMap = dados.loja_top_por_alcada || lojaTopPorAlcada;
                    
                    // Calcular total geral de descontos para % do Total
                    const totalDescontoGeral = Object.values(descontoMap).reduce((s, v) => s + v, 0);
                    
                    dados.alcada_detalhada.forEach(a => {{
                        const alcadaNome = a.alcada;
                        const alcadaClass = alcadaNome.includes('Vendedor') ? 'vendedor' : (alcadaNome.includes('Gerente') ? 'gerente' : 'comercial');
                        const totalDesconto = descontoMap[alcadaNome] || 0;
                        const lojaInfo = lojaMap[alcadaNome];
                        const lojaLabel = lojaInfo ? `${{lojaInfo.filial}} (${{formatNumber(lojaInfo.qtd_pedidos)}} pedidos)` : '-';
                        
                        const row = document.createElement('tr');
                        row.className = 'alcada-row-clickable';
                        row.setAttribute('data-alcada', alcadaNome);
                        row.onclick = function() {{ openFaixasModal(alcadaNome); }};
                        row.innerHTML = `
                            <td><span class="alcada-badge ${{alcadaClass}}">${{alcadaNome}}</span></td>
                            <td><strong>${{a.pct_medio ? a.pct_medio.toFixed(2) : '0.00'}}%</strong></td>
                            <td>${{formatNumber(a.qtd_pedidos)}}</td>
                            <td>${{formatMoney(totalDesconto)}}</td>
                            <td>${{totalDescontoGeral > 0 ? (totalDesconto / totalDescontoGeral * 100).toFixed(1) : '0.0'}}%</td>
                            <td>${{lojaLabel}}</td>
                        `;
                        alcadaTable.appendChild(row);
                    }});
                }}
            }}
            
            // Atualizar gráficos de Alçada (Pedidos e Valor)
            if (dados.alcada_com_desconto) {{
                const alcadaLabels = dados.alcada_com_desconto.map(a => a.alcada);
                const alcadaPedidos = dados.alcada_com_desconto.map(a => a.qtd_pedidos);
                const alcadaValores = dados.alcada_com_desconto.map(a => a.total_desconto);
                
                // Atualizar gráfico de pizza de pedidos
                const chartPedidos = Chart.getChart('chartAlcadaPedidos');
                if (chartPedidos) {{
                    chartPedidos.data.labels = alcadaLabels;
                    chartPedidos.data.datasets[0].data = alcadaPedidos;
                    chartPedidos.update();
                }}
                
                // Atualizar gráfico de barras de valores
                const chartValor = Chart.getChart('chartAlcadaValor');
                if (chartValor) {{
                    chartValor.data.labels = alcadaLabels;
                    chartValor.data.datasets[0].data = alcadaValores;
                    chartValor.update();
                }}
            }}
        }}
        
        // Função para atualizar tabela de Mesoregião (agora está na aba Visão Geral)
        function atualizarTabelaMesoregiao(dados) {{
            if (!dados) return;
            
            // Atualizar tabela de regiões
            if (dados.top_regioes && dados.top_regioes.length > 0) {{
                const tbody = encontrarTabelaPorTitulo('Performance por Mesoregião');
                if (tbody) {{
                    tbody.innerHTML = '';
                    dados.top_regioes.forEach((r, idx) => {{
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><span class="rank-badge">${{idx + 1}}</span></td>
                            <td><strong>${{r.mesoregiao}}</strong></td>
                            <td>${{formatMoney(r.faturamento)}}</td>
                            <td>${{r.pct_faturamento.toFixed(1)}}%</td>
                            <td>${{formatNumber(r.qtd_pedidos)}}</td>
                            <td>${{formatMoney(r.total_desconto)}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
        }}
        
        // Função para atualizar dashboard quando o filtro de mês mudar
        function atualizarDashboardPorMes() {{
            const mesSelecionado = document.getElementById('filtro-mes-header').value;
            const dados = dadosPorMes[mesSelecionado];
            
            if (!dados) {{
                console.warn('Dados não encontrados para o período:', mesSelecionado);
                return;
            }}
            
            if (dados.vendedores_por_filial) {{
                vendedoresPorFilial = dados.vendedores_por_filial;
            }} else {{
                vendedoresPorFilial = {{}};
            }}
            if (dados.faixas_por_alcada) {{
                faixasPorAlcada = dados.faixas_por_alcada;
            }} else {{
                faixasPorAlcada = {{}};
            }}
            if (dados.loja_top_por_alcada) {{
                lojaTopPorAlcada = dados.loja_top_por_alcada;
            }} else {{
                lojaTopPorAlcada = {{}};
            }}
            
            // Atualizar KPIs
            atualizarKPIs(dados);
            
            // Atualizar gráficos
            atualizarGraficos(dados);
            
            // Atualizar tabelas
            atualizarTabelas(dados);
            
            // Atualizar aba de Descontos
            atualizarAbaDescontos(dados);
            
            // Atualizar tabela de Mesoregião (agora na aba Visão Geral)
            atualizarTabelaMesoregiao(dados);
            
            // Atualizar tabela de Grupo de Produtos
            atualizarGrupoProdutos(dados);
            
            // Atualizar tabela de descontos manuais (usa filtro do cabeçalho)
            filtrarDescontos();
            
            // Atualizar dados de todos os pedidos para modais
            if (dados.todos_os_pedidos) {{
                todosOsPedidos = dados.todos_os_pedidos;
            }}
        }}
        
        // Função para inicializar dropdown de meses
        function inicializarFiltroMes() {{
            const select = document.getElementById('filtro-mes-header');
            if (!select) {{
                console.warn('Elemento filtro-mes-header não encontrado');
                return;
            }}
            
            // Verificar se mesesDisponiveis está definido e não está vazio
            if (!mesesDisponiveis || !Array.isArray(mesesDisponiveis) || mesesDisponiveis.length === 0) {{
                console.warn('mesesDisponiveis não está disponível ou está vazio:', mesesDisponiveis);
                return;
            }}
            
            // Limpar opções existentes (exceto "Todo o período")
            while (select.children.length > 1) {{
                select.removeChild(select.lastChild);
            }}
            
            // Adicionar meses disponíveis
            mesesDisponiveis.forEach(mes => {{
                const option = document.createElement('option');
                option.value = mes.valor;
                option.textContent = mes.label;
                select.appendChild(option);
            }});
            
            console.log('Filtro de mês inicializado com', mesesDisponiveis.length, 'meses disponíveis');
        }}
        
        // Chamar inicialização quando o DOM estiver pronto
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                inicializarFiltroMes();
            }});
        }} else {{
            // DOM já está carregado, executar imediatamente
            inicializarFiltroMes();
        }}

        // Evolução Mensal
        chartEvolucao = new Chart(document.getElementById('chartEvolucao'), {{
            type: 'line',
            data: {{
                labels: evolucaoData.labels,
                datasets: [{{
                    label: 'Faturamento',
                    data: evolucaoData.data,
                    borderColor: '#2E7D32',
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2E7D32',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 8,
                    datalabels: {{
                        display: true,
                        align: 'top',
                        anchor: 'end',
                        offset: 8,
                        font: {{ weight: 'bold', size: 13 }},
                        color: '#1B5E20',
                        formatter: value => 'R$ ' + (value / 1000000).toFixed(1) + 'M'
                    }}
                }}]
            }},
            plugins: [ChartDataLabels],
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                layout: {{
                    padding: {{ top: 35, left: 40, right: 40 }}
                }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ callbacks: {{ label: ctx => 'R$ ' + ctx.raw.toLocaleString('pt-BR', {{minimumFractionDigits: 2}}) }} }}
                }},
                scales: {{
                    y: {{ 
                        display: false, 
                        beginAtZero: true
                    }},
                    x: {{ ticks: {{ font: {{ size: 11 }} }} }}
                }}
            }}
        }});

        // Função para atualizar gráficos
        function atualizarGraficos(dados) {{
            if (!dados) return;
            
            // Preparar dados para gráficos
            const diaSemanaMap = {{}};
            dados.dia_semana.forEach(item => {{
                diaSemanaMap[item.dia] = item.faturamento;
            }});
            
            const diaOrder = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
            const novoDiaData = {{
                labels: [],
                data: []
            }};
            diaOrder.forEach(dia => {{
                if (diaSemanaMap[dia] !== undefined) {{
                    novoDiaData.labels.push(dia);
                    novoDiaData.data.push(diaSemanaMap[dia]);
                }}
            }});
            
            // Atualizar gráfico de dia da semana
            if (chartDiaSemana) {{
                chartDiaSemana.data.labels = novoDiaData.labels;
                chartDiaSemana.data.datasets[0].data = novoDiaData.data;
                chartDiaSemana.update();
            }}
            
            // Atualizar gráfico de dia do mês
            if (dados.dia_mes && chartDiaMes) {{
                const diasComDados = {{}};
                dados.dia_mes.forEach(item => {{
                    diasComDados[parseInt(item.dia)] = item.faturamento;
                }});
                
                const novoDiaMesData = {{
                    labels: [],
                    data: []
                }};
                for (let dia = 1; dia <= 31; dia++) {{
                    novoDiaMesData.labels.push(dia.toString());
                    novoDiaMesData.data.push(diasComDados[dia] || 0);
                }}
                
                chartDiaMes.data.labels = novoDiaMesData.labels;
                chartDiaMes.data.datasets[0].data = novoDiaMesData.data;
                chartDiaMes.data.datasets[0].backgroundColor = novoDiaMesData.data.map(v => v > 0 ? 'rgba(46, 125, 50, 0.7)' : 'rgba(200, 200, 200, 0.3)');
                chartDiaMes.update();
            }}
            
            // Atualizar gráfico ABC
            if (dados.resumo_abc && chartABC) {{
                const novoABCData = {{
                    labels: dados.resumo_abc.map(item => `Classe ${{item.curva}} (${{item.qtd_produtos}} prod.)`),
                    data: dados.resumo_abc.map(item => item.faturamento)
                }};
                
                chartABC.data.labels = novoABCData.labels;
                chartABC.data.datasets[0].data = novoABCData.data;
                chartABC.update();
            }}
            
            // Atualizar gráfico de segmentos
            if (dados.segmentos_clientes && chartSegmentos) {{
                const segmentosOrdenados = dados.segmentos_clientes.sort((a, b) => b.qtd_clientes - a.qtd_clientes);
                const segEmojiMap = {{
                    'FIEL': '💚 Fiel',
                    'FIEL A RETER': '💛 Fiel a Reter',
                    'DESAFIO': '🔴 Desafio',
                    'POSITIVADO': '✅ Positivado',
                    'MANTIDO': '🔵 Mantido',
                    'A MANTER': '🟠 A Manter',
                    'NÃO CLASSIFICADO': '❓ Não Classificado',
                    'Champions': '🏆 Campeões',
                    'Loyal Customers': '💎 Leais',
                    'At Risk': '⚠️ Em Risco',
                    'Potential Loyalists': '⭐ Potenciais',
                    'Recent Customers': '🆕 Novos',
                    'Hibernating': '😴 Hibernando',
                    "Can't Lose Them": '❌ Perdidos',
                    'Others': '❓ Outros'
                }};
                
                const novoSegData = {{
                    labels: segmentosOrdenados.map(item => `${{segEmojiMap[item.segmento] || item.segmento}} (${{item.qtd_clientes}})`),
                    data: segmentosOrdenados.map(item => item.qtd_clientes)
                }};
                
                chartSegmentos.data.labels = novoSegData.labels;
                chartSegmentos.data.datasets[0].data = novoSegData.data;
                chartSegmentos.update();
            }}
        }}

        // Vendas por Dia do Mês
        chartDiaMes = new Chart(document.getElementById('chartDiaMes'), {{
            type: 'bar',
            data: {{
                labels: diaMesData.labels,
                datasets: [{{ 
                    label: 'Faturamento', 
                    data: diaMesData.data, 
                    backgroundColor: diaMesData.data.map(v => v > 0 ? 'rgba(46, 125, 50, 0.7)' : 'rgba(200, 200, 200, 0.3)'), 
                    borderRadius: 3 
                }}]
            }},
            options: {{
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {{ 
                    legend: {{ display: false }}, 
                    tooltip: {{ callbacks: {{ label: ctx => ctx.raw > 0 ? 'R$ ' + ctx.raw.toLocaleString('pt-BR', {{minimumFractionDigits: 2}}) : 'Sem vendas' }} }} 
                }},
                scales: {{ 
                    y: {{ beginAtZero: true, ticks: {{ callback: value => 'R$ ' + (value / 1000000).toFixed(1) + 'M' }} }},
                    x: {{ title: {{ display: true, text: 'Dia do Mês' }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});

        // Curva ABC
        const totalABC = abcData.data.reduce((a, b) => a + b, 0);
        chartABC = new Chart(document.getElementById('chartABC'), {{
            type: 'doughnut',
            data: {{
                labels: abcData.labels,
                datasets: [{{
                    data: abcData.data,
                    backgroundColor: ['#2E7D32', '#FFC107', '#E57373'],
                    borderWidth: 0,
                    datalabels: {{
                        display: true,
                        color: '#ffffff',
                        backgroundColor: '#616161',
                        borderRadius: 6,
                        padding: 6,
                        font: {{ weight: 'bold', size: 11 }},
                        textAlign: 'center',
                        anchor: 'end',
                        align: 'end',
                        offset: -25,
                        formatter: (value, ctx) => {{
                            const label = ctx.chart.data.labels[ctx.dataIndex];
                            const valorFormatado = 'R$ ' + (value / 1000000).toFixed(1) + 'M';
                            return [label, valorFormatado];
                        }}
                    }}
                }}]
            }},
            plugins: [ChartDataLabels],
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                layout: {{
                    padding: {{ top: 20, bottom: 20, left: 20, right: 20 }}
                }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ enabled: false }}
                }}
            }}
        }});

        // Segmentação de Clientes - Barras Horizontais
        chartSegmentos = new Chart(document.getElementById('chartSegmentos'), {{
            type: 'bar',
            data: {{
                labels: segData.labels,
                datasets: [{{ 
                    label: 'Clientes', 
                    data: segData.data, 
                    backgroundColor: ['#2E7D32', '#4CAF50', '#F44336', '#FF9800', '#81C784', '#A5D6A7', '#C8E6C9', '#BDBDBD'],
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true, 
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ 
                    legend: {{ display: false }},
                    tooltip: {{ callbacks: {{ label: ctx => ctx.raw + ' clientes' }} }}
                }},
                scales: {{ 
                    x: {{ beginAtZero: true, title: {{ display: true, text: 'Quantidade de Clientes' }} }}
                }}
            }}
        }});

        // Vendas por Dia da Semana
        chartDiaSemana = new Chart(document.getElementById('chartDiaSemana'), {{
            type: 'bar',
            data: {{
                labels: diaData.labels,
                datasets: [{{ 
                    label: 'Faturamento', 
                    data: diaData.data, 
                    backgroundColor: diaData.labels.map((d, i) => d === 'Sexta' ? '#2E7D32' : (d === 'Sábado' || d === 'Domingo' ? '#81C784' : '#4CAF50')),
                    borderRadius: 6,
                    datalabels: {{
                        display: true,
                        anchor: 'end',
                        align: 'top',
                        offset: 4,
                        font: {{ weight: 'bold', size: 12 }},
                        color: '#1B5E20',
                        formatter: value => 'R$ ' + (value / 1000000).toFixed(2) + 'M'
                    }}
                }}]
            }},
            plugins: [ChartDataLabels],
            options: {{
                responsive: true, 
                maintainAspectRatio: false,
                layout: {{
                    padding: {{ top: 30 }}
                }},
                plugins: {{ 
                    legend: {{ display: false }}, 
                    tooltip: {{ enabled: false }}
                }},
                scales: {{ 
                    y: {{ display: false, beginAtZero: true }}
                }}
            }}
        }});
    </script>

    <!-- Modal de Faixas de Desconto -->
    <div class="modal-overlay" id="faixasModal" onclick="closeFaixasModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="modalTitle">Faixas de Desconto</h3>
                <button class="modal-close" onclick="closeFaixasModal()">&times;</button>
            </div>
            <div class="modal-body">
                <table>
                    <thead>
                        <tr>
                            <th>Faixa de Desconto</th>
                            <th>Total Descontos</th>
                            <th>% do Total</th>
                            <th>Qtd. Pedidos</th>
                        </tr>
                    </thead>
                    <tbody id="modalTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Dados de todos os descontos e períodos disponíveis
        const todosDescontos = {descontos_json_str};
        const periodosDisponiveis = {periodos_json_str};
        
        // Dados de TODOS os pedidos para modais (inicializado vazio, preenchido via dadosPorMes)
        let todosOsPedidos = [];
        
        // Função para formatar mês/ano para exibição (2026-01 -> Jan/2026)
        function formatarPeriodo(periodo) {{
            const [ano, mes] = periodo.split('-');
            const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
            return meses[parseInt(mes) - 1] + '/' + ano;
        }}
        
        // Função para filtrar e renderizar descontos (usando filtro do cabeçalho, limitado a 100)
        function filtrarDescontos() {{
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            const tbody = document.getElementById('descontos-tbody');
            const totalSpan = document.getElementById('total-descontos');
            
            // Filtrar descontos pelo período selecionado
            const descontosFiltrados = periodoSelecionado === 'todos' 
                ? todosDescontos 
                : todosDescontos.filter(d => d.ano_mes === periodoSelecionado);
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Limitar a 100 registros para performance
            const maxRegistros = 100;
            const registrosExibidos = descontosFiltrados.slice(0, maxRegistros);
            
            // Renderizar linhas
            registrosExibidos.forEach((d, idx) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{idx + 1}}</td>
                    <td>${{d.data}}</td>
                    <td>${{d.pedido}}</td>
                    <td>${{d.cliente}}</td>
                    <td>${{d.vendedor}}</td>
                    <td>R$ ${{d.valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                    <td>${{d.pct.toFixed(2)}}%</td>
                    <td style="white-space: normal; word-break: break-word; max-width: 250px; font-size: 11px;">${{d.motivo_text}}</td>
                    <td><span class="alcada-badge ${{d.alcada_class}}">${{d.alcada_text}}</span></td>
                `;
                tbody.appendChild(row);
            }});
            
            // Atualizar total (mostra total real e quantos exibidos)
            const totalReal = descontosFiltrados.length;
            if (totalReal > maxRegistros) {{
                totalSpan.textContent = `Exibindo ${{maxRegistros}} de ${{totalReal}} pedidos`;
            }} else {{
                totalSpan.textContent = totalReal + ' pedido' + (totalReal !== 1 ? 's' : '');
            }}
        }}
        
        // Função para exportar descontos para Excel (.xlsx)
        function exportarDescontosExcel() {{
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            const descontosFiltrados = periodoSelecionado === 'todos' 
                ? todosDescontos 
                : todosDescontos.filter(d => d.ano_mes === periodoSelecionado);
            
            if (descontosFiltrados.length === 0) {{
                alert('Nenhum dado para exportar.');
                return;
            }}
            
            // Montar dados como array de objetos para o SheetJS
            const dados = descontosFiltrados.map(d => ({{
                'Data': d.data,
                'Pedido': d.pedido,
                'Cliente': d.cliente || '',
                'Vendedor': d.vendedor || '',
                'Filial': d.filial || '',
                'Valor Desconto': d.valor,
                '% Desc.': d.pct,
                'Motivo': d.motivo_text || '',
                'Al\u00e7ada': d.alcada_text || ''
            }}));
            
            // Criar workbook e worksheet
            const ws = XLSX.utils.json_to_sheet(dados);
            
            // Ajustar largura das colunas
            ws['!cols'] = [
                {{ wch: 12 }},  // Data
                {{ wch: 10 }},  // Pedido
                {{ wch: 30 }},  // Cliente
                {{ wch: 25 }},  // Vendedor
                {{ wch: 20 }},  // Filial
                {{ wch: 15 }},  // Valor Desconto
                {{ wch: 10 }},  // % Desc.
                {{ wch: 40 }},  // Motivo
                {{ wch: 12 }}   // Alçada
            ];
            
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Descontos Manuais');
            
            const periodo = periodoSelecionado === 'todos' ? 'todos_periodos' : periodoSelecionado;
            XLSX.writeFile(wb, `descontos_manuais_${{periodo}}.xlsx`);
        }}
        
        // === NOVAS FUNÇÕES PARA ANÁLISE DE IMPACTO POR GRUPO DE PRODUTOS ===
        
        // Função auxiliar para enriquecer e comparar dados completos vs ajustados
        function enriquecerComparativoGrupos(gruposOriginais, gruposAjustados) {{
            const mapOrig = {{}};
            gruposOriginais.forEach(g => {{
                mapOrig[g.grupo_produto] = g;
            }});

            const mapAj = {{}};
            gruposAjustados.forEach(g => {{
                mapAj[g.grupo_produto] = g;
            }});

            // Identificar todos os grupos únicos
            const todosOsGrupos = Array.from(new Set([
                ...gruposOriginais.map(g => g.grupo_produto),
                ...gruposAjustados.map(g => g.grupo_produto)
            ]));

            const gruposOriginaisEnriquecidos = [];
            const gruposAjustadosEnriquecidos = [];
            const topImpactados = [];

            todosOsGrupos.forEach(grupo_produto => {{
                const orig = mapOrig[grupo_produto] || {{
                    grupo_produto,
                    total_desconto: 0,
                    qtd_pedidos: 0,
                    pct_do_total: 0,
                    faturamento: 0
                }};
                const aj = mapAj[grupo_produto] || {{
                    grupo_produto,
                    total_desconto: 0,
                    qtd_pedidos: 0,
                    pct_do_total: 0,
                    faturamento: 0
                }};

                const delta_desconto = orig.total_desconto - aj.total_desconto;
                const pct_reducao = orig.total_desconto > 0 ? (delta_desconto / orig.total_desconto * 100) : 0;
                const impactado = delta_desconto > 0.01;

                const itemOrig = {{
                    ...orig,
                    delta_desconto,
                    pct_reducao,
                    impactado
                }};

                const itemAj = {{
                    ...aj,
                    delta_desconto,
                    pct_reducao,
                    impactado
                }};

                gruposOriginaisEnriquecidos.push(itemOrig);
                gruposAjustadosEnriquecidos.push(itemAj);

                if (impactado) {{
                    topImpactados.push({{
                        grupo_produto,
                        delta_desconto,
                        pct_reducao
                    }});
                }}
            }});

            // Ordenar impactados pela perda absoluta (delta_desconto)
            topImpactados.sort((a, b) => b.delta_desconto - a.delta_desconto);

            return {{
                gruposOriginaisEnriquecidos,
                gruposAjustadosEnriquecidos,
                topImpactados
            }};
        }}

        function formatarBadgeAjuste(grupo) {{
            if (!grupo || !grupo.impactado) {{
                return '<span style="color: #2e7d32; font-weight: 600;">Sem ajuste</span>';
            }}

            return `
                <div style="display: flex; flex-direction: column; gap: 2px;">
                    <span style="display: inline-flex; align-items: center; width: fit-content; padding: 2px 8px; border-radius: 999px; background: #ffebee; color: #c62828; font-size: 11px; font-weight: 700;">Impactado</span>
                    <span style="color: #c62828; font-weight: 600;">-${{formatMoney(grupo.delta_desconto || 0)}}</span>
                    <span style="color: #8d6e63; font-size: 11px;">${{Number(grupo.pct_reducao || 0).toFixed(1)}}%</span>
                </div>
            `;
        }}

        function renderizarGrupoProdutos(grupos, tbodyId, chartId, chartKey) {{
            const tbody = document.getElementById(tbodyId);
            const chartCanvas = document.getElementById(chartId);
            if (!tbody) return;

            tbody.innerHTML = '';

            if (!grupos || grupos.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">Nenhum dado disponível</td></tr>';
                if (chartKey === 'principal' && grupoProdutosChart) {{
                    grupoProdutosChart.destroy();
                    grupoProdutosChart = null;
                }}
                if (chartKey === 'ajustado' && grupoProdutosAjustadoChart) {{
                    grupoProdutosAjustadoChart.destroy();
                    grupoProdutosAjustadoChart = null;
                }}
                return;
            }}

            grupos.forEach((g, idx) => {{
                const row = document.createElement('tr');
                if (g.impactado) {{
                    row.style.background = 'rgba(255, 235, 238, 0.55)';
                }}
                row.innerHTML = `
                    <td><span class="rank-badge">${{idx + 1}}</span></td>
                    <td>
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <span>${{g.grupo_produto}}</span>
                            ${{g.impactado ? '<span style="display: inline-flex; align-items: center; width: fit-content; padding: 2px 8px; border-radius: 999px; background: #ffebee; color: #c62828; font-size: 11px; font-weight: 700;">Impactado</span>' : ''}}
                        </div>
                    </td>
                    <td>${{formatNumber(g.qtd_pedidos)}}</td>
                    <td>${{formatMoney(g.total_desconto)}}</td>
                    <td>${{Number(g.pct_do_total || 0).toFixed(2)}}%</td>
                    <td>${{formatarBadgeAjuste(g)}}</td>
                `;
                tbody.appendChild(row);
            }});

            const top5 = grupos.slice(0, 5);
            if (!chartCanvas) return;

            if (chartKey === 'principal' && grupoProdutosChart) {{
                grupoProdutosChart.destroy();
            }}
            if (chartKey === 'ajustado' && grupoProdutosAjustadoChart) {{
                grupoProdutosAjustadoChart.destroy();
            }}

            // Modo perda: exibir delta no grafico
            const modoPerda = (typeof ordemAtualGrupos !== 'undefined') && ordemAtualGrupos === 'perda';
            const chartLabel = modoPerda ? 'Perda de Ajuste' : 'Total Desconto';

            const chart = new Chart(chartCanvas, {{
                type: 'bar',
                data: {{
                    labels: top5.map(g => g.grupo_produto),
                    datasets: [{{
                        label: chartLabel,
                        data: top5.map(g => modoPerda ? (g.delta_desconto || 0) : g.total_desconto),
                        backgroundColor: chartKey === 'principal' ? 'rgba(220, 38, 38, 0.88)' : 'rgba(234, 88, 12, 0.88)',
                        borderColor: 'transparent',
                        borderWidth: 0,
                        borderRadius: 8,
                        barPercentage: 0.7
                    }}]

                }},

                plugins: [ChartDataLabels],

                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {{ padding: {{ right: 120, left: 10 }} }},

                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ enabled: false }},
                        datalabels: {{
                            display: true,
                            color: '#ffffff',
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            borderRadius: 4,
                            padding: 5,
                            font: {{ weight: 'bold', size: 10 }},
                            align: 'end',
                            anchor: 'end',
                            offset: 4,
                            clip: false,
                            formatter: (value, ctx) => {{
                                const grupo = top5[ctx.dataIndex] || {{}};
                                if (modoPerda) {{
                                    const pct = grupo.pct_reducao || 0;
                                    return '-' + formatMoney(value) + ' (' + Number(pct).toFixed(1) + '% red.)';
                                }}
                                const pct = grupo.pct_do_total || 0;
                                return formatMoney(value) + ' (' + Number(pct).toFixed(1) + '%)';
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ beginAtZero: true, display: false }},
                        y: {{
                            ticks: {{
                                color: '#333333',
                                font: {{ weight: 'bold', size: 11 }},
                                callback: function(value) {{
                                    const label = this.getLabelForValue ? this.getLabelForValue(value) : value;
                                    if (typeof label === 'string' && label.length > 20) {{
                                        return label.substring(0, 20) + '...';
                                    }}
                                    return label;
                                }}
                            }},
                            grid: {{ display: false }},
                            border: {{ display: false }}
                        }}
                    }}
                }}
            }});


            if (chartKey === 'principal') {{
                grupoProdutosChart = chart;
            }} else {{
                grupoProdutosAjustadoChart = chart;
            }}
        }}

        // Funcao para gerar o ranking mensal de impacto por grupo
        function gerarRankingMensalImpacto(topN) {{
            const topNVal = parseInt(topN || document.getElementById('rankingMensalTopN')?.value || 5);

            // Coletar todos os meses disponíveis (exceto 'todos') - limitados aos últimos 3 meses
            const mesesChaves = Object.keys(dadosPorMes).filter(k => k !== 'todos').sort().slice(-3);
            if (mesesChaves.length === 0) {{
                // Sem dados mensais - ocultar bloco inteiro
                const contEl = document.getElementById('rankingMensalContainer');
                if (contEl) contEl.style.display = 'none';
                return;
            }}

            // Para cada mes, calcular o comparativo de grupos
            const gruposDeltasPorMes = {{}};
            const todosGruposImpactados = new Set();

            mesesChaves.forEach(mes => {{
                const dadosMes = dadosPorMes[mes];
                if (!dadosMes) return;
                const gruposMes = dadosMes.desconto_por_grupo || [];
                const gruposAjMes = dadosMes.desconto_por_grupo_ajustado || [];
                const comp = enriquecerComparativoGrupos(gruposMes, gruposAjMes);
                comp.topImpactados.forEach(g => {{
                    todosGruposImpactados.add(g.grupo_produto);
                    if (!gruposDeltasPorMes[g.grupo_produto]) gruposDeltasPorMes[g.grupo_produto] = {{}};
                    gruposDeltasPorMes[g.grupo_produto][mes] = g.delta_desconto || 0;
                }});
                comp.gruposOriginaisEnriquecidos.filter(g => g.impactado).forEach(g => {{
                    todosGruposImpactados.add(g.grupo_produto);
                    if (!gruposDeltasPorMes[g.grupo_produto]) gruposDeltasPorMes[g.grupo_produto] = {{}};
                    if (!gruposDeltasPorMes[g.grupo_produto][mes]) {{
                        gruposDeltasPorMes[g.grupo_produto][mes] = g.delta_desconto || 0;
                    }}
                }});
            }});

            if (todosGruposImpactados.size === 0) {{
                const tabelaEl2 = document.getElementById('rankingMensalTabela');
                const canvasEl2 = document.getElementById('rankingMensalChart');
                if (canvasEl2) canvasEl2.parentElement.style.display = 'none';
                if (tabelaEl2) tabelaEl2.innerHTML = `
                    <div style="padding:16px;text-align:center;color:var(--text-secondary);font-size:12px;border:1px dashed var(--border);border-radius:8px;">
                        Nenhum impacto de validade detectado nos meses individuais.<br>
                        <span style="font-size:11px;">O impacto é calculado no período consolidado.</span>
                    </div>
                `;
                return;
            }}

            // Calcular total de impacto por grupo para rankeamento
            const gruposRankeados = Array.from(todosGruposImpactados)
                .map(nome => ({{
                    nome,
                    totalDelta: mesesChaves.reduce((s, m) => s + (gruposDeltasPorMes[nome]?.[m] || 0), 0)
                }}))
                .sort((a, b) => b.totalDelta - a.totalDelta);

            const gruposFiltrados = topNVal > 0 ? gruposRankeados.slice(0, topNVal) : gruposRankeados;

            // Labels dos meses formatados
            const labelsMeses = mesesChaves.map(m => {{
                const parts = m.split('-');
                if (parts.length === 2) {{
                    const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
                    return meses[parseInt(parts[1]) - 1] + '/' + parts[0].slice(2);
                }}
                return m;
            }});

            // Paleta de cores para os grupos
            const palette = [
                'rgba(229,57,53,0.85)', 'rgba(255,152,0,0.85)', 'rgba(33,150,243,0.85)',
                'rgba(76,175,80,0.85)', 'rgba(156,39,176,0.85)', 'rgba(0,188,212,0.85)',
                'rgba(255,193,7,0.85)', 'rgba(244,67,54,0.85)', 'rgba(103,58,183,0.85)',
                'rgba(0,150,136,0.85)'
            ];

            const datasets = gruposFiltrados.map((grupo, idx) => ({{
                label: grupo.nome,
                data: mesesChaves.map(m => gruposDeltasPorMes[grupo.nome]?.[m] || 0),
                backgroundColor: palette[idx % palette.length].replace('0.85', '0.75'),
                borderColor: palette[idx % palette.length],
                borderWidth: 2,
                borderRadius: 5,
            }}));

            const canvas = document.getElementById('rankingMensalChart');
            if (!canvas) return;
            canvas.parentElement.style.display = '';
            // Garantir que o container pai esteja visível
            const containerEl = document.getElementById('rankingMensalContainer');
            if (containerEl) containerEl.style.display = '';

            if (rankingMensalChart) {{
                rankingMensalChart.destroy();
                rankingMensalChart = null;
            }}

            rankingMensalChart = new Chart(canvas, {{
                type: 'bar',
                data: {{ labels: labelsMeses, datasets }},
                plugins: [ChartDataLabels],
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {{ padding: {{ top: 10 }} }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'bottom',
                            labels: {{ font: {{ size: 11 }}, padding: 14, boxWidth: 14 }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: ctx => ` ${{ctx.dataset.label}}: ${{formatMoney((ctx.parsed && ctx.parsed.y !== undefined) ? ctx.parsed.y : 0)}}`
                            }}
                        }},
                        datalabels: {{
                            display: false,
                            color: '#fff',
                            backgroundColor: ctx => datasets[ctx.datasetIndex]?.borderColor || '#333',
                            borderRadius: 3,
                            padding: {{ top: 2, bottom: 2, left: 4, right: 4 }},
                            font: {{ size: 9, weight: 'bold' }},
                            anchor: 'end',
                            align: 'end',
                            offset: 2,
                            clip: false,
                            formatter: v => v >= 1000 ? 'R$ ' + (v/1000).toFixed(0) + 'k' : formatMoney(v)
                        }}
                    }},
                    scales: {{
                        x: {{
                            stacked: false,
                            grid: {{ display: false }},
                            ticks: {{ font: {{ size: 11 }}, color: '#555' }}
                        }},
                        y: {{
                            beginAtZero: true,
                            grid: {{ color: 'rgba(0,0,0,0.06)' }},
                            ticks: {{
                                font: {{ size: 10 }},
                                color: '#555',
                                callback: v => 'R$ ' + (v >= 1000 ? (v/1000).toFixed(0) + 'k' : v.toFixed(0))
                            }}
                        }}
                    }}
                }}
            }});

            // Tabela de ranking mensal
            const tabelaEl = document.getElementById('rankingMensalTabela');
            if (tabelaEl) {{
                const mesHeaders = labelsMeses.map(m => `<th>${{m}}</th>`).join('');
                const rows = gruposFiltrados.map((grupo, idx) => {{
                    const cor = palette[idx % palette.length];
                    const corBg = cor.replace('0.85', '0.12');
                    const celulas = mesesChaves.map(m => {{
                        const v = gruposDeltasPorMes[grupo.nome]?.[m] || 0;
                        return v > 0
                            ? `<td style="color:#c62828;font-weight:600;">-${{formatMoney(v)}}</td>`
                            : `<td style="color:#bbb;">—</td>`;
                    }}).join('');
                    const totalDelta = grupo.totalDelta;
                    return `
                        <tr style="background:${{corBg}}">
                            <td><span class="rank-badge">${{idx+1}}</span></td>
                            <td style="font-weight:700;">${{grupo.nome}}</td>
                            ${{celulas}}
                            <td style="color:#c62828;font-weight:700;">-${{formatMoney(totalDelta)}}</td>
                        </tr>
                    `;
                }}).join('');
                tabelaEl.innerHTML = `
                    <table>
                        <thead style="position:sticky;top:0;z-index:1;">
                            <tr>
                                <th>#</th>
                                <th>Grupo</th>
                                ${{mesHeaders}}
                                <th>Total removido</th>
                            </tr>
                        </thead>
                        <tbody>${{rows}}</tbody>
                    </table>
                `;
            }}
        }}

        function atualizarRankingMensal() {{
            const topN = document.getElementById('rankingMensalTopN')?.value || 5;
            gerarRankingMensalImpacto(topN);
        }}

        function toggleOrdemGrupos(ordem) {{
            ordemAtualGrupos = ordem;
            
            const btnDesconto = document.getElementById('btnOrdemDesconto');
            const btnPerda = document.getElementById('btnOrdemPerda');
            
            if (ordem === 'perda') {{
                if (btnDesconto) {{
                    btnDesconto.style.background = '#fff';
                    btnDesconto.style.color = 'var(--primary)';
                    btnDesconto.style.border = '1.5px solid var(--primary)';
                }}
                if (btnPerda) {{
                    btnPerda.style.background = '#c62828';
                    btnPerda.style.color = '#fff';
                    btnPerda.style.border = '1.5px solid #c62828';
                }}
            }} else {{
                if (btnDesconto) {{
                    btnDesconto.style.background = 'var(--primary)';
                    btnDesconto.style.color = '#fff';
                    btnDesconto.style.border = '1.5px solid var(--primary)';
                }}
                if (btnPerda) {{
                    btnPerda.style.background = '#fff';
                    btnPerda.style.color = '#c62828';
                    btnPerda.style.border = '1.5px solid #c62828';
                }}
            }}
            
            if (cacheComparativoGrupos) {{
                const aplicarOrdem = (lista) => {{
                    if (ordemAtualGrupos === 'perda') {{
                        return [...lista].sort((a, b) => (b.delta_desconto || 0) - (a.delta_desconto || 0));
                    }}
                    return [...lista].sort((a, b) => (b.total_desconto || 0) - (a.total_desconto || 0));
                }};
                
                renderizarGrupoProdutos(aplicarOrdem(cacheComparativoGrupos.gruposOriginaisEnriquecidos), 'grupo-produtos-tbody', 'grupoProdutosChart', 'principal');
                renderizarGrupoProdutos(aplicarOrdem(cacheComparativoGrupos.gruposAjustadosEnriquecidos), 'grupo-produtos-ajustado-tbody', 'grupoProdutosAjustadoChart', 'ajustado');
            }}
        }}

        // Funcao para atualizar tabela e grafico de Grupo de Produtos
        function atualizarGrupoProdutos(dados) {{
            if (!dados) return;

            const grupos = dados.desconto_por_grupo || [];
            const gruposAjustados = dados.desconto_por_grupo_ajustado || [];
            const impacto = dados.desconto_por_grupo_impacto || {{}};
            const comparativo = enriquecerComparativoGrupos(grupos, gruposAjustados);
            cacheComparativoGrupos = comparativo;

            const aplicarOrdem = (lista) => {{
                if (ordemAtualGrupos === 'perda') {{
                    return [...lista].sort((a, b) => (b.delta_desconto || 0) - (a.delta_desconto || 0));
                }}
                return [...lista].sort((a, b) => (b.total_desconto || 0) - (a.total_desconto || 0));
            }};

            renderizarGrupoProdutos(aplicarOrdem(comparativo.gruposOriginaisEnriquecidos), 'grupo-produtos-tbody', 'grupoProdutosChart', 'principal');
            renderizarGrupoProdutos(aplicarOrdem(comparativo.gruposAjustadosEnriquecidos), 'grupo-produtos-ajustado-tbody', 'grupoProdutosAjustadoChart', 'ajustado');

            const itens = document.getElementById('grupoImpactoItens');
            const desconto = document.getElementById('grupoImpactoDesconto');
            const ajustado = document.getElementById('grupoImpactoAjustado');
            const gruposImpactados = document.getElementById('grupoImpactoGrupos');
            const maiorImpacto = document.getElementById('grupoImpactoMaior');
            const topImpactadosEl = document.getElementById('grupoTopImpactados');

            if (itens) {{
                const resumoItens = Number(impacto.itens_excluidos || 0).toLocaleString('pt-BR');
                const resumoStatus = `V: ${{impacto.vencido || 0}} | 30d: ${{impacto.vence_30 || 0}} | 60d: ${{impacto.vence_60 || 0}}`;
                itens.textContent = `${{resumoItens}} (${{resumoStatus}})`;
            }}
            if (desconto) {{
                const pct = Number(impacto.pct_desconto_excluido || 0).toFixed(1);
                desconto.textContent = `${{formatMoney(impacto.total_desconto_excluido || 0)}} (${{pct}}%)`;
            }}
            if (ajustado) {{
                ajustado.textContent = formatMoney(impacto.total_desconto_ajustado || 0);
            }}
            if (gruposImpactados) {{
                gruposImpactados.textContent = formatNumber(impacto.grupos_impactados || comparativo.topImpactados.length || 0);
            }}
            if (maiorImpacto) {{
                if (comparativo.topImpactados.length > 0) {{
                    const top = comparativo.topImpactados[0];
                    maiorImpacto.style.display = 'inline-flex';
                    maiorImpacto.innerHTML = `⚡ Maior ajuste: ${{top.grupo_produto}} (-${{formatMoney(top.delta_desconto || 0)}})`;
                }} else {{
                    maiorImpacto.style.display = 'none';
                }}
            }}
            if (topImpactadosEl) {{
                if (comparativo.topImpactados.length === 0) {{
                    topImpactadosEl.innerHTML = `
                        <div style="padding: 12px; border: 1px dashed var(--border); border-radius: 10px; color: var(--text-secondary); font-size: 12px;">
                            Nenhum impacto calculado no periodo selecionado.
                        </div>
                    `;
                }} else {{
                    topImpactadosEl.innerHTML = comparativo.topImpactados.map((grupo, idx) => `
                        <div style="padding: 12px; border-radius: 10px; background: #fff5f5; border: 1px solid #ffcdd2;">
                            <div style="font-size: 11px; color: #c62828; font-weight: 700; margin-bottom: 6px;">#${{idx + 1}}</div>
                            <div style="font-size: 13px; font-weight: 700; color: #3e2723; margin-bottom: 6px;">${{grupo.grupo_produto}}</div>
                            <div style="font-size: 12px; color: #5d4037;">Removido: <strong>${{formatMoney(grupo.delta_desconto || 0)}}</strong></div>
                            <div style="font-size: 12px; color: #6d4c41;">Reducao: ${{Number(grupo.pct_reducao || 0).toFixed(1)}}%</div>
                        </div>
                    `).join('');
                }}
            }}
            
            gerarRankingMensalImpacto();
        }}
        
        // Inicializar tabelas ao carregar
        document.addEventListener('DOMContentLoaded', function() {{
            // Renderizar tabela de descontos inicial
            filtrarDescontos();
            
            // Renderizar tabela e gráfico de grupo de produtos inicial
            const dadosIniciais = dadosPorMes['todos'];
            if (dadosIniciais) {{
                atualizarGrupoProdutos(dadosIniciais);
                // CRITICAL: Inicializar todosOsPedidos com os dados do período completo
                if (dadosIniciais.todos_os_pedidos) {{
                    todosOsPedidos = dadosIniciais.todos_os_pedidos;
                }}
            }}
        }});

        // Dados das faixas de desconto por alçada
        let faixasPorAlcada = {faixas_json};
        let lojaTopPorAlcada = {loja_top_por_alcada_json};

        function formatMoney(value) {{
            return 'R$ ' + value.toLocaleString('pt-BR', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        }}

        function formatNumber(value) {{
            return value.toLocaleString('pt-BR');
        }}

        function openFaixasModal(alcada) {{
            const modal = document.getElementById('faixasModal');
            const title = document.getElementById('modalTitle');
            const tbody = document.getElementById('modalTableBody');
            
            // Definir título baseado na alçada
            title.innerHTML = 'Faixas de Desconto - ' + alcada;
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Preencher com dados da alçada selecionada
            const faixas = faixasPorAlcada[alcada] || [];
            
            // Calcular total de descontos do período para % do Total
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            const descontosPeriodo = periodoSelecionado === 'todos'
                ? todosDescontos
                : todosDescontos.filter(d => d.ano_mes === periodoSelecionado);
            const totalDescontoPeriodo = descontosPeriodo.reduce((sum, d) => sum + d.valor, 0);
            
            if (faixas.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">Nenhum dado disponível</td></tr>';
            }} else {{
                faixas.forEach(faixa => {{
                    const pctTotal = totalDescontoPeriodo > 0 ? (faixa.total_desconto / totalDescontoPeriodo * 100).toFixed(1) : '0.0';
                    const row = document.createElement('tr');
                    row.style.cursor = 'pointer';
                    row.title = 'Clique para ver pedidos desta faixa';
                    row.onclick = function() {{ openFaixaPedidosModal(alcada, faixa.faixa); }};
                    row.innerHTML = `
                        <td><span class="faixa-badge">${{faixa.faixa}}</span></td>
                        <td><strong>${{formatMoney(faixa.total_desconto)}}</strong></td>
                        <td>${{pctTotal}}%</td>
                        <td>${{formatNumber(faixa.qtd_pedidos)}}</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}

        function closeFaixasModal(event) {{
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('faixasModal').classList.remove('active');
        }}
        
        // Função para abrir modal de pedidos de uma faixa específica
        function openFaixaPedidosModal(alcada, faixa) {{
            const modal = document.getElementById('vendedorPedidosModal');
            const title = document.getElementById('vendedorPedidosModalTitle');
            const tbody = document.getElementById('vendedorPedidosModalBody');
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            
            // Definir título
            title.innerHTML = '📊 Pedidos - ' + alcada + ' - Faixa ' + faixa;
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Atualizar cabeçalho da tabela
            const tableHead = modal.querySelector('table thead tr');
            if (tableHead) {{
                tableHead.innerHTML = `
                    <th>#</th>
                    <th>Data</th>
                    <th>Pedido</th>
                    <th>Cliente</th>
                    <th>Vendedor</th>
                    <th>Valor Desconto</th>
                    <th>% Desc.</th>
                    <th>Motivo</th>
                `;
            }}
            
            // Determinar nome da alçada esperada (remover "Alçada " se presente e tirar legenda)
            const alcadaNome = alcada.replace('Alçada ', '').split(' (')[0].trim();
            
            // Filtrar pedidos pela alçada e faixa de desconto usando a faixa pré-computada
            const pedidosFaixa = todosDescontos.filter(d => {{
                const mesmoPeriodo = periodoSelecionado === 'todos' || d.ano_mes === periodoSelecionado;
                const mesmaAlcada = d.alcada_text === alcadaNome;
                const mesmaFaixa = d.faixa_desconto === faixa;
                return mesmoPeriodo && mesmaAlcada && mesmaFaixa;
            }});
            
            if (pedidosFaixa.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #999;">Nenhum pedido encontrado para esta faixa/período.</td></tr>`;
            }} else {{
                pedidosFaixa.forEach((d, idx) => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="rank-badge">${{idx + 1}}</span></td>
                        <td>${{d.data}}</td>
                        <td>${{d.pedido}}</td>
                        <td>${{d.cliente}}</td>
                        <td>${{d.vendedor}}</td>
                        <td>R$ ${{d.valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td>${{d.pct.toFixed(2)}}%</td>
                        <td style="white-space: normal; word-break: break-word; max-width: 250px; font-size: 11px;">${{d.motivo_text}}</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}

        // Fechar com ESC
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeFaixasModal();
                closeVendedoresModal();
                closeVendedorPedidosModal();
                closeMotivoPedidosModal();
            }}
        }});
        
        // Dados de vendedores por filial
        let vendedoresPorFilial = {vendedores_por_filial_json};
        
        function openVendedoresModal(filial) {{
            const modal = document.getElementById('vendedoresModal');
            const title = document.getElementById('vendedoresModalTitle');
            const tbody = document.getElementById('vendedoresModalBody');
            
            // Definir título
            title.innerHTML = '👥 Vendedores - ' + filial;
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Preencher com dados dos vendedores da filial
            const vendedores = vendedoresPorFilial[filial] || [];
            
            if (vendedores.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">Nenhum vendedor encontrado</td></tr>';
            }} else {{
                vendedores.forEach((v, idx) => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="rank-badge">${{idx + 1}}</span></td>
                        <td>${{v.vendedor}}</td>
                        <td><strong>${{formatMoney(v.faturamento)}}</strong></td>
                        <td>${{formatNumber(v.qtd_pedidos)}}</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}
        
        function closeVendedoresModal(event) {{
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('vendedoresModal').classList.remove('active');
        }}

        function openVendedorPedidosModal(vendedor, showDiscounts = true) {{
            const modal = document.getElementById('vendedorPedidosModal');
            const title = document.getElementById('vendedorPedidosModalTitle');
            const tbody = document.getElementById('vendedorPedidosModalBody');
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            
            // Definir título
            title.innerHTML = '👤 Pedidos - ' + vendedor;
            
            // Limpar tabela
            tbody.innerHTML = '';

            // Atualizar cabeçalho da tabela se necessário
            const tableHead = modal.querySelector('table thead tr');
            if (tableHead) {{
                if (showDiscounts) {{
                    tableHead.innerHTML = `
                        <th>#</th>
                        <th>Data</th>
                        <th>Pedido</th>
                        <th>Cliente</th>
                        <th>Valor Desconto</th>
                        <th>% Desc.</th>
                        <th>Motivo</th>
                    `;
                }} else {{
                    tableHead.innerHTML = `
                        <th>#</th>
                        <th>Data</th>
                        <th>Pedido</th>
                        <th>Cliente</th>
                        <th>Valor</th>
                    `;
                }}
            }}
            
            if (showDiscounts) {{
                // Filtrar de todosDescontos (apenas pedidos com desconto)
                const pedidosVendedor = todosDescontos.filter(d => {{
                    const mesmoVendedor = d.vendedor === vendedor;
                    const mesmoPeriodo = periodoSelecionado === 'todos' || d.ano_mes === periodoSelecionado;
                    return mesmoVendedor && mesmoPeriodo;
                }});
                
                if (pedidosVendedor.length === 0) {{
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #999;">Nenhum pedido encontrado para este período.</td></tr>`;
                }} else {{
                    pedidosVendedor.forEach((d, idx) => {{
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><span class="rank-badge">${{idx + 1}}</span></td>
                            <td>${{d.data}}</td>
                            <td>${{d.pedido}}</td>
                            <td>${{d.cliente}}</td>
                            <td>R$ ${{d.valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                            <td>${{d.pct.toFixed(2)}}%</td>
                            <td style="white-space: normal; word-break: break-word; max-width: 250px; font-size: 11px;">${{d.motivo_text}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }} else {{
                // Filtrar de todosOsPedidos (TODOS os pedidos, não apenas com desconto)
                const pedidosVendedor = todosOsPedidos.filter(d => {{
                    const mesmoVendedor = d.vendedor === vendedor;
                    const mesmoPeriodo = periodoSelecionado === 'todos' || d.ano_mes === periodoSelecionado;
                    return mesmoVendedor && mesmoPeriodo;
                }});
                
                if (pedidosVendedor.length === 0) {{
                    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #999;">Nenhum pedido encontrado para este período.</td></tr>`;
                }} else {{
                    pedidosVendedor.forEach((d, idx) => {{
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><span class="rank-badge">${{idx + 1}}</span></td>
                            <td>${{d.data}}</td>
                            <td>${{d.pedido}}</td>
                            <td>${{d.cliente}}</td>
                            <td>R$ ${{d.valor_total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}
        
        // Função para abrir modal de vendedores com dados de desconto (para Top 10 Filiais - Descontos)
        function openVendedoresDescontoModal(filial) {{
            const modal = document.getElementById('vendedoresModal');
            const title = document.getElementById('vendedoresModalTitle');
            const tbody = document.getElementById('vendedoresModalBody');
            
            // Definir título
            title.innerHTML = '💸 Vendedores (Descontos) - ' + filial;
            
            // Atualizar cabeçalho da tabela
            const tableHead = modal.querySelector('table thead tr');
            if (tableHead) {{
                tableHead.innerHTML = `
                    <th>#</th>
                    <th>Vendedor</th>
                    <th>Total Desconto</th>
                    <th>Pedidos c/ Desc.</th>
                `;
            }}
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Preencher com dados dos vendedores da filial (filtrados por desconto)
            const vendedores = vendedoresPorFilial[filial] || [];
            const vendedoresComDesconto = vendedores.filter(v => v.total_desconto > 0)
                .sort((a, b) => b.total_desconto - a.total_desconto);
            
            if (vendedoresComDesconto.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">Nenhum vendedor com desconto encontrado</td></tr>';
            }} else {{
                vendedoresComDesconto.forEach((v, idx) => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="rank-badge">${{idx + 1}}</span></td>
                        <td>${{v.vendedor}}</td>
                        <td><strong>${{formatMoney(v.total_desconto)}}</strong></td>
                        <td>${{formatNumber(v.qtd_pedidos_desconto)}}</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}
        
        // Função para abrir modal de pedidos por motivo de desconto
        function openMotivoPedidosModal(motivo) {{
            const modal = document.getElementById('vendedorPedidosModal');
            const title = document.getElementById('vendedorPedidosModalTitle');
            const tbody = document.getElementById('vendedorPedidosModalBody');
            const periodoSelecionado = document.getElementById('filtro-mes-header').value;
            
            // Normalizar motivo (pode ser array se label foi quebrada)
            const motivoStr = Array.isArray(motivo) ? motivo.join('') : motivo;
            
            // Definir título
            title.innerHTML = '📊 Pedidos - ' + motivoStr;
            
            // Limpar tabela
            tbody.innerHTML = '';
            
            // Atualizar cabeçalho da tabela
            const tableHead = modal.querySelector('table thead tr');
            if (tableHead) {{
                tableHead.innerHTML = `
                    <th>#</th>
                    <th>Data</th>
                    <th>Pedido</th>
                    <th>Cliente</th>
                    <th>Vendedor</th>
                    <th>Valor Desconto</th>
                    <th>% Desc.</th>
                `;
            }}
            
            // Filtrar descontos pelo motivo (usando motivo_categoria raw para comparar com chart label)
            const pedidosMotivo = todosDescontos.filter(d => {{
                const mesmoPeriodo = periodoSelecionado === 'todos' || d.ano_mes === periodoSelecionado;
                // Comparar com motivo_categoria (raw, sem emojis)
                const mesmoMotivo = d.motivo_categoria && d.motivo_categoria.trim() === motivoStr.trim();
                return mesmoMotivo && mesmoPeriodo;
            }});
            
            if (pedidosMotivo.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #999;">Nenhum pedido encontrado para este motivo/período.</td></tr>`;
            }} else {{
                pedidosMotivo.forEach((d, idx) => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="rank-badge">${{idx + 1}}</span></td>
                        <td>${{d.data}}</td>
                        <td>${{d.pedido}}</td>
                        <td>${{d.cliente}}</td>
                        <td>${{d.vendedor}}</td>
                        <td>R$ ${{d.valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td>${{d.pct.toFixed(2)}}%</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}
            
            // Mostrar modal
            modal.classList.add('active');
        }}
        
        function closeVendedorPedidosModal(event) {{
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('vendedorPedidosModal').classList.remove('active');
        }}
        
        function closeMotivoPedidosModal(event) {{
            closeVendedorPedidosModal(event);
        }}

        // Atualizar listener de ESC
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeFaixasModal();
                closeVendedoresModal();
                closeVendedorPedidosModal();
            }}
        }});

        // Forçar redimensionamento de todos os gráficos ao mudar de tela/monitor
        let resizeTimer = null;
        window.addEventListener('resize', function() {{
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {{
                // Iterar sobre todas as instâncias Chart.js registradas
                const allCharts = Object.values(Chart.instances || {{}});
                allCharts.forEach(function(chart) {{
                    if (chart && chart.canvas) {{
                        chart.resize();
                    }}
                }});
            }}, 250);
        }});
    </script>
    
    <!-- Modal de Vendedores por Filial -->
    <div class="modal-overlay" id="vendedoresModal" onclick="closeVendedoresModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="vendedoresModalTitle">Vendedores da Filial</h3>
                <button class="modal-close" onclick="closeVendedoresModal()">&times;</button>
            </div>
            <div class="modal-body">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Vendedor</th>
                            <th>Faturamento</th>
                            <th>Pedidos</th>
                        </tr>
                    </thead>
                    <tbody id="vendedoresModalBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <!-- Modal de Pedidos do Vendedor -->
    <div class="modal-overlay" id="vendedorPedidosModal" onclick="closeVendedorPedidosModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()" style="width: 1100px;">
            <div class="modal-header">
                <h3 id="vendedorPedidosModalTitle">Pedidos do Vendedor</h3>
                <button class="modal-close" onclick="closeVendedorPedidosModal()">&times;</button>
            </div>
            <div class="modal-body">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Data</th>
                                <th>Pedido</th>
                                <th>Cliente</th>
                                <th>Valor Desconto</th>
                                <th>% Desc.</th>
                                <th>Motivo</th>
                            </tr>
                        </thead>
                        <tbody id="vendedorPedidosModalBody">
                        </tbody>
                    </table>
            </div>
        </div>
    </div>
    </div>

    <script>
        // Bloquear scroll do body quando modal estiver aberto (evita barra dupla)
        const modalObserver = new MutationObserver(function() {{
            const anyModalActive = document.querySelector('.modal-overlay.active');
            document.body.style.overflow = anyModalActive ? 'hidden' : '';
        }});
        document.querySelectorAll('.modal-overlay').forEach(function(modal) {{
            modalObserver.observe(modal, {{ attributes: true, attributeFilter: ['class'] }});
        }});
    </script>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard HTML gerado: {output_path}")
