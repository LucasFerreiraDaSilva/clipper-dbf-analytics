"""
Leitura de arquivos DBF do sistema legado Clipper
Responsável por extrair dados dos arquivos .DBF
"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dbfread import DBF
from core.logger import setup_logger

logger = setup_logger(__name__)


class DBFReader:
    """Leitor de arquivos DBF com tratamento de erros e encoding"""
    
    def __init__(self, encoding: str = "latin1"):
        """
        Inicializa leitor DBF
        
        Args:
            encoding: Encoding dos arquivos DBF
        """
        self.encoding = encoding
        self.last_error = None
    
    def ler_arquivo(self, caminho_arquivo: Path) -> Optional[pd.DataFrame]:
        """
        Lê arquivo DBF e retorna como DataFrame
        
        Args:
            caminho_arquivo: Caminho do arquivo .DBF
        
        Returns:
            DataFrame ou None se erro
        """
        try:
            if not caminho_arquivo.exists():
                logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
                return None
            
            if not caminho_arquivo.suffix.lower() == ".dbf":
                logger.warning(f"Arquivo não é DBF: {caminho_arquivo}")
                return None
            
            logger.info(f"Lendo: {caminho_arquivo.name}")
            
            # Ler DBF
            dbf_table = DBF(str(caminho_arquivo), encoding=self.encoding)
            
            # Converter para lista de dicionários
            records = []
            for record in dbf_table:
                records.append(dict(record))
            
            if not records:
                logger.warning(f"Arquivo vazio: {caminho_arquivo.name}")
                return pd.DataFrame()
            
            # Criar DataFrame
            df = pd.DataFrame(records)
            
            # Limpar colunas deletadas (começam com *)
            df = df[[col for col in df.columns if not col.startswith('*')]]
            
            logger.info(
                f"✓ Lido: {caminho_arquivo.name} "
                f"({len(df)} linhas, {len(df.columns)} colunas)"
            )
            
            return df
        
        except UnicodeDecodeError as e:
            self.last_error = f"Erro de encoding: {e}"
            logger.error(f"✗ {self.last_error} em {caminho_arquivo.name}")
            return None
        
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"✗ Erro ao ler {caminho_arquivo.name}: {e}")
            return None
    
    def listar_arquivos_dbf(self, diretorio: Path) -> List[Path]:
        """
        Lista todos os arquivos .DBF em um diretório
        
        Args:
            diretorio: Caminho do diretório
        
        Returns:
            Lista de caminhos dos arquivos DBF
        """
        try:
            if not diretorio.exists():
                logger.error(f"Diretório não existe: {diretorio}")
                return []
            
            arquivos = sorted(diretorio.glob("*.DBF"))
            arquivos += sorted(diretorio.glob("*.dbf"))
            
            # Remover duplicatas
            arquivos = list(set(arquivos))
            arquivos.sort()
            
            logger.info(f"✓ Encontrados {len(arquivos)} arquivos DBF em {diretorio.name}")
            
            return arquivos
        
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []
    
    def ler_todos(self, diretorio: Path) -> Dict[str, pd.DataFrame]:
        """
        Lê todos os arquivos DBF de um diretório
        
        Args:
            diretorio: Caminho do diretório
        
        Returns:
            Dicionário com {nome_tabela: DataFrame}
        """
        arquivos = self.listar_arquivos_dbf(diretorio)
        dados = {}
        erros = []
        
        logger.info(f"Processando {len(arquivos)} arquivos...")
        
        for arquivo in arquivos:
            try:
                df = self.ler_arquivo(arquivo)
                
                if df is not None and not df.empty:
                    # Nome da tabela (sem extensão)
                    nome_tabela = arquivo.stem.upper()
                    dados[nome_tabela] = df
                
                elif df is not None and df.empty:
                    erros.append(f"{arquivo.name} (vazio)")
            
            except Exception as e:
                erros.append(f"{arquivo.name}: {e}")
        
        if erros:
            logger.warning(f"Erros ao processar arquivos: {len(erros)}")
            for erro in erros[:5]:  # Mostrar primeiros 5
                logger.warning(f"  - {erro}")
        
        logger.info(f"✓ Total de tabelas carregadas: {len(dados)}")
        
        return dados


__all__ = ["DBFReader"]
