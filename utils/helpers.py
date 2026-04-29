"""
Utilitários e funções auxiliares
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from core.logger import setup_logger

logger = setup_logger(__name__)


def validar_estrutura_projeto(root_dir: Path = None) -> bool:
    """
    Valida se a estrutura do projeto está completa
    
    Args:
        root_dir: Diretório raiz do projeto
    
    Returns:
        True se válido, False caso contrário
    """
    if root_dir is None:
        root_dir = Path(__file__).resolve().parent
    
    diretorios_necessarios = [
        root_dir / "config",
        root_dir / "core",
        root_dir / "etl",
        root_dir / "dashboard",
        root_dir / "data",
        root_dir / "logs"
    ]
    
    arquivos_necessarios = [
        root_dir / "config" / "settings.py",
        root_dir / "core" / "database.py",
        root_dir / "core" / "business_rules.py",
        root_dir / "etl" / "dbf_reader.py",
        root_dir / "etl" / "processor.py",
        root_dir / "etl_dbf.py",
        root_dir / "app_dashboard.py"
    ]
    
    # Validar diretórios
    for diretorio in diretorios_necessarios:
        if not diretorio.exists():
            logger.error(f"Diretório não encontrado: {diretorio}")
            return False
    
    # Validar arquivos
    for arquivo in arquivos_necessarios:
        if not arquivo.exists():
            logger.error(f"Arquivo não encontrado: {arquivo}")
            return False
    
    logger.info("✓ Estrutura do projeto validada com sucesso")
    return True


def sanitizar_nome_tabela(nome: str) -> str:
    """
    Sanitiza nome de tabela SQL
    
    Args:
        nome: Nome original
    
    Returns:
        Nome sanitizado
    """
    nome = nome.upper()
    nome = nome.replace("-", "_")
    nome = nome.replace(".", "_")
    nome = "".join(c for c in nome if c.isalnum() or c == "_")
    
    # Não começar com número
    if nome and nome[0].isdigit():
        nome = "_" + nome
    
    return nome


def formatar_numero(valor: float, casas: int = 2) -> str:
    """
    Formata número com separadores de milhares
    
    Args:
        valor: Número a formatar
        casas: Casas decimais
    
    Returns:
        String formatada
    """
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def exibir_progresso(atual: int, total: int) -> str:
    """
    Cria barra de progresso em texto
    
    Args:
        atual: Valor atual
        total: Valor total
    
    Returns:
        String com barra
    """
    if total == 0:
        return "[" + "=" * 50 + "] 0%"
    
    percentual = (atual / total) * 100
    tamanho_barra = 50
    barra_preenchida = int(tamanho_barra * atual / total)
    
    barra = "[" + "=" * barra_preenchida + " " * (tamanho_barra - barra_preenchida) + "]"
    
    return f"{barra} {percentual:.1f}%"


def comparar_dfs(df1: pd.DataFrame, df2: pd.DataFrame, coluna_chave: str) -> dict:
    """
    Compara dois DataFrames
    
    Args:
        df1: Primeiro DataFrame
        df2: Segundo DataFrame
        coluna_chave: Coluna para fazer merge
    
    Returns:
        Dicionário com diferenças
    """
    
    resultado = {
        "apenas_em_df1": df1[~df1[coluna_chave].isin(df2[coluna_chave])],
        "apenas_em_df2": df2[~df2[coluna_chave].isin(df1[coluna_chave])],
        "em_ambos": df1[df1[coluna_chave].isin(df2[coluna_chave])]
    }
    
    return resultado


__all__ = [
    "validar_estrutura_projeto",
    "sanitizar_nome_tabela",
    "formatar_numero",
    "exibir_progresso",
    "comparar_dfs"
]
