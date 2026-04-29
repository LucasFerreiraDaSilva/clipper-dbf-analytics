"""
Gerenciamento de banco de dados SQLite
Cria e gerencia conexões com o banco
"""

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
from config.settings import DATABASE_PATH
from core.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Gerenciador centralizado do banco de dados"""
    
    def __init__(self, db_path: Path = None):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho do arquivo SQLite (usa default se None)
        """
        self.db_path = db_path or DATABASE_PATH
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Cria engine e session factory"""
        try:
            # Criar diretório se não existir
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar engine
            connection_string = f"sqlite:///{self.db_path}"
            self.engine = create_engine(
                connection_string,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"✓ Banco de dados inicializado: {self.db_path}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao inicializar banco: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager para sessões do banco
        
        Yields:
            SQLAlchemy Session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erro na transação: {e}")
            raise
        finally:
            session.close()
    
    def get_tables(self) -> list:
        """
        Lista todas as tabelas do banco
        
        Returns:
            Lista de nomes de tabelas
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            True se existe, False caso contrário
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Obtém informações sobre uma tabela
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            Dicionário com informações
        """
        inspector = inspect(self.engine)
        
        if not self.table_exists(table_name):
            return None
        
        return {
            "columns": inspector.get_columns(table_name),
            "primary_keys": inspector.get_pk_constraint(table_name),
            "row_count": self._get_row_count(table_name)
        }
    
    def _get_row_count(self, table_name: str) -> int:
        """Obtém contagem de linhas de uma tabela"""
        try:
            with self.get_session() as session:
                result = session.execute(f"SELECT COUNT(*) FROM {table_name}")
                return result.scalar()
        except Exception as e:
            logger.error(f"Erro ao contar linhas de {table_name}: {e}")
            return 0
    
    def clear_table(self, table_name: str):
        """
        Limpa todos os dados de uma tabela
        
        Args:
            table_name: Nome da tabela
        """
        try:
            with self.get_session() as session:
                session.execute(f"DELETE FROM {table_name}")
                logger.info(f"✓ Tabela {table_name} limpa")
        except Exception as e:
            logger.error(f"Erro ao limpar {table_name}: {e}")
    
    def close(self):
        """Fecha conexões do banco"""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Conexões do banco fechadas")


# Instância global do gerenciador
db_manager = DatabaseManager()

__all__ = ["DatabaseManager", "db_manager"]
