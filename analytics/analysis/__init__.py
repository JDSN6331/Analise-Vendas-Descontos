"""
Módulos de análise - Cooxupé Sales Analytics
"""

from .sales_performance import analyze_sales_performance, generate_sales_report
from .branch_analysis import analyze_branches, generate_branch_report
from .product_analysis import analyze_products, generate_abc_report
from .customer_analysis import analyze_customers, generate_customer_report
from .seller_analysis import analyze_sellers, generate_seller_report
from .campaign_analysis import analyze_campaigns, generate_campaign_report
from .time_analysis import analyze_time, generate_time_report
from .financial_analysis import analyze_financial, generate_financial_report

__all__ = [
    'analyze_sales_performance', 'generate_sales_report',
    'analyze_branches', 'generate_branch_report',
    'analyze_products', 'generate_abc_report',
    'analyze_customers', 'generate_customer_report',
    'analyze_sellers', 'generate_seller_report',
    'analyze_campaigns', 'generate_campaign_report',
    'analyze_time', 'generate_time_report',
    'analyze_financial', 'generate_financial_report',
]
