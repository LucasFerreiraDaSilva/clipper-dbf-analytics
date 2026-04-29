"""
Script de exemplo mostrando como usar a aplicação programaticamente
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DBF_SOURCE_DIR
from core.logger import logger
from etl.processor import processor
from core.business_rules import estoque_calc


def exemplo_etl():
    """Exemplo: Executar ETL"""
    print("\n" + "="*70)
    print("EXEMPLO 1: Executar ETL".center(70))
    print("="*70 + "\n")
    
    try:
        stats = processor.carregar_diretorio(DBF_SOURCE_DIR)
        print(f"✓ ETL concluído:")
        print(f"  - Tabelas: {stats['tabelas_processadas']}")
        print(f"  - Registros: {stats['registros_carregados']}")
        print(f"  - Erros: {stats['erros']}")
    except Exception as e:
        logger.error(f"Erro no ETL: {e}")


def exemplo_comparacao():
    """Exemplo: Comparar estoques"""
    print("\n" + "="*70)
    print("EXEMPLO 2: Comparar Estoques".center(70))
    print("="*70 + "\n")
    
    try:
        # Carregar dados
        estoque_calc.carregar_dados()
        
        # Comparar
        comparacao = estoque_calc.comparar_estoques()
        
        if not comparacao.empty:
            print(f"✓ Comparação gerada com {len(comparacao)} produtos\n")
            
            # Mostrar top 5 com maior erro
            print("Top 5 maiores diferenças:")
            for idx, row in comparacao.head(5).iterrows():
                print(f"  {row['PRODUTO']:30} | "
                      f"Sistema: {row['QUANTIDADE_SISTEMA']:10.0f} | "
                      f"Calculado: {row['QUANTIDADE_CALC']:10.0f} | "
                      f"Erro: {row['PERCENTUAL_ERRO']:6.2f}%")
    
    except Exception as e:
        logger.error(f"Erro na comparação: {e}")


def exemplo_inconsistencias():
    """Exemplo: Detectar inconsistências"""
    print("\n" + "="*70)
    print("EXEMPLO 3: Detectar Inconsistências".center(70))
    print("="*70 + "\n")
    
    try:
        # Detectar
        inconsistencias = estoque_calc.detectar_inconsistencias(limiar_erro=5.0)
        
        if not inconsistencias.empty:
            print(f"✓ Encontradas {len(inconsistencias)} inconsistências\n")
            
            # Agrupar por criticidade
            por_criticidade = inconsistencias['CRITICIDADE'].value_counts()
            print("Distribuição por criticidade:")
            for criticidade, count in por_criticidade.items():
                print(f"  {criticidade}: {count}")
            
            print("\nExemplos de produtos críticos:")
            criticas = inconsistencias[
                inconsistencias['CRITICIDADE'] == 'CRÍTICA'
            ].head(3)
            
            for idx, row in criticas.iterrows():
                print(f"  - {row['PRODUTO']:30} | "
                      f"Diferença: {row['DIFERENCA']:10.0f} | "
                      f"Criticidade: {row['CRITICIDADE']}")
    
    except Exception as e:
        logger.error(f"Erro ao detectar inconsistências: {e}")


def exemplo_consumo():
    """Exemplo: Analisar consumo"""
    print("\n" + "="*70)
    print("EXEMPLO 4: Análise de Consumo".center(70))
    print("="*70 + "\n")
    
    try:
        # Calcular
        consumo = estoque_calc.calcular_consumo_por_produto()
        
        if not consumo.empty:
            print(f"✓ Consumo calculado para {len(consumo)} produtos\n")
            
            print("Top 10 produtos mais consumidos:")
            for idx, row in consumo.head(10).iterrows():
                print(f"  {row['PRODUTO']:30} | "
                      f"Consumo Total: {row['CONSUMO_TOTAL']:10.0f} | "
                      f"Médio: {row['CONSUMO_MEDIO']:8.2f} | "
                      f"Saídas: {row['NUM_SAIDAS']:5.0f}")
    
    except Exception as e:
        logger.error(f"Erro ao calcular consumo: {e}")


def exemplo_exportacao():
    """Exemplo: Exportar dados"""
    print("\n" + "="*70)
    print("EXEMPLO 5: Exportar Dados".center(70))
    print("="*70 + "\n")
    
    try:
        # Comparação
        comparacao = estoque_calc.comparar_estoques()
        
        if not comparacao.empty:
            # Salvar em CSV
            output_file = PROJECT_ROOT / "relatorio_comparacao.csv"
            comparacao.to_csv(output_file, index=False, encoding='utf-8')
            print(f"✓ Relatório salvo em: {output_file}")
        
        # Inconsistências
        inconsistencias = estoque_calc.detectar_inconsistencias()
        
        if not inconsistencias.empty:
            output_file = PROJECT_ROOT / "relatorio_inconsistencias.csv"
            inconsistencias.to_csv(output_file, index=False, encoding='utf-8')
            print(f"✓ Inconsistências salvas em: {output_file}")
    
    except Exception as e:
        logger.error(f"Erro ao exportar: {e}")


def main():
    """Executa exemplos"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "EXEMPLOS DE USO - CLIPPER DBF ANALYTICS".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    exemplos = [
        ("ETL", exemplo_etl),
        ("Comparação", exemplo_comparacao),
        ("Inconsistências", exemplo_inconsistencias),
        ("Consumo", exemplo_consumo),
        ("Exportação", exemplo_exportacao),
    ]
    
    print("\nExemplos disponíveis:")
    for i, (nome, _) in enumerate(exemplos, 1):
        print(f"  {i}. {nome}")
    
    try:
        escolha = input("\nEscolha um exemplo (1-5) ou Enter para todos: ").strip()
        
        if not escolha:
            # Executar todos
            for nome, funcao in exemplos:
                try:
                    funcao()
                except Exception as e:
                    logger.error(f"Erro no exemplo {nome}: {e}")
        else:
            indice = int(escolha) - 1
            if 0 <= indice < len(exemplos):
                nome, funcao = exemplos[indice]
                funcao()
            else:
                print("❌ Opção inválida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Execução cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
