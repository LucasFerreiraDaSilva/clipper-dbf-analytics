"""
Processador de dados DBF para SQLite
Transforma e carrega dados no banco de dados
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from sqlalchemy import text
from core.logger import setup_logger
from core.database import db_manager
from config.settings import DBF_ENCODING
from etl.dbf_reader import DBFReader

logger = setup_logger(__name__)


class DBFProcessor:
    """Processa e carrega dados DBF no SQLite"""
    
    def __init__(self):
        """Inicializa o processador"""
        self.reader = DBFReader(encoding=DBF_ENCODING)
        self.stats = {
            "tabelas_processadas": 0,
            "registros_carregados": 0,
            "erros": 0
        }
    
    def processar_dados(self, df: pd.DataFrame, tabela: str) -> Optional[pd.DataFrame]:
        """
        Aplica transformações nos dados
        
        Args:
            df: DataFrame com dados brutos
            tabela: Nome da tabela
        
        Returns:
            DataFrame processado
        """
        try:
            df = df.copy()
            
            # Renomear colunas para maiúsculas
            df.columns = df.columns.str.upper()
            
            # Remover linhas completamente vazias
            df = df.dropna(how='all')
            
            # Remover espaços em branco de colunas texto
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()
            
            # Tratar datas
            for col in df.columns:
                if 'data' in col.lower() or 'dt' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except:
                        pass
            
            # Converter booleanos
            for col in df.select_dtypes(include=['bool']).columns:
                df[col] = df[col].astype(int)
            
            return df
        
        except Exception as e:
            logger.error(f"Erro ao processar {tabela}: {e}")
            return None
    
    def carregar_arquivo(self, caminho_arquivo: Path) -> bool:
        """
        Carrega um arquivo DBF para o banco
        
        Args:
            caminho_arquivo: Caminho do arquivo .DBF
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Ler arquivo
            df = self.reader.ler_arquivo(caminho_arquivo)
            
            if df is None or df.empty:
                return False
            
            # Nome da tabela
            nome_tabela = caminho_arquivo.stem.upper()
            
            # Processar dados
            df = self.processar_dados(df, nome_tabela)
            
            if df is None or df.empty:
                return False
            
            # Carregar no banco
            with db_manager.get_session() as session:
                # Deletar dados existentes (recarregar)
                session.execute(text(f"DELETE FROM {nome_tabela}"))
                session.commit()
                logger.info(f"  Limpando tabela existente: {nome_tabela}")
            
            # Inserir novos dados
            engine = db_manager.engine
            df.to_sql(
                nome_tabela,
                engine,
                if_exists='append',
                index=False
            )
            
            self.stats["tabelas_processadas"] += 1
            self.stats["registros_carregados"] += len(df)
            
            logger.info(f"✓ Carregado: {nome_tabela} ({len(df)} registros)")
            
            return True
        
        except Exception as e:
            self.stats["erros"] += 1
            logger.error(f"✗ Erro ao carregar {caminho_arquivo.name}: {e}")
            return False
    
    def carregar_diretorio(self, diretorio: Path) -> Dict:
        """
        Carrega todos os arquivos DBF de um diretório
        
        Args:
            diretorio: Caminho do diretório
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Listar arquivos
            arquivos = self.reader.listar_arquivos_dbf(diretorio)
            
            if not arquivos:
                logger.warning(f"Nenhum arquivo DBF encontrado em {diretorio}")
                return self.stats
            
            logger.info(f"Processando {len(arquivos)} arquivos de {diretorio}")
            
            # Resetar stats
            self.stats = {
                "tabelas_processadas": 0,
                "registros_carregados": 0,
                "erros": 0
            }
            
            # Processar cada arquivo
            for arquivo in arquivos:
                self.carregar_arquivo(arquivo)
            
            # Resumo
            logger.info("=" * 60)
            logger.info("RESUMO DO CARREGAMENTO")
            logger.info("=" * 60)
            logger.info(f"Tabelas processadas: {self.stats['tabelas_processadas']}")
            logger.info(f"Registros carregados: {self.stats['registros_carregados']}")
            logger.info(f"Erros: {self.stats['erros']}")
            logger.info("=" * 60)
            
            return self.stats
        
        except Exception as e:
            logger.error(f"Erro ao carregar diretório: {e}")
            return self.stats
    
    def listar_tabelas_carregadas(self) -> list:
        """
        Lista todas as tabelas carregadas no banco
        
        Returns:
            Lista de nomes de tabelas
        """
        return db_manager.get_tables()
    
    def gerar_relatorio(self) -> str:
        """
        Gera relatório sobre o estado do banco
        
        Returns:
            String com relatório
        """
        try:
            tabelas = db_manager.get_tables()
            
            relatorio = "\n" + "=" * 70 + "\n"
            relatorio += "RELATÓRIO DE TABELAS CARREGADAS\n"
            relatorio += "=" * 70 + "\n\n"
            
            total_registros = 0
            
            for tabela in sorted(tabelas):
                info = db_manager.get_table_info(tabela)
                
                if info:
                    num_cols = len(info['columns'])
                    num_registros = info['row_count']
                    total_registros += num_registros
                    
                    relatorio += f"📊 {tabela:<20} | "
                    relatorio += f"Colunas: {num_cols:<3} | "
                    relatorio += f"Registros: {num_registros:<10}\n"
            
            relatorio += "\n" + "-" * 70 + "\n"
            relatorio += f"Total de tabelas: {len(tabelas)}\n"
            relatorio += f"Total de registros: {total_registros}\n"
            relatorio += "=" * 70 + "\n"
            
            return relatorio
        
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return "Erro ao gerar relatório"


# Instância global
processor = DBFProcessor()

__all__ = ["DBFProcessor", "processor"]
