import subprocess
import sys
import os

def install_dependencies():
    """Instala las dependencias del requirements.txt"""
    print("🚀 Iniciando instalación de dependencias...")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    
    # Ruta al requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        print(f"❌ ERROR: No se encontró requirements.txt en {requirements_path}")
        return False
    
    print(f"\n📦 Instalando desde: {requirements_path}")
    
    try:
        # Instalar dependencias
        subprocess.check_call([
            sys.executable, 
            '-m', 
            'pip', 
            'install', 
            '-r', 
            requirements_path,
        ])
    
        
        print("\n✅ ¡Dependencias instaladas exitosamente!")
        
        # Verificar instalación
        print("\n🔍 Verificando instalación...")
        import flask
        import requests
        from dotenv import load_dotenv
        
        print(f"✅ Flask {flask.__version__}")
        print(f"✅ Requests {requests.__version__}")
        print("✅ python-dotenv instalado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR durante la instalación: {e}")
        return False
    except ImportError as e:
        print(f"\n⚠️ Advertencia: No se pudo importar {e}")
        return False

if __name__ == '__main__':
    success = install_dependencies()
    if success:
        print("\n🎉 Instalación completada. Puedes reiniciar la aplicación ahora.")
    else:
        print("\n❌ Hubo problemas durante la instalación. Revisa los errores arriba.")