"""
Documentação técnica completa da aplicação
"""

# Clipper DBF Analytics - Documentação Técnica

## 1. Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│            ARQUITETURA DA APLICAÇÃO                      │
└─────────────────────────────────────────────────────────┘

    DBF FILES (Clipper)
          │
          ▼
    ┌──────────────┐
    │ ETL Module   │  (config/, etl/)
    │ - DBFReader  │  Extrai dados brutos
    │ - Processor  │
    └──────────────┘
          │
          ▼
    ┌──────────────────────────┐
    │   SQLite Database        │  (data/clipper_data.db)
    │   - Armazena dados       │
    │   - Transações seguras   │
    └──────────────────────────┘
          │
          ▼
    ┌──────────────┐
    │  Core Logic  │  (core/)
    │ - Business   │  Processa e calcula
    │   Rules      │
    └──────────────┘
          │
          ▼
    ┌──────────────────────────┐
    │   Dashboard              │  (app_dashboard.py)
    │   - Streamlit Interface  │
    │   - Visualizações        │
    └──────────────────────────┘
```

## 2. Módulos Principais

### 2.1 Configuração (config/)

**Arquivo: `config/settings.py`**

Define todas as constantes e caminhos:
- `DBF_SOURCE_DIR`: Caminho dos arquivos DBF originais
- `DATABASE_PATH`: Caminho do banco SQLite
- `DBF_ENCODING`: Encoding dos arquivos (latin1 por padrão)
- `LOG_DIR`, `LOG_LEVEL`: Configuração de logs

**Uso:**
```python
from config.settings import DBF_SOURCE_DIR, DATABASE_PATH
```

### 2.2 ETL (etl/)

**Classe: `DBFReader`**
- Lê arquivos .DBF usando biblioteca `dbfread`
- Suporta múltiplos encodings
- Validação e tratamento de erros
- Método principal: `ler_arquivo()` → pandas DataFrame

**Classe: `DBFProcessor`**
- Transforma dados (normalização, tipos, limpeza)
- Carrega em SQLite via SQLAlchemy
- Gestão de índices e constraints
- Método principal: `carregar_diretorio()` → estatísticas

**Exemplo:**
```python
from etl.processor import processor

stats = processor.carregar_diretorio(DBF_SOURCE_DIR)
# {'tabelas_processadas': 50, 'registros_carregados': 100000, 'erros': 0}
```

### 2.3 Core (core/)

#### 2.3.1 Database Manager

**Classe: `DatabaseManager`**
- Gerencia conexões SQLite com SQLAlchemy
- Context managers para sessões seguras
- Métodos auxiliares: `get_tables()`, `table_exists()`, `get_table_info()`

**Exemplo:**
```python
from core.database import db_manager

with db_manager.get_session() as session:
    resultado = session.execute("SELECT * FROM ACESSOS")
```

#### 2.3.2 Business Rules

**Classe: `EstoqueCalculator`**

Implementa lógica complexa de cálculo:

1. **`calcular_estoque_real()`**
   - Simula movimentações de entrada/saída
   - Agrupa por produto
   - Retorna estoque calculado

2. **`comparar_estoques()`**
   - Compara sistema vs calculado
   - Calcula divergências e percentuais
   - Identifica produtos problemáticos

3. **`detectar_inconsistencias(limiar_erro)`**
   - Flagging automático de problemas
   - Classificação por criticidade:
     - CRÍTICA: erro > 50% ou diferença > 1000 unidades
     - ALTA: erro > 25% ou diferença > 100
     - MÉDIA: erro > 10% ou diferença > 10
     - BAIXA: resto

4. **`calcular_consumo_por_produto()`**
   - Extrai saídas (movimentos tipo 'S')
   - Agrupa por produto
   - Calcula consumo total, médio e número de saídas

**Lógica de Movimentação:**
```
ENTRADA → soma no estoque
SAÍDA → reduz estoque
TRANSFERÊNCIA → move entre estoques
PRODUÇÃO → consome matéria-prima
```

**Exemplo:**
```python
from core.business_rules import estoque_calc

estoque_calc.carregar_dados()
comparacao = estoque_calc.comparar_estoques()
inconsistencias = estoque_calc.detectar_inconsistencias(limiar_erro=5.0)
consumo = estoque_calc.calcular_consumo_por_produto()
```

### 2.4 Logging (core/logger.py)

**Classe: `Logger`**
- Sistema centralizado de logging
- Output para console + arquivo
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Uso:**
```python
from core.logger import logger

logger.info("Mensagem de informação")
logger.error("Erro crítico")
```

## 3. Scripts Executáveis

### 3.1 ETL Script (`etl_dbf.py`)

**Execução:**
```bash
python etl_dbf.py                    # Carregamento padrão
python etl_dbf.py --clean            # Limpa e recarrega
python etl_dbf.py --source C:/dados  # Fonte customizada
```

**Fluxo:**
1. Validação de diretório
2. Leitura de todos os .DBF
3. Processamento e transformação
4. Carregamento em SQLite
5. Geração de relatório

**Saída:**
```
================================================================================
🔄 ETL - CLIPPER DBF → SQLite
================================================================================

📂 Fonte: \\192.168.0.77\semar26
💾 Banco: data/clipper_data.db

Processando 236 arquivos...
✓ ACESSOS (450 registros)
✓ CADMOV (15000 registros)
...

================================================================================
RESUMO DO CARREGAMENTO
================================================================================
Tabelas processadas: 236
Registros carregados: 1000000
Erros: 0
================================================================================
```

### 3.2 Dashboard (`app_dashboard.py`)

**Execução:**
```bash
streamlit run app_dashboard.py
```

Abre em: `http://localhost:8501`

**Abas:**

1. **📊 Resumo**
   - Métricas principais em cards
   - Quick stats

2. **🔍 Comparação**
   - Tabela comparativa: Sistema vs Calculado
   - Filtros por produto e limiar de erro
   - Gráficos de divergência

3. **⚠️ Inconsistências**
   - Detecção automática com limiar ajustável
   - Tabela com classificação de criticidade
   - Pie chart e scatter plot

4. **📉 Consumo**
   - Top N produtos consumidos
   - Análise consumo médio vs total
   - Tabela detalhada

5. **📋 Dados**
   - Explorador de tabelas
   - Busca e filtros
   - Download em CSV

### 3.3 Setup Script (`run_setup.py`)

**Execução:**
```bash
python run_setup.py
```

Valida:
- Versão Python (3.10+)
- Estrutura do projeto
- Dependências instaladas
- Configuração inicial

### 3.4 CLI Tool (`cli.py`)

**Execução:**
```bash
python cli.py etl                                  # Executar ETL
python cli.py status                              # Ver status
python cli.py analyze --threshold 10              # Analisar
python cli.py export --output ./relatorios        # Exportar
```

### 3.5 Examples (`examples.py`)

**Execução:**
```bash
python examples.py
```

Exemplos interativos de uso programático

## 4. Fluxo de Dados

### 4.1 Leitura de DBF

```
DBF File (.DBF)
    │
    ├─ Magic: 0x83 (validação)
    ├─ Header: nomes de campos
    ├─ Records: dados
    └─ EOF: 0x1A
    
        ▼
    
DBFReader.ler_arquivo()
    ├─ Abrir com dbfread
    ├─ Converter para dicts
    ├─ Criar DataFrame
    └─ Limpar colunas deletadas (*)
    
        ▼
    
pandas.DataFrame
```

### 4.2 Processamento

```
Raw DataFrame
    │
    ├─ Normalizar colunas → UPPERCASE
    ├─ Remover linhas vazias
    ├─ Limpar espaços em branco
    ├─ Converter datas
    ├─ Converter booleanos
    └─ Tratar NULL
    
        ▼
    
Processed DataFrame
    │
    └─ to_sql() → SQLite
```

### 4.3 Cálculo de Estoque

```
Tabela CADMOV (Movimentos)
    │
    ├─ Classificar: ENTRADA / SAÍDA / TRANSFER
    ├─ Agrupar por PRODUTO
    ├─ Somar QUANTIDADE
    └─ Calcular estoque por produto
    
        ▼
    
Estoque Calculado
    │
    ├─ Comparar com ESTOQUE (sistema)
    ├─ Calcular diferença
    ├─ Calcular % erro
    └─ Flagging de inconsistências
    
        ▼
    
Relatórios e Alertas
```

## 5. Estrutura de Dados

### 5.1 Tabela CADMOV (Movimentos)

```
CADMOV
├─ MVID (int)           # ID do movimento
├─ DATA (date)          # Data do movimento
├─ TIPO (char)          # E=Entrada, S=Saída, T=Transferência
├─ PRODUTO (int)        # ID do produto
├─ QUANTIDADE (float)   # Quantidade movimentada
├─ ARMAZEM (int)        # ID do armazém
├─ DESCRICAO (text)     # Descrição
└─ ...outros campos
```

### 5.2 Tabela ESTOQUE (Saldo)

```
ESTOQUE
├─ PRODID (int)         # ID do produto
├─ PRODUTO (text)       # Nome/código
├─ QUANTIDADE (float)   # Quantidade em estoque
├─ MINIMO (float)       # Estoque mínimo
├─ MAXIMO (float)       # Estoque máximo
├─ CUSTOUNITARIO (float)# Custo unitário
└─ ...outros campos
```

## 6. Performance

### 6.1 Otimizações

- **Batch Processing**: Carregamento em chunks
- **SQLite Indexing**: Índices automáticos em chaves primárias
- **Streamlit Caching**: TTL de 5 minutos para dados
- **Connection Pooling**: Reuso de conexões

### 6.2 Limits

- **Max Workers**: 4 (processamento paralelo)
- **Chunk Size**: 5000 registros
- **Query Timeout**: Padrão SQLite

## 7. Tratamento de Erros

### 7.1 Encoding Errors

Se DBF usar encoding diferente:
```python
# Em config/settings.py
DBF_ENCODING = "cp1252"  # Alterar conforme necessário
```

### 7.2 Data Type Mismatch

Conversão automática:
- Texto → VARCHAR
- Número → FLOAT
- Data → TEXT (com parsing)
- Booleano → INTEGER (0/1)

### 7.3 Conexão Falha

Retry automático com timeout

## 8. Segurança

✅ **Read-Only**: Sem modificação de DBFs
✅ **Encoding**: UTF-8 interno
✅ **SQL Injection**: Prepared statements
✅ **Logs**: Auditoria completa

## 9. Troubleshooting

| Problema | Solução |
|----------|---------|
| "Arquivo não encontrado" | Verificar `DBF_SOURCE_DIR` em `config/settings.py` |
| "Encoding error" | Alterar `DBF_ENCODING` |
| "Table not found" | Executar novamente `python etl_dbf.py` |
| "Memory error" | Reduzir `CHUNK_SIZE` |
| "Slow dashboard" | Aumentar `ttl` em cache decorators |

## 10. Próximas Extensões

- [ ] API REST (FastAPI)
- [ ] Webhook para alertas
- [ ] Sincronização programada (APScheduler)
- [ ] Versionamento de snapshots
- [ ] Integração com Excel VBA
- [ ] Notificações por email

---

**Desenvolvido para sistemas Clipper/xBase legados**
**Python 3.10+ | Streamlit | SQLAlchemy | dbfread**
