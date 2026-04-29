#!/usr/bin/env python3
"""
Script de ETL - Extrai dados de DBF Clipper e carrega em SQLite
Execução: python etl_dbf.py
"""

import sys
import argparse
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DBF_SOURCE_DIR, DATABASE_PATH
from core.logger import logger
from etl.processor import processor


def main():
    """Função principal do ETL"""
    
    print("\n" + "=" * 80)
    print("🔄 ETL - CLIPPER DBF → SQLite".center(80))
    print("=" * 80 + "\n")
    
    # Argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description="Carrega dados de arquivos DBF Clipper para SQLite"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(DBF_SOURCE_DIR),
        help=f"Diretório dos arquivos DBF (default: {DBF_SOURCE_DIR})"
    )
    parser.add_argument(
        "--database",
        type=str,
        default=str(DATABASE_PATH),
        help=f"Caminho do banco SQLite (default: {DATABASE_PATH})"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpar banco antes de carregar"
    )
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    
    # Validações
    if not source_dir.exists():
        logger.error(f"✗ Diretório não encontrado: {source_dir}")
        logger.error("Verifique a configuração em config/settings.py")
        return 1
    
    try:
        # Carregar dados
        logger.info(f"📂 Fonte: {source_dir}")
        logger.info(f"💾 Banco: {DATABASE_PATH}\n")
        
        # Se flag --clean, limpar todas as tabelas
        if args.clean:
            logger.warning("Limpando banco de dados...")
            tabelas = processor.listar_tabelas_carregadas()
            for tabela in tabelas:
                db_manager.clear_table(tabela)
        
        # Processar diretório
        stats = processor.carregar_diretorio(source_dir)
        
        # Gerar relatório
        relatorio = processor.gerar_relatorio()
        print(relatorio)
        
        # Resultado
        if stats["erros"] == 0:
            logger.info("✓ ETL concluído com sucesso!")
            return 0
        else:
            logger.warning(f"⚠ ETL concluído com {stats['erros']} erros")
            return 1
    
    except Exception as e:
        logger.error(f"✗ Erro fatal no ETL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
