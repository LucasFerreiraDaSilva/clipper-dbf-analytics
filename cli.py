"""
Iniciador de linha de comando para a aplicação
Gerencia workflows comuns
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import logger
from config.settings import DBF_SOURCE_DIR, DATABASE_PATH
from etl.processor import processor
from core.business_rules import estoque_calc


def cmd_etl(args):
    """Comando: Executar ETL"""
    logger.info("Iniciando ETL...")
    
    source_dir = Path(args.source) if args.source else DBF_SOURCE_DIR
    
    if not source_dir.exists():
        logger.error(f"Diretório não encontrado: {source_dir}")
        return 1
    
    try:
        stats = processor.carregar_diretorio(source_dir)
        
        if stats['erros'] == 0:
            logger.info("✓ ETL concluído com sucesso")
            return 0
        else:
            logger.warning(f"ETL concluído com {stats['erros']} erros")
            return 1
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


def cmd_status(args):
    """Comando: Exibir status"""
    try:
        tabelas = processor.listar_tabelas_carregadas()
        relatorio = processor.gerar_relatorio()
        print(relatorio)
        return 0
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


def cmd_analyze(args):
    """Comando: Analisar estoques"""
    try:
        estoque_calc.carregar_dados()
        
        print("\n" + "="*70)
        print("ANÁLISE DE ESTOQUE".center(70))
        print("="*70 + "\n")
        
        # Comparação
        comparacao = estoque_calc.comparar_estoques()
        print(f"Produtos analisados: {len(comparacao)}")
        
        # Inconsistências
        inconsistencias = estoque_calc.detectar_inconsistencias(
            limiar_erro=args.threshold
        )
        print(f"Inconsistências encontradas: {len(inconsistencias)}")
        
        if not inconsistencias.empty:
            # Agrupar por criticidade
            por_criticidade = inconsistencias['CRITICIDADE'].value_counts()
            print("\nDistribuição por criticidade:")
            for criticidade, count in por_criticidade.items():
                print(f"  {criticidade}: {count}")
        
        # Consumo
        consumo = estoque_calc.calcular_consumo_por_produto()
        print(f"\nProdutos com saída: {len(consumo)}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


def cmd_export(args):
    """Comando: Exportar dados"""
    try:
        estoque_calc.carregar_dados()
        
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Comparação
        comparacao = estoque_calc.comparar_estoques()
        if not comparacao.empty:
            file = output_dir / "comparacao.csv"
            comparacao.to_csv(file, index=False, encoding='utf-8')
            logger.info(f"✓ Comparação: {file}")
        
        # Inconsistências
        inconsistencias = estoque_calc.detectar_inconsistencias()
        if not inconsistencias.empty:
            file = output_dir / "inconsistencias.csv"
            inconsistencias.to_csv(file, index=False, encoding='utf-8')
            logger.info(f"✓ Inconsistências: {file}")
        
        # Consumo
        consumo = estoque_calc.calcular_consumo_por_produto()
        if not consumo.empty:
            file = output_dir / "consumo.csv"
            consumo.to_csv(file, index=False, encoding='utf-8')
            logger.info(f"✓ Consumo: {file}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


def main():
    """Parser de linha de comando"""
    
    parser = argparse.ArgumentParser(
        description="Clipper DBF Analytics - Ferramenta de linha de comando"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: etl
    etl_parser = subparsers.add_parser('etl', help='Executar ETL')
    etl_parser.add_argument(
        '--source',
        type=str,
        help='Diretório dos arquivos DBF'
    )
    etl_parser.set_defaults(func=cmd_etl)
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Exibir status')
    status_parser.set_defaults(func=cmd_status)
    
    # Comando: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisar estoques')
    analyze_parser.add_argument(
        '--threshold',
        type=float,
        default=5.0,
        help='Limiar de erro para inconsistências (%)'
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Comando: export
    export_parser = subparsers.add_parser('export', help='Exportar dados')
    export_parser.add_argument(
        '--output',
        type=str,
        default='export',
        help='Diretório de saída'
    )
    export_parser.set_defaults(func=cmd_export)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
