"""
Análise de Clientes/Cooperados (RFM)
Cooxupé Sales Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime


def analyze_customers(df: pd.DataFrame) -> dict:
    """
    Realiza análise completa de clientes incluindo segmentação RFM.
    
    Returns:
        Dicionário com todas as métricas e tabelas de análise
    """
    results = {}
    
    # Data de referência para cálculo de recência
    data_ref = df['data_pedido'].max()
    
    # === ANÁLISE RFM ===
    rfm = df.groupby(['matricula_cooperado', 'nome_conta']).agg({
        'data_pedido': 'max',  # Recência: última compra
        'num_pedido': 'nunique',  # Frequência: número de pedidos
        'preco_total': 'sum'  # Monetário: valor total
    }).reset_index()
    
    rfm.columns = ['matricula', 'nome', 'ultima_compra', 'frequencia', 'valor_monetario']
    rfm['recencia_dias'] = (data_ref - rfm['ultima_compra']).dt.days
    
    # Função auxiliar para qcut seguro que ajusta o número de quantis dinamicamente
    def safe_qcut(series, q=5, labels=None, duplicates='drop'):
        """Aplica qcut ajustando dinamicamente o número de quantis se necessário."""
        if len(series) == 0:
            return pd.Series([], dtype='category')
        
        # Contar valores únicos
        unique_count = series.nunique()
        
        # Se houver menos valores únicos do que quantis solicitados, ajustar
        if unique_count < q:
            q_adj = max(2, unique_count)  # Mínimo de 2 quantis
        else:
            q_adj = q
        
        # Ajustar labels se necessário
        if labels is not None and isinstance(labels, list):
            if len(labels) != q_adj:
                # Distribuir labels uniformemente pegando índices espaçados
                if q_adj == 1:
                    labels_adj = [labels[len(labels)//2]]
                else:
                    indices = [int(i * (len(labels) - 1) / (q_adj - 1)) for i in range(q_adj)]
                    labels_adj = [labels[i] for i in indices]
            else:
                labels_adj = labels
        else:
            labels_adj = labels
        
        try:
            result = pd.qcut(series, q=q_adj, labels=labels_adj, duplicates=duplicates)
            return result
        except (ValueError, TypeError):
            # Se ainda falhar, usar rank e dividir manualmente
            ranked = series.rank(method='first')
            n = len(ranked)
            if n == 0:
                return pd.Series([], dtype='category')
            
            # Dividir em quantis iguais baseado no rank
            quantiles = []
            for val in ranked:
                quantile_idx = int((val - 1) / n * q_adj)
                quantile_idx = min(quantile_idx, q_adj - 1)
                if labels_adj is not None:
                    quantiles.append(labels_adj[quantile_idx])
                else:
                    quantiles.append(quantile_idx + 1)
            
            return pd.Series(quantiles, index=series.index, dtype='category')
    
    # Scores RFM (1-5)
    rfm['r_score'] = safe_qcut(rfm['recencia_dias'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = safe_qcut(rfm['frequencia'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = safe_qcut(rfm['valor_monetario'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Converter para int (tratando valores NaN ou None)
    rfm['r_score'] = pd.to_numeric(rfm['r_score'], errors='coerce').fillna(3).astype(int)
    rfm['f_score'] = pd.to_numeric(rfm['f_score'], errors='coerce').fillna(3).astype(int)
    rfm['m_score'] = pd.to_numeric(rfm['m_score'], errors='coerce').fillna(3).astype(int)
    
    # Score RFM combinado
    rfm['rfm_score'] = rfm['r_score'] * 100 + rfm['f_score'] * 10 + rfm['m_score']
    rfm['rfm_sum'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']
    
    # Segmentação
    def segmentar_cliente(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 4 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'Recent Customers'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:
            return 'Can\'t Lose Them'
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        else:
            return 'Others'
    
    rfm['segmento'] = rfm.apply(segmentar_cliente, axis=1)
    rfm = rfm.sort_values('valor_monetario', ascending=False).reset_index(drop=True)
    rfm['posicao'] = range(1, len(rfm) + 1)
    
    results['rfm'] = rfm
    
    # === RESUMO POR SEGMENTO ===
    segmento_resumo = rfm.groupby('segmento').agg({
        'matricula': 'count',
        'valor_monetario': 'sum',
        'frequencia': 'mean',
        'recencia_dias': 'mean'
    }).reset_index()
    segmento_resumo.columns = ['segmento', 'qtd_clientes', 'faturamento', 'freq_media', 'recencia_media']
    segmento_resumo = segmento_resumo.sort_values('faturamento', ascending=False)
    segmento_resumo['participacao'] = (segmento_resumo['faturamento'] / segmento_resumo['faturamento'].sum() * 100).round(2)
    results['segmento_resumo'] = segmento_resumo
    
    # === TOP 20 CLIENTES VIP ===
    results['top_20_clientes'] = rfm.head(20)
    
    # === CLIENTES EM RISCO ===
    clientes_risco = rfm[rfm['segmento'].isin(['At Risk', "Can't Lose Them", 'Hibernating'])]
    results['clientes_risco'] = clientes_risco.head(20)
    
    # === ESTATÍSTICAS ===
    results['stats'] = {
        'total_clientes': len(rfm),
        'clientes_ativos_30d': len(rfm[rfm['recencia_dias'] <= 30]),
        'clientes_ativos_90d': len(rfm[rfm['recencia_dias'] <= 90]),
        'clientes_inativos_90d': len(rfm[rfm['recencia_dias'] > 90]),
        'ticket_medio_cliente': rfm['valor_monetario'].mean(),
        'mediana_compras': rfm['frequencia'].median(),
        'champions': len(rfm[rfm['segmento'] == 'Champions']),
        'at_risk': len(rfm[rfm['segmento'] == 'At Risk']),
    }
    
    # === DISTRIBUIÇÃO DE FREQUÊNCIA ===
    freq_dist = rfm['frequencia'].value_counts().sort_index().reset_index()
    freq_dist.columns = ['frequencia', 'qtd_clientes']
    results['distribuicao_frequencia'] = freq_dist
    
    # === EVOLUÇÃO DE NOVOS CLIENTES ===
    primeiro_pedido = df.groupby('matricula_cooperado')['data_pedido'].min().reset_index()
    primeiro_pedido.columns = ['matricula', 'primeiro_pedido']
    primeiro_pedido['ano_mes'] = primeiro_pedido['primeiro_pedido'].dt.to_period('M').astype(str)
    novos_clientes = primeiro_pedido.groupby('ano_mes').size().reset_index(name='novos_clientes')
    results['novos_clientes_mensal'] = novos_clientes
    
    # === SEGMENTAÇÃO COMERCIAL ===
    # Carregar segmentação comercial do arquivo Excel
    try:
        from data_loader import load_classe_cooperado
        df_classe = load_classe_cooperado()
        if df_classe is not None:
            # Garantir que matricula_cooperado seja int para o join
            df_temp = df.copy()
            df_temp['matricula_cooperado'] = pd.to_numeric(df_temp['matricula_cooperado'], errors='coerce').fillna(0).astype(int)
            
            # Agrupar por cooperado e fazer merge com classe comercial
            clientes_comercial = df_temp.groupby('matricula_cooperado').agg({
                'nome_conta': 'first',
                'preco_total': 'sum',
                'num_pedido': 'nunique'
            }).reset_index()
            clientes_comercial.columns = ['matricula', 'nome', 'faturamento', 'qtd_pedidos']
            
            # Merge com classe comercial
            clientes_comercial = clientes_comercial.merge(
                df_classe,
                left_on='matricula',
                right_on='matricula_cooperado',
                how='left'
            )
            clientes_comercial['classe_comercial'] = clientes_comercial['classe_comercial'].fillna('NÃO CLASSIFICADO')
            
            # Resumo por classe comercial
            classe_resumo = clientes_comercial.groupby('classe_comercial').agg({
                'matricula': 'count',
                'faturamento': 'sum',
                'qtd_pedidos': 'sum'
            }).reset_index()
            classe_resumo.columns = ['segmento', 'qtd_clientes', 'faturamento', 'qtd_pedidos']
            classe_resumo = classe_resumo.sort_values('faturamento', ascending=False)
            classe_resumo['participacao'] = (classe_resumo['faturamento'] / classe_resumo['faturamento'].sum() * 100).round(2)
            
            # Usar segmentação comercial em vez de RFM
            results['segmento_resumo'] = classe_resumo
            results['clientes_comercial'] = clientes_comercial
            results['usando_segmentacao_comercial'] = True
        else:
            results['usando_segmentacao_comercial'] = False
    except Exception as e:
        results['usando_segmentacao_comercial'] = False
        results['erro_segmentacao'] = str(e)
    
    return results


def generate_customer_report(results: dict) -> pd.DataFrame:
    """
    Gera relatório de clientes formatado.
    """
    top = results['top_20_clientes'].copy()
    top['valor_fmt'] = top['valor_monetario'].apply(lambda x: f"R$ {x:,.2f}")
    top['ultima_compra_fmt'] = top['ultima_compra'].dt.strftime('%d/%m/%Y')
    
    return top[['posicao', 'matricula', 'nome', 'valor_fmt', 
                'frequencia', 'ultima_compra_fmt', 'segmento']]
