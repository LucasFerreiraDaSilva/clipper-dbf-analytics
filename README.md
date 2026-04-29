# Clipper DBF Analytics

Aplicação completa em Python para leitura, processamento e visualização de dados de sistemas legados Clipper/xBase.

## 🎯 Objetivo

Criar uma solução externa que, sem modificar o sistema original Clipper, realiza:

1. **Extração (ETL)**: Leitura de arquivos .DBF
2. **Transformação**: Processamento e cálculo de estoque real
3. **Armazenamento**: Migração para SQLite moderno
4. **Análise**: Dashboard visual com Streamlit

## 📋 Pré-requisitos

- Python 3.10+
- Acesso aos arquivos DBF do sistema Clipper
- Bibliotecas Python (veja `requirements.txt`)

## 🚀 Instalação Rápida

```bash
# 1. Clonar ou baixar o projeto
cd clipper-dbf-analytics

# 2. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar caminho dos DBFs
# Editar: config/settings.py
# Ajustar DBF_SOURCE_DIR para o caminho correto

# 5. Executar ETL
python etl_dbf.py

# 6. Abrir Dashboard
streamlit run app_dashboard.py
```

## 📁 Estrutura do Projeto

```
clipper-dbf-analytics/
├── config/
│   ├── __init__.py
│   └── settings.py           # Configurações globais
├── core/
│   ├── __init__.py
│   ├── database.py           # Gerenciador SQLite
│   ├── business_rules.py     # Lógica de estoque
│   └── logger.py             # Sistema de logs
├── etl/
│   ├── __init__.py
│   ├── dbf_reader.py         # Leitor de DBF
│   └── processor.py          # Processador ETL
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Funções auxiliares
├── data/                     # Banco de dados SQLite
├── logs/                     # Arquivos de log
├── etl_dbf.py               # Script de ETL (executável)
├── app_dashboard.py         # Dashboard Streamlit (executável)
└── requirements.txt         # Dependências Python
```

## 🔧 Configuração

### 1. Configurar Caminho dos DBFs

Editar `config/settings.py`:

```python
# Exemplo: Caminho UNC (rede)
DBF_SOURCE_DIR = r"\\192.168.0.77\semar26"

# Ou caminho local
DBF_SOURCE_DIR = Path("C:/dados/semar26")
```

### 2. Executar ETL

```bash
# Carregamento inicial
python etl_dbf.py

# Com limpeza do banco antes (recarregar)
python etl_dbf.py --clean

# Com diretório customizado
python etl_dbf.py --source "C:/meus_dbfs"
```

## 📊 Dashboard

Abrir interface web:

```bash
streamlit run app_dashboard.py
```

### Abas Disponíveis:

1. **📊 Resumo**: Métricas principais
   - Total de tabelas carregadas
   - Estoque do sistema
   - Estoque calculado
   - Inconsistências detectadas

2. **🔍 Comparação**: Comparação detalhada estoque
   - Tabela com todas as diferenças
   - Gráficos de maiores divergências
   - Distribuição de erros

3. **⚠️ Inconsistências**: Detecção automática
   - Produtos com problemas
   - Classificação por criticidade
   - Scatter plot: Sistema vs Calculado

4. **📉 Consumo**: Análise de movimentação
   - Top produtos consumidos
   - Consumo médio por produto
   - Número de saídas

5. **📋 Dados**: Explorador de tabelas
   - Visualizar dados brutos
   - Busca e filtros
   - Download em CSV

## 🎯 Funcionalidades Principais

### ETL (etl_dbf.py)

✅ **Leitura de DBF**
- Suporte a múltiplos arquivos
- Tratamento de encoding (Latin1)
- Validação de dados

✅ **Transformação**
- Normalização de colunas
- Conversão de tipos
- Limpeza de dados

✅ **Carregamento**
- Migração para SQLite
- Controle transacional
- Recuperação de erros

### Business Rules (core/business_rules.py)

✅ **Cálculo de Estoque Real**
- Entrada de material → soma
- Saída/Faturamento → reduz
- Produção → consome matéria-prima

✅ **Comparação Sistema vs Calculado**
- Identificação de divergências
- Cálculo de percentual de erro
- Análise de consumo

✅ **Detecção de Inconsistências**
- Flagging automático de problemas
- Classificação por criticidade
- Relatórios detalhados

## 📈 Exemplos de Uso

### Analisar Produtos com Maior Erro

```python
from core.business_rules import estoque_calc

# Carregar dados
estoque_calc.carregar_dados()

# Detectar inconsistências
inconsistencias = estoque_calc.detectar_inconsistencias(limiar_erro=5.0)

# Exibir top 10
print(inconsistencias.head(10))
```

### Calcular Consumo por Período

```python
# Calcular consumo
consumo = estoque_calc.calcular_consumo_por_produto()

# Filtrar maiores consumidores
top_10 = consumo.nlargest(10, 'CONSUMO_TOTAL')
print(top_10)
```

### Exportar Relatório

```python
# Obter comparação
comparacao = estoque_calc.comparar_estoques()

# Salvar em CSV
comparacao.to_csv('relatorio_estoque.csv', index=False)
```

## 🔍 Troubleshooting

### Erro: "Diretório não existe"
**Solução**: Verificar caminho em `config/settings.py`

### Erro: "Encoding problem"
**Solução**: Alguns DBFs podem usar CP1252 em vez de Latin1
```python
# Em config/settings.py
DBF_ENCODING = "cp1252"  # Alterar conforme necessário
```

### Erro: "Tabela não encontrada"
**Solução**: Executar novamente `python etl_dbf.py`

### Dashboard lento
**Solução**: Aumentar `ttl` em cache
```python
@st.cache_data(ttl=600)  # Aumentar de 300 para 600 segundos
```

## 📊 Arquivos DBF Reconhecidos

O sistema processa automaticamente:
- ACESSOS
- CADMOV
- ESTOQUE
- MOVIMENT
- CLIENTES
- COMPRAS
- (e muitos outros...)

Veja lista completa em `config/settings.py`

## 🔐 Considerações de Segurança

✅ Sistema somente leitura (não modifica DBFs)
✅ Banco SQLite local (sem exposição)
✅ Encoding seguro (UTF-8 interno)
✅ Logs de auditoria

## 📝 Logs

Todos os eventos são registrados em:
```
logs/clipper_etl.log
```

## 🚀 Próximas Melhorias

- [ ] Suporte a múltiplos bancos SQLite
- [ ] API REST para integração
- [ ] Webhook para notificações automáticas
- [ ] Versionamento de snapshots
- [ ] Sincronização programada
- [ ] Alertas por email

## 📞 Suporte

Para problemas ou sugestões, verifique:
1. Logs em `logs/`
2. Configuração em `config/settings.py`
3. Estrutura do projeto com `utils.validar_estrutura_projeto()`

## 📄 Licença

Este projeto é fornecido como está para uso em sistemas Clipper legados.

## 👨‍💻 Desenvolvido por

Especialista em Sistemas Legados Clipper/xBase e Python

---

**Última atualização**: 2026-04-29
