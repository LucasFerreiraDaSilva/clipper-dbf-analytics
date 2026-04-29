"""
Configurações globais da aplicação
Define caminhos, nomes de tabelas e parâmetros do sistema
"""

import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório dos arquivos DBF originais (Clipper)
# Ajuste este caminho conforme sua instalação
DBF_SOURCE_DIR = r"\\192.168.0.77\semar26"  # Caminho UNC da rede
# Alternativa local:
# DBF_SOURCE_DIR = Path("C:/dados/semar26")

# Diretório de banco de dados
DATABASE_DIR = BASE_DIR / "data"
DATABASE_DIR.mkdir(exist_ok=True)

# Caminho do banco SQLite
DATABASE_PATH = DATABASE_DIR / "clipper_data.db"

# Diretório de logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configurações de encoding
DBF_ENCODING = "latin1"  # Encoding padrão de arquivos DBF do Clipper

# Tabelas principais de interesse (pode ser vazio para processar todas)
MAIN_TABLES = [
    "ACESSOS",      # Acessórios
    "CADMOV",       # Movimentações de estoque
    "ESTOQUE",      # Estoque
    "MOVIMENT",     # Movimentos
    "CLIENTES",     # Clientes
    "COMPRAS",      # Compras
    "VENDAS",       # Vendas
    "PRODUCTS",     # Produtos
]

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurações de processamento
CHUNK_SIZE = 5000  # Tamanho dos chunks para processamento de grandes arquivos
MAX_WORKERS = 4    # Workers para processamento paralelo

# Mapeamento de tipos de dados para DBF
# Usado para compatibilidade entre DBF e SQLite
TYPE_MAPPING = {
    "C": "TEXT",      # Character
    "N": "REAL",      # Numeric
    "D": "TEXT",      # Date (armazenado como texto)
    "L": "INTEGER",   # Logical (armazenado como 0/1)
    "M": "TEXT",      # Memo
    "F": "REAL",      # Float
}

# Filtros padrão para análise
STOCK_MOVEMENTS = ["E", "S", "T"]  # Entrada, Saída, Transferência
PRODUCTION_TYPES = ["P", "S"]      # Produção, Semi-elaborado

print(f"✓ Configurações carregadas")
print(f"  DBF Source: {DBF_SOURCE_DIR}")
print(f"  Database: {DATABASE_PATH}")
