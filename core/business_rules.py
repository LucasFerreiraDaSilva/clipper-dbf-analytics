"""
Regras de negócio da aplicação
Implementa cálculos de estoque, consumo e divergências
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from core.logger import setup_logger
from core.database import db_manager

logger = setup_logger(__name__)


class EstoqueCalculator:
    """
    Calcula estoque real baseado em movimentações
    
    Lógica:
    - Entrada de material → soma no estoque
    - Saída/Faturamento → reduz estoque
    - Produção → consome matéria-prima
    """
    
    def __init__(self):
        self.movimentos = None
        self.estoque_inicial = None
    
    def carregar_dados(self):
        """Carrega dados de movimentação do banco"""
        try:
            with db_manager.get_session() as session:
                # Tenta carregar tabela de movimentos
                if db_manager.table_exists("CADMOV"):
                    query = "SELECT * FROM CADMOV ORDER BY DATA"
                    self.movimentos = pd.read_sql(query, session.bind)
                    logger.info(f"✓ Carregados {len(self.movimentos)} movimentos")
                else:
                    logger.warning("Tabela CADMOV não encontrada")
                    self.movimentos = pd.DataFrame()
                
                # Carrega estoque inicial se disponível
                if db_manager.table_exists("ESTOQUE"):
                    query = "SELECT * FROM ESTOQUE"
                    self.estoque_inicial = pd.read_sql(query, session.bind)
                    logger.info(f"✓ Carregado estoque inicial com {len(self.estoque_inicial)} itens")
                else:
                    logger.warning("Tabela ESTOQUE não encontrada")
                    self.estoque_inicial = pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def calcular_estoque_real(self) -> pd.DataFrame:
        """
        Calcula estoque real a partir de movimentações
        
        Returns:
            DataFrame com estoque calculado por produto
        """
        if self.movimentos is None or self.movimentos.empty:
            logger.warning("Sem dados de movimentos para calcular")
            return pd.DataFrame()
        
        try:
            # Normalizar colunas de referência
            df = self.movimentos.copy()
            
            # Identificar colunas de produto (tenta vários nomes comuns)
            col_produto = self._encontrar_coluna(df, ["PRODUTO", "PROD_ID", "ITEMID", "ITEM_ID"])
            col_quantidade = self._encontrar_coluna(df, ["QUANTIDADE", "QTD", "QTDE", "QUANT"])
            col_tipo = self._encontrar_coluna(df, ["TIPO", "MOVTIPO", "TIPO_MOV", "MOV_TYPE"])
            col_data = self._encontrar_coluna(df, ["DATA", "DATA_MOV", "DT_MOV"])
            
            if not col_produto or not col_quantidade:
                logger.error("Colunas de produto/quantidade não encontradas")
                return pd.DataFrame()
            
            # Filtrar movimentos válidos
            df = df[df[col_quantidade].notna()].copy()
            df[col_quantidade] = pd.to_numeric(df[col_quantidade], errors='coerce').fillna(0)
            
            # Classificar movimentos
            # Entrada: tipo 'E', 'ENTRADA', 'IN', 'COMPRA'
            # Saída: tipo 'S', 'SAIDA', 'OUT', 'VENDA'
            df['tipo_calc'] = df[col_tipo].fillna('').astype(str).str.upper()
            
            entradas = df[df['tipo_calc'].isin(['E', 'ENTRADA', 'IN', 'COMPRA'])][col_quantidade].sum()
            saidas = df[df['tipo_calc'].isin(['S', 'SAIDA', 'OUT', 'VENDA'])][col_quantidade].sum()
            
            # Agrupar por produto
            estoque_calculado = df.groupby(col_produto, as_index=False).agg({
                col_quantidade: 'sum',
                col_tipo: 'count'  # Contar movimentações
            })
            
            estoque_calculado.columns = ['PRODUTO', 'QUANTIDADE_CALC', 'NUM_MOVIMENTOS']
            
            logger.info(f"✓ Estoque calculado para {len(estoque_calculado)} produtos")
            logger.info(f"  Total Entradas: {entradas:.2f}")
            logger.info(f"  Total Saídas: {saidas:.2f}")
            
            return estoque_calculado
        
        except Exception as e:
            logger.error(f"Erro ao calcular estoque real: {e}")
            raise
    
    def comparar_estoques(self) -> pd.DataFrame:
        """
        Compara estoque real (calculado) com estoque do sistema
        
        Returns:
            DataFrame com comparação e divergências
        """
        try:
            estoque_calc = self.calcular_estoque_real()
            
            if estoque_calc.empty or self.estoque_inicial.empty:
                logger.warning("Não há dados para comparação")
                return pd.DataFrame()
            
            # Normalizar coluna de produto no estoque inicial
            col_prod_est = self._encontrar_coluna(
                self.estoque_inicial, 
                ["PRODUTO", "PROD_ID", "ITEMID", "ITEM_ID"]
            )
            col_qtd_est = self._encontrar_coluna(
                self.estoque_inicial,
                ["QUANTIDADE", "QTD", "QTDE", "QUANT", "ESTOQUE"]
            )
            
            if not col_prod_est or not col_qtd_est:
                logger.error("Colunas do estoque não encontradas")
                return pd.DataFrame()
            
            estoque_est = self.estoque_inicial[[col_prod_est, col_qtd_est]].copy()
            estoque_est.columns = ['PRODUTO', 'QUANTIDADE_SISTEMA']
            estoque_est['QUANTIDADE_SISTEMA'] = pd.to_numeric(
                estoque_est['QUANTIDADE_SISTEMA'], 
                errors='coerce'
            ).fillna(0)
            
            # Merge
            comparacao = estoque_calc.merge(
                estoque_est,
                on='PRODUTO',
                how='outer'
            ).fillna(0)
            
            # Calcular divergência
            comparacao['DIFERENCA'] = (
                comparacao['QUANTIDADE_SISTEMA'] - 
                comparacao['QUANTIDADE_CALC']
            )
            comparacao['PERCENTUAL_ERRO'] = (
                (comparacao['DIFERENCA'] / 
                 comparacao['QUANTIDADE_SISTEMA'].replace(0, 1)) * 100
            ).round(2)
            
            # Ordenar por maior divergência
            comparacao = comparacao.sort_values('DIFERENCA', ascending=False)
            
            logger.info(f"✓ Comparação gerada com {len(comparacao)} produtos")
            
            return comparacao
        
        except Exception as e:
            logger.error(f"Erro ao comparar estoques: {e}")
            raise
    
    def detectar_inconsistencias(self, limiar_erro: float = 5.0) -> pd.DataFrame:
        """
        Detecta produtos com inconsistências de estoque
        
        Args:
            limiar_erro: Percentual mínimo de erro para flagging
        
        Returns:
            DataFrame com produtos inconsistentes
        """
        try:
            comparacao = self.comparar_estoques()
            
            if comparacao.empty:
                return pd.DataFrame()
            
            # Filtrar inconsistências
            inconsistencias = comparacao[
                (comparacao['DIFERENCA'].abs() > 0) |
                (comparacao['PERCENTUAL_ERRO'].abs() > limiar_erro)
            ].copy()
            
            inconsistencias['CRITICIDADE'] = inconsistencias.apply(
                self._calcular_criticidade,
                axis=1
            )
            
            inconsistencias = inconsistencias.sort_values('CRITICIDADE', ascending=False)
            
            logger.info(
                f"✓ Detectadas {len(inconsistencias)} inconsistências "
                f"(limiar: {limiar_erro}%)"
            )
            
            return inconsistencias
        
        except Exception as e:
            logger.error(f"Erro ao detectar inconsistências: {e}")
            raise
    
    def calcular_consumo_por_produto(self) -> pd.DataFrame:
        """
        Calcula consumo/saída por produto no período
        
        Returns:
            DataFrame com consumo por produto
        """
        try:
            if self.movimentos is None or self.movimentos.empty:
                return pd.DataFrame()
            
            df = self.movimentos.copy()
            
            col_produto = self._encontrar_coluna(df, ["PRODUTO", "PROD_ID", "ITEMID"])
            col_quantidade = self._encontrar_coluna(df, ["QUANTIDADE", "QTD", "QTDE"])
            col_tipo = self._encontrar_coluna(df, ["TIPO", "MOVTIPO", "TIPO_MOV"])
            
            if not all([col_produto, col_quantidade, col_tipo]):
                return pd.DataFrame()
            
            df = df[df[col_quantidade].notna()].copy()
            df[col_quantidade] = pd.to_numeric(df[col_quantidade], errors='coerce').fillna(0)
            df['tipo_calc'] = df[col_tipo].fillna('').astype(str).str.upper()
            
            # Filtrar apenas saídas
            saidas = df[df['tipo_calc'].isin(['S', 'SAIDA', 'OUT', 'VENDA'])].copy()
            
            consumo = saidas.groupby(col_produto, as_index=False).agg({
                col_quantidade: ['sum', 'count', 'mean']
            }).round(2)
            
            consumo.columns = ['PRODUTO', 'CONSUMO_TOTAL', 'NUM_SAIDAS', 'CONSUMO_MEDIO']
            consumo = consumo.sort_values('CONSUMO_TOTAL', ascending=False)
            
            logger.info(f"✓ Consumo calculado para {len(consumo)} produtos")
            
            return consumo
        
        except Exception as e:
            logger.error(f"Erro ao calcular consumo: {e}")
            raise
    
    @staticmethod
    def _encontrar_coluna(df: pd.DataFrame, opcoes: List[str]) -> str:
        """
        Encontra coluna alternativa no DataFrame
        Útil para lidar com variações de nomes
        
        Args:
            df: DataFrame
            opcoes: Lista de nomes possíveis (em ordem de preferência)
        
        Returns:
            Nome da coluna encontrada ou None
        """
        cols_upper = {col.upper(): col for col in df.columns}
        
        for opcao in opcoes:
            if opcao.upper() in cols_upper:
                return cols_upper[opcao.upper()]
        
        return None
    
    @staticmethod
    def _calcular_criticidade(row: pd.Series) -> str:
        """
        Classifica criticidade de uma inconsistência
        
        Args:
            row: Linha do DataFrame de inconsistências
        
        Returns:
            String com nível: CRÍTICA, ALTA, MÉDIA, BAIXA
        """
        erro_pct = abs(row['PERCENTUAL_ERRO'])
        diferenca = abs(row['DIFERENCA'])
        
        if erro_pct > 50 or diferenca > 1000:
            return "CRÍTICA"
        elif erro_pct > 25 or diferenca > 100:
            return "ALTA"
        elif erro_pct > 10 or diferenca > 10:
            return "MÉDIA"
        else:
            return "BAIXA"


# Instância global
estoque_calc = EstoqueCalculator()

__all__ = ["EstoqueCalculator", "estoque_calc"]
