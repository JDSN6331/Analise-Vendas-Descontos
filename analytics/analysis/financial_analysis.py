"""
Análise Financeira
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np
import re


def categorizar_motivo(texto):
    """
    Extrai informações detalhadas do motivo do desconto.
    Retorna um resumo específico e útil para análise de negócios.
    """
    if pd.isna(texto) or str(texto).strip() == '':
        return 'Não informado'
    
    texto_orig = str(texto).strip()
    texto_lower = texto_orig.lower()
    
    # =====================================
    # 1. CONCORRÊNCIA - Extrair qual concorrente
    # =====================================
    concorrentes = {
        'coopercitrus': 'Coopercitrus',
        'coopama': 'Coopama',
        'coocapec': 'Coocapec',
        'cocapec': 'Coocapec',
        'coopercam': 'Coopercam',
        'minasul': 'Minasul',
        'geagro': 'Geagro',
        'futura': 'Futura',
        'sagra': 'Sagra',
        'agropec': 'Agropec',
        'casa do café': 'Casa do Café',
        'campo verde': 'Campo Verde',
        'focco': 'Focco',
        'capebe': 'Capebe',
        'hinova': 'Hinova',
        'ga agroneg': 'GA Agronegocios',
        'inova': 'Inova',
        'protec': 'Protec',
        'robinho': 'Robinho Agrícola',
        'café forte': 'Café Forte',
        'agrofertil': 'Agrofertil',
        'carpec': 'Carpec',
        'fitovet': 'Fitovet'
    }
    
    for termo, nome in concorrentes.items():
        if termo in texto_lower:
            return f'Concorrente: {nome}'
    
    # Concorrência genérica
    if any(p in texto_lower for p in ['concorrên', 'concorren', 'cobrir oferta', 'acompanhar preço', 'preço mercado']):
        return 'Acompanhar Mercado'
    
    # =====================================
    # 2. REVENDA - Extrair nome da revenda
    # =====================================
    revendas = {
        '3 barras': 'Revenda 3 Barras',
        'tres barras': 'Revenda 3 Barras',
        'petúnia': 'Revenda Petúnia',
        'petunia': 'Revenda Petúnia',
        'bom jesus': 'Revenda Bom Jesus',
        'cabo verde': 'Revenda Cabo Verde',
        'juruaia': 'Revenda Juruaia'
    }
    
    for termo, nome in revendas.items():
        if termo in texto_lower:
            return nome
    
    if 'revenda' in texto_lower:
        return 'Revenda'
    
    # =====================================
    # 3. PRODUTO COM PROBLEMA - Especificar
    # =====================================
    if any(p in texto_lower for p in ['vencid', 'vencimento', 'próximo venc']):
        return 'Prod. Vencido/Vencendo'
    if any(p in texto_lower for p in ['danificad', 'avariad', 'quebrad', 'rachad']):
        return 'Prod. Danificado'
    if 'defeito' in texto_lower:
        return 'Prod. com Defeito'
    if any(p in texto_lower for p in ['empedrad', 'molhad', 'pedrado']):
        return 'Prod. Empedrado/Molhado'
    
    # =====================================
    # 4. PAGAMENTO - Especificar prazo
    # =====================================
    if any(p in texto_lower for p in ['a vista', 'à vista', 'avista', 'pix', 'caixa']):
        return 'Pgto. À Vista'
    if 'curto prazo' in texto_lower or '7 dias' in texto_lower:
        return 'Pgto. Curto Prazo'
    
    # =====================================
    # 5. PROMOÇÃO/CAMPANHA - Especificar
    # =====================================
    if 'empório' in texto_lower or 'emporio' in texto_lower:
        return 'Promoção Empório'
    if 'campanha' in texto_lower or 'ação de vendas' in texto_lower:
        return 'Campanha Comercial'
    if 'promoção' in texto_lower or 'promocao' in texto_lower:
        return 'Promoção'
    if 'liquidação' in texto_lower or 'liquidaç' in texto_lower:
        return 'Liquidação Estoque'
    
    # =====================================
    # 6. AUTORIZADO - Extrair nome de quem autorizou
    # =====================================
    # Padrões para extrair nomes após palavras-chave
    padroes_autorizador = [
        r'autorizado\s+(?:por|pelo|pela)?\s*(\w+)',
        r'alinhado\s+(?:com)?\s*(\w+)',
        r'aprovado\s+(?:por|pelo|pela)?\s*(\w+)',
        r'gerente\s+(\w+)',
        r'supervisor\s+(\w+)',
        r'desconto\s+(\w+)$',  # Nome no final: "Desconto Tossani"
        r'aut\.?\s*(\w+)',  # "Aut. Denise"
        r'desc\.?\s+aut\.?\s+ger\.?\s*(\w+)',  # "Desc aut Ger Vandelino"
    ]
    
    # Nomes conhecidos de autorizadores
    nomes_conhecidos = [
        'vandelino', 'inácio', 'inacio', 'paulo', 'rafael', 'denise', 'joaquim',
        'flávio', 'flavio', 'thalles', 'tales', 'marcelo', 'dirceu', 'mauro',
        'ana', 'leiliele', 'bruno', 'simoninho', 'raul', 'lais', 'laís',
        'michelle', 'ademir', 'sergio', 'reginaldo', 'andre', 'andré',
        'tossani', 'eto', 'chiquinho', 'otávio', 'otavio'
    ]
    
    for nome in nomes_conhecidos:
        if nome in texto_lower:
            nome_formatado = nome.capitalize()
            if nome == 'otávio' or nome == 'otavio':
                nome_formatado = 'Paulo Otávio'
            elif nome == 'inácio' or nome == 'inacio':
                nome_formatado = 'Inácio'
            return f'Aut. {nome_formatado}'
    
    if any(p in texto_lower for p in ['autorizado', 'autorização', 'alinhado', 'aprovado']):
        return 'Autorizado (Gerência)'
    
    if 'gerente' in texto_lower or 'supervisor' in texto_lower:
        return 'Autorizado (Gerência)'
    
    if 'comercial' in texto_lower and 'alinhad' in texto_lower:
        return 'Alinhamento Comercial'
    
    # =====================================
    # 7. COOPERADO/NEGOCIAÇÃO
    # =====================================
    if 'cooperado fecha' in texto_lower or 'negociado com cooperado' in texto_lower:
        return 'Negociação Cooperado'
    if 'preferência' in texto_lower or 'fiel' in texto_lower:
        return 'Fidelização Cooperado'
    if 'terceiro' in texto_lower or 'proponente' in texto_lower:
        return 'Terceiro/Proponente'
    
    # =====================================
    # 8. COTAÇÃO ESPECÍFICA
    # =====================================
    if 'cotação específica' in texto_lower or 'cotação especifica' in texto_lower:
        return 'Cotação Específica'
    
    # =====================================
    # 9. FUNCIONÁRIO/COLABORADOR
    # =====================================
    if any(p in texto_lower for p in ['funcionário', 'funcionaria', 'colaborador', 'funcinária']):
        return 'Funcionário'
    
    # =====================================
    # 10. SE NADA ACIMA, MOSTRAR RESUMO DO TEXTO
    # =====================================
    # Retornar primeiras palavras do texto original (até 25 chars)
    resumo = texto_orig[:25].strip()
    if len(texto_orig) > 25:
        resumo = resumo.rsplit(' ', 1)[0] + '...'
    return resumo


def _calcular_desconto_por_grupo(df_base: pd.DataFrame) -> pd.DataFrame:
    """Agrupa descontos por grupo de produto com a lógica do dashboard."""
    if len(df_base) == 0:
        return None

    desconto_por_grupo = df_base.groupby('grupo_produto').agg(
        total_desconto=('valor_desconto_manual', 'sum'),
        qtd_pedidos=('num_pedido', 'nunique'),
        pct_medio=('desconto_manual_pct', 'mean'),
        faturamento=('preco_total', 'sum')
    ).reset_index()

    desconto_por_grupo = desconto_por_grupo.sort_values('total_desconto', ascending=False)
    total_desconto_geral = desconto_por_grupo['total_desconto'].sum()
    desconto_por_grupo['pct_do_total'] = (
        desconto_por_grupo['total_desconto'] / total_desconto_geral * 100
    ).round(2) if total_desconto_geral > 0 else 0

    return desconto_por_grupo


def _resumir_impacto_estoque_critico(df_excluidos: pd.DataFrame, total_desconto_original: float) -> dict:
    """Resume o impacto da exclusão de itens vencidos/a vencer na análise ajustada."""
    impacto = {
        'itens_excluidos': 0,
        'pedidos_excluidos': 0,
        'grupos_impactados': 0,
        'total_desconto_excluido': 0.0,
        'pct_desconto_excluido': 0.0,
        'vencido': 0,
        'vence_30': 0,
        'vence_60': 0,
    }

    if len(df_excluidos) == 0:
        return impacto

    contagem_status = df_excluidos['status_validade'].value_counts().to_dict()
    total_desconto_excluido = float(df_excluidos['valor_desconto_manual'].sum())

    impacto.update({
        'itens_excluidos': int(len(df_excluidos)),
        'pedidos_excluidos': int(df_excluidos['num_pedido'].nunique()),
        'grupos_impactados': int(df_excluidos['grupo_produto'].nunique()),
        'total_desconto_excluido': total_desconto_excluido,
        'pct_desconto_excluido': (
            total_desconto_excluido / total_desconto_original * 100
        ) if total_desconto_original > 0 else 0.0,
        'vencido': int(contagem_status.get('vencido', 0)),
        'vence_30': int(contagem_status.get('vence_30', 0)),
        'vence_60': int(contagem_status.get('vence_60', 0)),
    })

    return impacto



def analyze_financial(df: pd.DataFrame) -> dict:
    """
    Realiza análise financeira detalhada.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # === PREPARAÇÃO DE DADOS PEDIDOS ÚNICOS (para Descontos) ===
    # Agrupar por pedido:
    # - SOMAR valores de desconto de cada linha
    # - MAX do % de desconto (alçada é definida pelo MAIOR % de desconto entre as linhas)
    df_pedidos = df.groupby('num_pedido').agg({
        'valor_desconto_manual': 'sum',  # SOMA de todos os descontos das linhas do pedido
        'preco_total': 'sum',  # Valor líquido total do pedido (soma das linhas)
        'valor_pedido': 'first',  # Valor do pedido (referência)
        'tem_desconto': 'max',
        'data_pedido': 'first',
        'nome_conta': 'first',
        'filial_nome': 'first',
        'vendedor_01': 'first',
        'desconto_manual_pct': 'max',  # MAX % de desconto (para definir alçada)
        'motivo_desconto': 'first'  # Primeiro motivo do pedido
    }).reset_index()
    
    # Renomear a coluna de % para clareza
    df_pedidos = df_pedidos.rename(columns={'desconto_manual_pct': 'max_desconto_pct'})
    
    # Total de descontos (soma dos PEDIDOS com desconto líquido positivo - para bater com a tabela)
    # Agrupa por pedido para obter o desconto líquido
    pedidos_net_desconto = df.groupby('num_pedido')['valor_desconto_manual'].sum()
    # Soma apenas os pedidos que no final tiveram desconto positivo
    total_desconto = pedidos_net_desconto[pedidos_net_desconto > 0].sum()
    total_faturamento_liquido = df['preco_total'].sum()  # Soma das linhas (correto)
    total_faturamento_bruto = total_faturamento_liquido + total_desconto
    
    # Pedidos com desconto (pelo menos 1 linha com desconto = pedido com desconto)
    df_com_desconto = df_pedidos[df_pedidos['valor_desconto_manual'] > 0]
    
    desconto_stats = {
        'total_desconto': total_desconto,
        'faturamento_bruto': total_faturamento_bruto,
        'faturamento_liquido': total_faturamento_liquido,
        'pct_desconto_total': (total_desconto / total_faturamento_liquido * 100) if total_faturamento_liquido > 0 else 0,
        'pedidos_com_desconto': len(df_com_desconto),  # Pedidos ÚNICOS
        'pedidos_sem_desconto': len(df_pedidos) - len(df_com_desconto),
        'pct_pedidos_com_desconto': (len(df_com_desconto) / len(df_pedidos) * 100) if len(df_pedidos) > 0 else 0,
        'desconto_medio': df_com_desconto['valor_desconto_manual'].mean() if len(df_com_desconto) > 0 else 0,
        'desconto_mediano': df_com_desconto['valor_desconto_manual'].median() if len(df_com_desconto) > 0 else 0,
        'maior_desconto': df_com_desconto['valor_desconto_manual'].max() if len(df_com_desconto) > 0 else 0,
    }
    results['desconto_stats'] = desconto_stats
    
    # === DESCONTOS POR PERÍODO ===
    # Calcular desconto por período (usando pedidos únicos)
    df_pedidos['ano_mes'] = df_pedidos['data_pedido'].dt.to_period('M').astype(str)
    desconto_mensal = df_pedidos.groupby('ano_mes').agg({
        'valor_desconto_manual': 'sum',
        'num_pedido': lambda x: (df_pedidos.loc[x.index, 'valor_desconto_manual'] > 0).sum()
    }).reset_index()
    
    # Faturamento por período (usando linhas)
    fat_mensal = df.groupby('ano_mes').agg({'preco_total': 'sum'}).reset_index()
    
    # Total de pedidos por período (para KPI dinâmico)
    pedidos_mensal = df_pedidos.groupby('ano_mes')['num_pedido'].count().reset_index()
    pedidos_mensal.columns = ['ano_mes', 'total_pedidos_periodo']
    
    desconto_mensal = pd.merge(desconto_mensal, fat_mensal, on='ano_mes')
    desconto_mensal = pd.merge(desconto_mensal, pedidos_mensal, on='ano_mes')
    
    desconto_mensal.columns = ['periodo', 'total_desconto', 'pedidos_com_desconto', 'faturamento', 'total_pedidos']
    desconto_mensal['pct_desconto'] = (desconto_mensal['total_desconto'] / 
                                        (desconto_mensal['faturamento'] + desconto_mensal['total_desconto']) * 100).round(2)
    desconto_mensal['pct_pedidos_com_desconto'] = (desconto_mensal['pedidos_com_desconto'] / desconto_mensal['total_pedidos'] * 100).round(2)
    
    results['desconto_mensal'] = desconto_mensal
    
    # === DESCONTOS POR FILIAL ===
    desconto_filial = df_pedidos.groupby('filial_nome').agg({
        'valor_desconto_manual': 'sum'
    }).reset_index()
    
    fat_filial = df.groupby('filial_nome').agg({'preco_total': 'sum'}).reset_index()
    
    desconto_filial = pd.merge(desconto_filial, fat_filial, on='filial_nome')
    desconto_filial.columns = ['filial', 'total_desconto', 'faturamento']
    desconto_filial['pct_desconto'] = (desconto_filial['total_desconto'] / 
                                        (desconto_filial['faturamento'] + desconto_filial['total_desconto']) * 100).round(2)
    desconto_filial = desconto_filial.sort_values('total_desconto', ascending=False)
    results['desconto_por_filial'] = desconto_filial
    
    # === DESCONTOS POR VENDEDOR ===
    desconto_vendedor = df_pedidos.groupby('vendedor_01').agg({
        'valor_desconto_manual': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    
    fat_vendedor = df.groupby('vendedor_01').agg({'preco_total': 'sum'}).reset_index()
    
    desconto_vendedor = pd.merge(desconto_vendedor, fat_vendedor, on='vendedor_01')
    desconto_vendedor.columns = ['vendedor', 'total_desconto', 'qtd_pedidos', 'faturamento']
    desconto_vendedor['pct_desconto'] = (desconto_vendedor['total_desconto'] / 
                                          (desconto_vendedor['faturamento'] + desconto_vendedor['total_desconto']) * 100).round(2)
    desconto_vendedor = desconto_vendedor.sort_values('total_desconto', ascending=False).head(20)
    results['desconto_por_vendedor'] = desconto_vendedor
    
    # === ANÁLISE POR CATEGORIA DE CRÉDITO ===
    # Faturamento por categoria (linhas)
    credito_fat = df.groupby('cat_limite_credito').agg({
        'preco_total': 'sum',
        'num_pedido': 'nunique',
        'matricula_cooperado': 'nunique'
    }).reset_index()
    
    # Desconto por categoria (precisamos vincular categoria ao pedido unico)
    # Assumindo que categoria é por pedido (vem do cliente/pedido)
    # Precisamos pegar a categoria de cada pedido
    pedido_cat = df.groupby('num_pedido')['cat_limite_credito'].first().reset_index()
    pedido_cat = pd.merge(pedido_cat, df_pedidos[['num_pedido', 'valor_desconto_manual']], on='num_pedido')
    
    credito_desc = pedido_cat.groupby('cat_limite_credito')['valor_desconto_manual'].sum().reset_index()
    
    credito_analysis = pd.merge(credito_fat, credito_desc, on='cat_limite_credito', how='left').fillna(0)
    credito_analysis.columns = ['categoria', 'faturamento', 'qtd_pedidos', 'qtd_clientes', 'total_desconto']
    
    credito_analysis['ticket_medio'] = (credito_analysis['faturamento'] / credito_analysis['qtd_pedidos']).round(2)
    credito_analysis['pct_desconto'] = (credito_analysis['total_desconto'] / 
                                         (credito_analysis['faturamento'] + credito_analysis['total_desconto']) * 100).round(2)
    credito_analysis = credito_analysis.sort_values('faturamento', ascending=False)
    results['analise_credito'] = credito_analysis
    
    # === FAIXAS DE VALOR DE PEDIDO ===
    # Usar df_pedidos pois faixa é sobre valor do pedido
    df_pedidos['faixa_valor'] = pd.cut(df_pedidos['valor_pedido'], 
                                bins=[0, 100, 500, 1000, 5000, 10000, 50000, float('inf')],
                                labels=['Até R$100', 'R$100-500', 'R$500-1K', 'R$1K-5K', 
                                       'R$5K-10K', 'R$10K-50K', 'Acima de R$50K'])
    
    # Faturamento das faixas deve ser a soma dos Pedidos dessa faixa (não das linhas) 
    # ou soma das linhas dos pedidos dessa faixa.
    # Se usarmos valor_pedido (que é o total), podemos somar direto do df_pedidos para ter o faturamento liquido
    
    faixa_analysis = df_pedidos.groupby('faixa_valor', observed=True).agg({
        'valor_pedido': 'sum',
        'num_pedido': 'count'
    }).reset_index()
    
    # Contar clientes
    clientes_faixa = df.groupby('num_pedido').agg({'valor_pedido': 'first', 'matricula_cooperado': 'first'}).reset_index()
    clientes_faixa['faixa_valor'] = pd.cut(clientes_faixa['valor_pedido'], 
                                bins=[0, 100, 500, 1000, 5000, 10000, 50000, float('inf')],
                                labels=['Até R$100', 'R$100-500', 'R$500-1K', 'R$1K-5K', 
                                       'R$5K-10K', 'R$10K-50K', 'Acima de R$50K'])
    clientes_por_faixa = clientes_faixa.groupby('faixa_valor', observed=True)['matricula_cooperado'].nunique().reset_index()
    
    faixa_analysis = pd.merge(faixa_analysis, clientes_por_faixa, on='faixa_valor')
    faixa_analysis.columns = ['faixa', 'faturamento', 'qtd_transacoes', 'qtd_clientes']
    faixa_analysis['participacao'] = (faixa_analysis['faturamento'] / faixa_analysis['faturamento'].sum() * 100).round(2)
    results['faixas_valor'] = faixa_analysis
    
    # === TODOS OS PEDIDOS COM DESCONTO ===
    # Aplicar categorização aos motivos
    df_com_desconto = df_com_desconto.copy()
    df_com_desconto['motivo_categoria'] = df_com_desconto['motivo_desconto'].apply(categorizar_motivo)
    df_com_desconto['ano_mes'] = df_com_desconto['data_pedido'].dt.to_period('M').astype(str)
    
    # Retornar TODOS os descontos, ordenados por data (mais recente primeiro)
    todos_descontos = df_com_desconto.sort_values('data_pedido', ascending=False)[
        ['data_pedido', 'num_pedido', 'nome_conta', 'filial_nome', 'vendedor_01', 
         'valor_pedido', 'valor_desconto_manual', 'max_desconto_pct', 'motivo_categoria', 'motivo_desconto', 'ano_mes']
    ].copy()
    results['top_descontos'] = todos_descontos
    
    # Lista de períodos disponíveis (para o filtro mensal)
    periodos_disponiveis = sorted(todos_descontos['ano_mes'].unique().tolist(), reverse=True)
    results['periodos_descontos'] = periodos_disponiveis
    
    # === TOP 5 MOTIVOS DE DESCONTO ===
    # Agrupar por categoria de motivo
    motivos_agrupados = df_com_desconto.groupby('motivo_categoria').agg({
        'valor_desconto_manual': 'sum',
        'num_pedido': 'nunique'
    }).reset_index()
    motivos_agrupados.columns = ['motivo', 'valor_total', 'qtd_pedidos']
    motivos_agrupados = motivos_agrupados.sort_values('valor_total', ascending=False).head(5)
    results['top_motivos_desconto'] = motivos_agrupados
    
    # === ANÁLISE POR ALÇADA DE DESCONTO ===
    # Regras de alçada (baseado no % de desconto do PEDIDO, não da linha):
    # - Até 0,50%: Alçada Vendedor
    # - De 0,51% até 3,00%: Alçada Gerente
    # - Acima de 3,00%: Alçada Comercial
    
    def classificar_alcada_pct(pct):
        """Classifica alçada baseado apenas no percentual (para agregações)."""
        if pct <= 0.5:
            return 'Vendedor (≤0,5%)'
        elif pct <= 3.0:
            return 'Gerente (0,51-3%)'
        else:
            return 'Comercial (>3%)'
    
    def classificar_alcada(row):
        """Classifica alçada de pedido baseado no valor de desconto e percentual."""
        # Se não tem valor de desconto, é Sem Desconto
        if row['valor_desconto_manual'] <= 0:
            return 'Sem Desconto'
        # Se tem valor mas % é 0 ou muito baixo, considera como Vendedor
        elif row['max_desconto_pct'] <= 0.5:
            return 'Vendedor (≤0,5%)'
        elif row['max_desconto_pct'] <= 3.0:
            return 'Gerente (0,51-3%)'
        else:
            return 'Comercial (>3%)'
    
    # Classificar PEDIDOS por alçada (baseado no MAIOR % de desconto e valor de desconto)
    df_pedidos['alcada'] = df_pedidos.apply(classificar_alcada, axis=1)
    
    # Agregação por alçada usando PEDIDOS ÚNICOS
    alcada_analysis = df_pedidos.groupby('alcada').agg({
        'num_pedido': 'count',  # Conta pedidos únicos
        'valor_desconto_manual': 'sum',  # Soma valores de desconto
        'preco_total': 'sum'
    }).reset_index()
    alcada_analysis.columns = ['alcada', 'qtd_pedidos', 'total_desconto', 'valor_pedidos']
    
    # Ordenar na ordem lógica
    ordem_alcada = ['Sem Desconto', 'Vendedor (≤0,5%)', 'Gerente (0,51-3%)', 'Comercial (>3%)']
    alcada_analysis['ordem'] = alcada_analysis['alcada'].apply(lambda x: ordem_alcada.index(x) if x in ordem_alcada else 99)
    alcada_analysis = alcada_analysis.sort_values('ordem').drop('ordem', axis=1)
    
    # Calcular percentuais
    total_pedidos_all = alcada_analysis['qtd_pedidos'].sum()
    alcada_analysis['pct_pedidos'] = (alcada_analysis['qtd_pedidos'] / total_pedidos_all * 100).round(2)
    alcada_analysis['pct_desconto'] = (alcada_analysis['total_desconto'] / alcada_analysis['total_desconto'].sum() * 100).round(2)
    
    results['alcada_analysis'] = alcada_analysis
    
    # Filtrar apenas pedidos COM desconto para análises detalhadas
    alcada_com_desconto = alcada_analysis[alcada_analysis['alcada'] != 'Sem Desconto'].copy()
    results['alcada_com_desconto'] = alcada_com_desconto
    
    # Linhas com desconto
    df_linhas_com_desconto = df[df['valor_desconto_manual'] > 0]
    
    # Top vendedores por desconto concedido
    # Contar PEDIDOS ÚNICOS e somar VALORES
    vendedor_alcada = df_linhas_com_desconto.groupby('vendedor_01').agg(
        qtd_pedidos=('num_pedido', 'nunique'),  # Pedidos únicos
        total_desconto=('valor_desconto_manual', 'sum'),  # Soma de valores
        pct_medio=('desconto_manual_pct', 'mean')  # % médio
    ).reset_index()
    vendedor_alcada.columns = ['vendedor', 'qtd_pedidos', 'total_desconto', 'pct_medio']
    vendedor_alcada['alcada_predominante'] = vendedor_alcada['pct_medio'].apply(classificar_alcada_pct)
    vendedor_alcada = vendedor_alcada.sort_values('total_desconto', ascending=False).head(10)
    results['vendedor_alcada'] = vendedor_alcada
    
    # Descontos por filial
    filial_alcada = df_linhas_com_desconto.groupby('filial_nome').agg(
        qtd_pedidos=('num_pedido', 'nunique'),  # Pedidos únicos
        total_desconto=('valor_desconto_manual', 'sum'),
        pct_medio=('desconto_manual_pct', 'mean')
    ).reset_index()
    filial_alcada.columns = ['filial', 'qtd_pedidos', 'total_desconto', 'pct_medio']
    filial_alcada['alcada_predominante'] = filial_alcada['pct_medio'].apply(classificar_alcada_pct)
    filial_alcada = filial_alcada.sort_values('total_desconto', ascending=False)
    results['filial_alcada'] = filial_alcada
    
    # Evolução mensal de descontos por alçada
    df_pedidos['mes'] = df_pedidos['data_pedido'].dt.to_period('M').astype(str)
    desconto_mensal_alcada = df_pedidos[df_pedidos['valor_desconto_manual'] > 0].groupby(['mes', 'alcada']).agg({
        'valor_desconto_manual': 'sum',
        'num_pedido': 'count'
    }).reset_index()
    desconto_mensal_alcada.columns = ['mes', 'alcada', 'total_desconto', 'qtd_pedidos']
    results['desconto_mensal_alcada'] = desconto_mensal_alcada
    
    # === ANÁLISE DETALHADA POR ALÇADA ===
    # % Médio de Desconto por Alçada (usando PEDIDOS)
    df_pedidos_com_desconto = df_pedidos[df_pedidos['valor_desconto_manual'] > 0]
    
    alcada_detalhada = df_pedidos_com_desconto.groupby('alcada').agg({
        'max_desconto_pct': 'mean',
        'num_pedido': 'count',  # Pedidos únicos
        'preco_total': 'sum',  # Faturamento
        'valor_desconto_manual': 'sum'  # Total Desconto
    }).reset_index()
    alcada_detalhada.columns = ['alcada', 'pct_medio', 'qtd_pedidos', 'faturamento', 'total_desconto']
    
    # Ordenar na ordem lógica
    ordem_alcada_det = ['Vendedor (≤0,5%)', 'Gerente (0,51-3%)', 'Comercial (>3%)']
    alcada_detalhada['ordem'] = alcada_detalhada['alcada'].apply(lambda x: ordem_alcada_det.index(x) if x in ordem_alcada_det else 99)
    alcada_detalhada = alcada_detalhada.sort_values('ordem').drop('ordem', axis=1)
    results['alcada_detalhada'] = alcada_detalhada
    
    # % Médio de Desconto Geral (considerando apenas pedidos com desconto)
    pct_medio_geral = df_pedidos_com_desconto['max_desconto_pct'].mean() if len(df_pedidos_com_desconto) > 0 else 0
    results['pct_medio_geral'] = pct_medio_geral
    
    # Loja que mais solicita desconto por alçada (pedidos únicos)
    loja_top_por_alcada = {}
    for alcada in ['Vendedor (≤0,5%)', 'Gerente (0,51-3%)', 'Comercial (>3%)']:
        df_alcada = df_pedidos_com_desconto[df_pedidos_com_desconto['alcada'] == alcada]
        if len(df_alcada) > 0:
            loja_counts = df_alcada.groupby('filial_nome')['num_pedido'].count().reset_index()
            loja_counts.columns = ['filial', 'qtd_pedidos']
            top_loja = loja_counts.sort_values('qtd_pedidos', ascending=False).iloc[0]
            loja_top_por_alcada[alcada] = {
                'filial': top_loja['filial'],
                'qtd_pedidos': int(top_loja['qtd_pedidos'])
            }
    results['loja_top_por_alcada'] = loja_top_por_alcada
    
    # === FAIXAS DE DESCONTO POR ALÇADA (para modal) ===
    # Definir faixas de desconto em intervalos de 1%
    def get_faixa_desconto(pct):
        if pct <= 0.5:
            return 'Até 0,50%'
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
    
    # Aplicar faixa de desconto
    df_pedidos_com_desconto = df_pedidos_com_desconto.copy()
    df_pedidos_com_desconto['faixa_desconto'] = df_pedidos_com_desconto['max_desconto_pct'].apply(get_faixa_desconto)
    
    # Gerar dados de faixas por alçada
    faixas_por_alcada = {}
    for alcada in ['Vendedor (≤0,5%)', 'Gerente (0,51-3%)', 'Comercial (>3%)']:

        df_alcada = df_pedidos_com_desconto[df_pedidos_com_desconto['alcada'] == alcada]
        if len(df_alcada) > 0:
            faixas = df_alcada.groupby('faixa_desconto').agg({
                'preco_total': 'sum',  # Faturamento
                'num_pedido': 'count',  # Qtd pedidos
                'valor_desconto_manual': 'sum'  # Total Desconto
            }).reset_index()
            faixas.columns = ['faixa', 'faturamento', 'qtd_pedidos', 'total_desconto']
            
            # Ordenar faixas logicamente
            ordem_faixas = [
                'Até 0,50%', '0,51% a 1,00%', '1,01% a 2,00%', '2,01% a 3,00%',
                '3,01% a 4,00%', '4,01% a 5,00%', '5,01% a 6,00%', '6,01% a 7,00%',
                '7,01% a 8,00%', '8,01% a 9,00%', '9,01% a 10,00%', 'Acima de 10%'
            ]
            faixas['ordem'] = faixas['faixa'].apply(lambda x: ordem_faixas.index(x) if x in ordem_faixas else 99)
            faixas = faixas.sort_values('ordem').drop('ordem', axis=1)
            
            faixas_por_alcada[alcada] = faixas.to_dict('records')
    
    results['faixas_por_alcada'] = faixas_por_alcada
    
    # === DESCONTOS POR GRUPO DE PRODUTOS ===
    try:
        try:
            from data_loader import load_grupo_produtos, load_estoque_critico
        except ImportError:
            from analytics.data_loader import load_grupo_produtos, load_estoque_critico
        df_grupo = load_grupo_produtos()
        df_estoque_critico = load_estoque_critico()
        
        if df_grupo is not None:
            # Garantir que cod_produto é numérico em ambos os DataFrames
            df_temp = df.copy()
            df_temp['cod_produto'] = pd.to_numeric(df_temp['cod_produto'], errors='coerce').fillna(0).astype(int)
            
            # Merge: associar cada ITEM (linha) ao seu grupo de produto
            df_com_grupo = pd.merge(df_temp, df_grupo, on='cod_produto', how='left')
            df_com_grupo['grupo_produto'] = df_com_grupo['grupo_produto'].fillna('Não Classificado')
            
            # Filtrar apenas itens com desconto > 0
            df_itens_com_desconto = df_com_grupo[df_com_grupo['valor_desconto_manual'] > 0]
            
            if len(df_itens_com_desconto) > 0:
                df_itens_com_desconto = df_itens_com_desconto.copy()

                if df_estoque_critico is not None and len(df_estoque_critico) > 0:
                    df_estoque_match = df_estoque_critico[
                        ['cod_produto', 'filial_codigo', 'status_validade', 'dias_janela']
                    ].drop_duplicates().rename(columns={
                        'status_validade': 'status_validade_estoque',
                        'dias_janela': 'dias_janela_estoque'
                    })
                    df_itens_com_desconto = pd.merge(
                        df_itens_com_desconto,
                        df_estoque_match,
                        on=['cod_produto', 'filial_codigo'],
                        how='left'
                    )
                    df_itens_com_desconto['estoque_critico'] = df_itens_com_desconto['status_validade_estoque'].notna()
                    df_itens_com_desconto['status_validade'] = df_itens_com_desconto['status_validade_estoque'].fillna('')
                    df_itens_com_desconto['dias_janela'] = df_itens_com_desconto['dias_janela_estoque'].fillna(0).astype(int)
                    df_itens_com_desconto = df_itens_com_desconto.drop(
                        columns=['status_validade_estoque', 'dias_janela_estoque']
                    )
                else:
                    df_itens_com_desconto['estoque_critico'] = False
                    df_itens_com_desconto['status_validade'] = ''
                    df_itens_com_desconto['dias_janela'] = 0

                df_excluidos = df_itens_com_desconto[df_itens_com_desconto['estoque_critico']].copy()
                df_ajustado = df_itens_com_desconto[~df_itens_com_desconto['estoque_critico']].copy()

                desconto_por_grupo = _calcular_desconto_por_grupo(df_itens_com_desconto)
                desconto_por_grupo_ajustado = _calcular_desconto_por_grupo(df_ajustado)
                total_desconto_original = float(df_itens_com_desconto['valor_desconto_manual'].sum())
                impacto_estoque_critico = _resumir_impacto_estoque_critico(df_excluidos, total_desconto_original)
                impacto_estoque_critico['total_desconto_original'] = total_desconto_original
                impacto_estoque_critico['total_desconto_ajustado'] = float(df_ajustado['valor_desconto_manual'].sum())

                results['desconto_por_grupo'] = desconto_por_grupo
                results['desconto_por_grupo_ajustado'] = desconto_por_grupo_ajustado
                results['desconto_por_grupo_impacto'] = impacto_estoque_critico
            else:
                results['desconto_por_grupo'] = None
                results['desconto_por_grupo_ajustado'] = None
                results['desconto_por_grupo_impacto'] = None
        else:
            results['desconto_por_grupo'] = None
            results['desconto_por_grupo_ajustado'] = None
            results['desconto_por_grupo_impacto'] = None
    except Exception as e:
        print(f"⚠️ Erro ao analisar descontos por grupo de produtos: {e}")
        results['desconto_por_grupo'] = None
        results['desconto_por_grupo_ajustado'] = None
        results['desconto_por_grupo_impacto'] = None
    
    return results


def generate_financial_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório financeiro formatado.
    """
    stats = results['desconto_stats']
    
    report_data = [
        ['Faturamento Bruto', f"R$ {stats['faturamento_bruto']:,.2f}"],
        ['Total de Descontos', f"R$ {stats['total_desconto']:,.2f}"],
        ['Faturamento Líquido', f"R$ {stats['faturamento_liquido']:,.2f}"],
        ['% Desconto sobre Bruto', f"{stats['pct_desconto_total']:.2f}%"],
        ['Pedidos com Desconto', f"{stats['pedidos_com_desconto']:,}"],
        ['% Pedidos com Desconto', f"{stats['pct_pedidos_com_desconto']:.1f}%"],
        ['Desconto Médio', f"R$ {stats['desconto_medio']:,.2f}"],
        ['Maior Desconto', f"R$ {stats['maior_desconto']:,.2f}"],
    ]
    
    return pd.DataFrame(report_data, columns=['Métrica', 'Valor'])
