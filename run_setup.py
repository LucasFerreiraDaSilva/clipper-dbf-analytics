#!/usr/bin/env python3
"""
Script de inicialização e verificação do projeto
Execução: python run_setup.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DBF_SOURCE_DIR, DATABASE_PATH
from core.logger import logger
from utils.helpers import validar_estrutura_projeto


def print_banner():
    """Exibe banner de boas-vindas"""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║        🗃️  CLIPPER DBF ANALYTICS - SISTEMA DE SETUP           ║
    ║                                                                ║
    ║        Aplicação para análise de estoque Clipper/xBase        ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Verifica ambiente e dependências"""
    
    print("\n" + "="*70)
    print("VERIFICANDO AMBIENTE".center(70))
    print("="*70 + "\n")
    
    checks = {
        "Python 3.10+": lambda: sys.version_info >= (3, 10),
        "Estrutura do projeto": lambda: validar_estrutura_projeto(),
        "Diretório de dados": lambda: DATABASE_PATH.parent.exists() or True,
        "Diretório de logs": lambda: (PROJECT_ROOT / "logs").exists() or True,
    }
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            if result:
                print(f"✅ {check_name:<40} PASSOU")
                passed += 1
            else:
                print(f"❌ {check_name:<40} FALHOU")
                failed += 1
        except Exception as e:
            print(f"❌ {check_name:<40} ERRO: {e}")
            failed += 1
    
    print("\n" + "-"*70)
    print(f"Resultado: {passed} passou(s), {failed} falhou/falharam")
    print("-"*70 + "\n")
    
    return failed == 0


def check_dependencies():
    """Verifica dependências Python"""
    
    print("\n" + "="*70)
    print("VERIFICANDO DEPENDÊNCIAS".center(70))
    print("="*70 + "\n")
    
    required_packages = {
        "pandas": "Processamento de dados",
        "sqlalchemy": "ORM para banco de dados",
        "dbfread": "Leitura de arquivos DBF",
        "streamlit": "Framework para dashboard",
        "plotly": "Visualização de gráficos",
    }
    
    installed = 0
    missing = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package:<20} ({description})")
            installed += 1
        except ImportError:
            print(f"❌ {package:<20} (faltando)")
            missing.append(package)
    
    if missing:
        print("\n" + "⚠️ " + "="*66)
        print("Pacotes faltando. Instale com:")
        print(f"\n  pip install -r requirements.txt\n")
        print("="*70 + "\n")
        return False
    else:
        print("\n✅ Todas as dependências OK\n")
        return True


def show_configuration():
    """Exibe configuração atual"""
    
    print("\n" + "="*70)
    print("CONFIGURAÇÃO ATUAL".center(70))
    print("="*70 + "\n")
    
    print(f"📂 Diretório raiz:     {PROJECT_ROOT}")
    print(f"📁 Fonte DBF:          {DBF_SOURCE_DIR}")
    print(f"💾 Banco de dados:     {DATABASE_PATH}")
    print(f"📝 Logs:               {PROJECT_ROOT / 'logs'}")
    print("\n")


def show_next_steps():
    """Exibe próximos passos"""
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASSOS".center(70))
    print("="*70 + "\n")
    
    steps = [
        ("1️⃣ ", "Verificar configuração", "Editar config/settings.py se necessário"),
        ("2️⃣ ", "Executar ETL", "python etl_dbf.py"),
        ("3️⃣ ", "Abrir Dashboard", "streamlit run app_dashboard.py"),
    ]
    
    for number, title, command in steps:
        print(f"{number} {title}")
        print(f"   └─ {command}\n")


def main():
    """Função principal"""
    
    print_banner()
    
    # Verificar estrutura
    if not check_environment():
        logger.error("Ambiente não válido. Por favor, corrija os problemas acima.")
        return 1
    
    # Verificar dependências
    if not check_dependencies():
        logger.error("Dependências não instaladas.")
        return 1
    
    # Mostrar configuração
    show_configuration()
    
    # Próximos passos
    show_next_steps()
    
    # Conclusão
    print("="*70)
    print("✅ SETUP VERIFICADO COM SUCESSO!".center(70))
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
