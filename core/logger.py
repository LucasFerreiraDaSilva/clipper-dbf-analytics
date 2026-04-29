"""
Sistema de logging centralizado
Gerencia logs da aplicação
"""

import logging
import sys
from pathlib import Path
from config.settings import LOG_DIR, LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Configura logger para um módulo
    
    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    level = level or LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo
    log_file = LOG_DIR / f"{name}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Logger global
logger = setup_logger("clipper_etl")

__all__ = ["setup_logger", "logger"]
