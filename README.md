# Cooxupé Sales Analytics Dashboard

Dashboard de análise de vendas para visualização de indicadores de desempenho.

## 📁 Estrutura do Projeto

```
├── analytics/          # Código principal da aplicação
│   ├── analysis/       # Módulos de análise (vendas, clientes, produtos, etc.)
│   ├── dashboard/      # Gerador de dashboard HTML
│   ├── data_loader.py  # Carregamento e preparação de dados
│   ├── main.py         # Script principal de análise
│   └── server.py       # Servidor Flask
├── data/               # Arquivos de dados de entrada
├── logs/               # Logs do serviço Windows
├── scripts/            # Scripts de gerenciamento do serviço
└── requirements.txt    # Dependências Python
```

## 🚀 Instalação como Serviço Windows

1. **Execute como Administrador:** `scripts/01_instalar_servico.bat`
2. **Acesse:** http://172.16.253.34:5050

O dashboard iniciará automaticamente com o Windows.

## 🔧 Gerenciamento do Serviço

| Script | Função |
|--------|--------|
| `02_parar_servico.bat` | Para o serviço |
| `03_iniciar_servico.bat` | Inicia o serviço |
| `04_remover_servico.bat` | Remove o serviço |
| `05_reiniciar_servico.bat` | Reinicia o serviço |
| `06_status_servico.bat` | Verifica status |

## 🔄 Atualização de Dados

Para atualizar os dados do dashboard:
1. Substitua o arquivo `data/Pedidos - Completo.csv`
2. Acesse http://172.16.253.34:5050/refresh

## 📊 Análises Disponíveis

- Performance de Vendas
- Análise por Filial
- Curva ABC de Produtos
- Segmentação RFM de Clientes
- Ranking de Vendedores
- Análise de Campanhas
- Análise Temporal
- Indicadores Financeiros
