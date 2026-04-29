"""
Guia Rápido de Uso
Quick Start Guide
"""

# 🚀 GUIA RÁPIDO - CLIPPER DBF ANALYTICS

## 1️⃣ INSTALAÇÃO (5 minutos)

### Passo 1: Preparar Ambiente

```bash
# Clone ou baixe o projeto
cd clipper-dbf-analytics

# Crie ambiente virtual
python -m venv venv

# Ative
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Configurar Caminho dos DBFs

Edite `config/settings.py`:

```python
# ANTES (padrão):
DBF_SOURCE_DIR = r"\\192.168.0.77\semar26"

# DEPOIS (seu caminho):
DBF_SOURCE_DIR = r"\\192.168.X.X\sua_pasta"
# ou
DBF_SOURCE_DIR = Path("C:/dados/semar26")
```

## 2️⃣ PRIMEIRO USO

### Passo 1: Verificar Setup

```bash
python run_setup.py
```

Deve exibir ✅ em todos os itens

### Passo 2: Executar ETL

```bash
python etl_dbf.py
```

Aguarde conclusão. Verá relatório como:

```
================================================================================
RESUMO DO CARREGAMENTO
================================================================================
Tabelas processadas: 236
Registros carregados: 1000000
Erros: 0
================================================================================
```

### Passo 3: Abrir Dashboard

```bash
streamlit run app_dashboard.py
```

Abrirá em `http://localhost:8501`

## 3️⃣ USANDO O DASHBOARD

### Aba: Resumo

- **Total de tabelas**: Quantos arquivos foram carregados
- **Estoque Sistema**: Total de itens no sistema Clipper
- **Estoque Calculado**: Total calculado a partir de movimentos
- **Inconsistências**: Quantos produtos têm problemas

### Aba: Comparação

```
Filtrar por:
├─ Produto: busca textual
├─ Erro Mínimo: ex 5%
└─ Erro Máximo: ex 50%

Visualizar:
├─ Tabela com diferenças
├─ Gráfico de maiores divergências
└─ Histograma de erros
```

### Aba: Inconsistências

```
Ajustar:
└─ Limiar de Erro: ex 5% significa alertar 
                   se |erro| > 5%

Ver:
├─ Distribuição por criticidade
├─ Tabela com produtos problemáticos
└─ Scatter plot comparativo
```

### Aba: Consumo

```
Filtrar:
└─ Top N produtos (default 15)

Visualizar:
├─ Produtos mais consumidos
├─ Consumo total vs médio
└─ Relação com número de saídas
```

### Aba: Dados

```
Explorar:
├─ Selecionar uma tabela
├─ Buscar texto
├─ Limitar linhas
└─ Download em CSV
```

## 4️⃣ LINHA DE COMANDO

### Opção 1: CLI Tool (Recomendado)

```bash
# Executar ETL
python cli.py etl

# Ver status
python cli.py status

# Analisar estoques
python cli.py analyze --threshold 10

# Exportar dados
python cli.py export --output ./relatorios
```

### Opção 2: Scripts Individuais

```bash
# Só ETL
python etl_dbf.py

# Só Dashboard
streamlit run app_dashboard.py

# Exemplos
python examples.py
```

## 5️⃣ PROGRAMATICAMENTE

### Exemplo 1: Comparação Simples

```python
from core.business_rules import estoque_calc

# Carregar dados
estoque_calc.carregar_dados()

# Obter comparação
comparacao = estoque_calc.comparar_estoques()

# Ver top 10 maiores diferenças
top_10 = comparacao.nlargest(10, 'DIFERENCA')
print(top_10[['PRODUTO', 'QUANTIDADE_SISTEMA', 
              'QUANTIDADE_CALC', 'DIFERENCA']])
```

### Exemplo 2: Detectar Problemas

```python
# Produtos com erro > 10%
problematicos = estoque_calc.detectar_inconsistencias(limiar_erro=10.0)

# Ver por criticidade
print(problematicos['CRITICIDADE'].value_counts())

# Salvar em CSV
problematicos.to_csv('problemas.csv', index=False)
```

### Exemplo 3: Analisar Consumo

```python
# Consumo por produto
consumo = estoque_calc.calcular_consumo_por_produto()

# Produtos mais consumidos
top_consumo = consumo.nlargest(20, 'CONSUMO_TOTAL')

print(top_consumo[['PRODUTO', 'CONSUMO_TOTAL', 
                   'NUM_SAIDAS', 'CONSUMO_MEDIO']])
```

## 6️⃣ INTERPRETANDO RESULTADOS

### Caso 1: Produto com "Diferença = 100"

```
Sistema:    500 unidades
Calculado:  400 unidades
Diferença:  -100 (falta 100)
Erro:       -20%

Interpretação: Sistema diz que tem 500, mas os movimentos 
              indicam que deveria ter 400. Faltam 100 unidades.

Possíveis causas:
├─ Movimentos não registrados
├─ Saída sem documentação
├─ Danificação/Perda
└─ Erro de entrada inicial
```

### Caso 2: Criticidade "CRÍTICA"

```
Produto: XYZ
Diferença: 5000 unidades
Erro: 150%

Interpretação: Problema muito sério!
              Sistema pode estar com erro de entrada 
              ou múltiplos movimentos não foram registrados

Ação: Auditoria imediata
```

### Caso 3: Produto com Alto Consumo

```
Produto: ABC
Consumo Total: 10000 unidades
Consumo Médio: 500 por saída
Num Saídas: 20

Interpretação: Produto sai frequentemente (20x)
              Cada saída é ~500 unidades
              Total consumido: 10000

Recomendação: Verificar capacidade de reposição
```

## 7️⃣ TROUBLESHOOTING RÁPIDO

### "Diretório não encontrado"

```bash
# Verificar se caminho existe
# Windows:
dir \\192.168.0.77\semar26

# Linux:
ls -la /caminho/dos/dbfs

# Editar config/settings.py com caminho correto
```

### "Encoding error"

```python
# Em config/settings.py, altere:
DBF_ENCODING = "cp1252"  # ou "utf-8", "iso-8859-1", etc
```

### "Database locked"

```bash
# Fechar todas instâncias do Streamlit
# Windows:
taskkill /F /IM python.exe

# Reexecute:
python etl_dbf.py
streamlit run app_dashboard.py
```

### "Sem dados de comparação"

```bash
# Verificar se tabelas existem
python cli.py status

# Se vazio, reexecute ETL:
python etl_dbf.py --clean
```

## 8️⃣ CASOS DE USO COMUNS

### 📊 Auditoria Completa

```bash
# 1. Executar ETL
python etl_dbf.py

# 2. Analisar
python cli.py analyze

# 3. Exportar
python cli.py export --output ./auditoria

# 4. Abrir em Excel/Google Sheets
# Arquivos em ./auditoria/
```

### 🎯 Encontrar Inconsistências Graves

```bash
# 1. Abrir Dashboard
streamlit run app_dashboard.py

# 2. Ir para: Inconsistências
# 3. Ajustar limiar para 50%
# 4. Ver apenas CRÍTICA
```

### 📉 Analisar Consumo Mensal

```bash
# 1. Dashboard → Consumo
# 2. Aumentar Top N para 50
# 3. Analisar padrões
# 4. Exportar Top 10 para planejamento
```

### 🔍 Auditoria de Produto Específico

```bash
# 1. Dashboard → Comparação
# 2. Filtrar por produto (ex: "CIMENTO")
# 3. Ver histórico de movimentos
# 4. Dashboard → Dados → CADMOV
# 5. Buscar produto
```

## 9️⃣ DICAS PRO

**✅ Dica 1**: Executar ETL regularmente (ex: diariamente)
```bash
# Adicionar a cron/task scheduler
0 3 * * * cd /caminho && python etl_dbf.py
```

**✅ Dica 2**: Exportar relatórios antes de reuniões
```bash
python cli.py export --output ./relatorios_$(date +%Y%m%d)
```

**✅ Dica 3**: Personalizar limiar de inconsistência
```python
# Mais rigoroso (5%):
inconsistencias = estoque_calc.detectar_inconsistencias(limiar_erro=5.0)

# Mais leniente (20%):
inconsistencias = estoque_calc.detectar_inconsistencias(limiar_erro=20.0)
```

**✅ Dica 4**: Combinar com Excel para análise
```python
# Exportar com formato:
df.to_excel('analise.xlsx', index=False)
```

## 🔟 PRÓXIMOS PASSOS

1. ✅ Setup completo
2. ✅ Executar ETL pela primeira vez
3. ✅ Explorar Dashboard
4. ✅ Identificar inconsistências principais
5. ✅ Exportar relatórios
6. ✅ Compartilhar com time
7. ⏭️ Planejar correções
8. ⏭️ Automatizar ETL diário
9. ⏭️ Integrar com sistema principal

---

**Precisa de ajuda?** Consulte:
- `README.md` - Visão geral
- `TECHNICAL.md` - Documentação técnica
- `examples.py` - Exemplos de código

**Tempo médio**: 
- Setup: 10 min
- Primeiro ETL: 5-30 min (depende do volume)
- Exploração: 20 min
- Total: ~1 hora para estar pronto ✨
