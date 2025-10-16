#!/usr/bin/env python3
"""
Comprehensive validation script for LP Document Parser setup.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_core_imports():
    """Test core application imports."""
    print("🧪 Testing core imports...")
    
    try:
        from app.core.config import settings
        print("  ✅ Configuration imported")
    except Exception as e:
        print(f"  ❌ Configuration import failed: {e}")
        return False
    
    try:
        from app.db.database import engine, SessionLocal, Base
        print("  ✅ Database modules imported")
    except Exception as e:
        print(f"  ❌ Database import failed: {e}")
        return False
    
    try:
        from app.models.user import User
        from app.models.document import Document
        print("  ✅ Models imported")
    except Exception as e:
        print(f"  ❌ Models import failed: {e}")
        return False
    
    try:
        from app.schemas.schemas import DocumentResponse, UserResponse
        print("  ✅ Schemas imported")
    except Exception as e:
        print(f"  ❌ Schemas import failed: {e}")
        return False
    
    try:
        from app.core.security import get_password_hash, create_access_token
        print("  ✅ Security modules imported")
    except Exception as e:
        print(f"  ❌ Security import failed: {e}")
        return False
    
    return True


def test_api_imports():
    """Test API imports."""
    print("\n🌐 Testing API imports...")
    
    try:
        from app.api.auth import router as auth_router
        print("  ✅ Auth API imported")
    except Exception as e:
        print(f"  ❌ Auth API import failed: {e}")
        return False
    
    try:
        from app.api.documents import router as docs_router
        print("  ✅ Documents API imported")
    except Exception as e:
        print(f"  ❌ Documents API import failed: {e}")
        return False
    
    return True


def test_optional_imports():
    """Test optional dependencies."""
    print("\n🔧 Testing optional dependencies...")
    
    optional_modules = [
        ("docling", "Document processing with Docling"),
        ("pytesseract", "OCR processing with Tesseract"),
        ("celery", "Background task processing"),
        ("redis", "Redis caching"),
        ("minio", "MinIO file storage"),
    ]
    
    results = []
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}: {description}")
            results.append(True)
        except ImportError:
            print(f"  ⚠️  {module_name}: {description} (not installed)")
            results.append(False)
    
    return results


def test_fastapi_app():
    """Test FastAPI application creation."""
    print("\n🚀 Testing FastAPI application...")
    
    try:
        from app.main import app
        print("  ✅ FastAPI app created successfully")
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/", "/auth/login", "/auth/register", "/documents/upload"]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✅ Route {route} registered")
            else:
                print(f"  ⚠️  Route {route} not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI app creation failed: {e}")
        return False


def test_database_models():
    """Test database model relationships."""
    print("\n🗄️  Testing database models...")
    
    try:
        from app.db.database import Base
        from app.models.user import User
        from app.models.document import Document, CapitalCallDetail, DistributionDetail
        
        # Check if models are registered with Base
        tables = Base.metadata.tables.keys()
        expected_tables = ["users", "documents", "capital_call_details", "distribution_details"]
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ Table {table} registered")
            else:
                print(f"  ❌ Table {table} not registered")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database models test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Check required settings
        required_settings = [
            'database_url', 'secret_key', 'upload_dir', 
            'max_file_size', 'allowed_extensions', 'api_title'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if setting == 'secret_key' and value == "your-secret-key-change-in-production":
                    print(f"  ⚠️  {setting}: Using default value (change in production)")
                else:
                    print(f"  ✅ {setting}: {value}")
            else:
                print(f"  ❌ {setting}: Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_directory_structure():
    """Test directory structure."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'app', 'app/api', 'app/core', 'app/db', 'app/models',
        'app/schemas', 'app/services', 'app/tasks',
        'deployment/docker', 'scripts', 'docs', 'tests',
        'alembic', 'alembic/versions'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} (missing)")
            all_exist = False
    
    return all_exist


def test_critical_files():
    """Test critical files."""
    print("\n📄 Testing critical files...")
    
    critical_files = [
        'requirements.txt', 'main.py', 'alembic.ini',
        'app/main.py', 'app/core/config.py', 'app/db/database.py',
        'deployment/docker/docker-compose.yml',
        'deployment/docker/Dockerfile', 'env.example'
    ]
    
    all_exist = True
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist


def test_scripts():
    """Test utility scripts."""
    print("\n🛠️  Testing utility scripts...")
    
    scripts = [
        'scripts/setup_db.py',
        'scripts/check_db.py', 
        'scripts/create_user.py',
        'scripts/test_setup.py',
        'scripts/validate_setup.py'
    ]
    
    all_exist = True
    for script in scripts:
        if Path(script).exists():
            # Check if script is executable
            if os.access(script, os.X_OK):
                print(f"  ✅ {script} (executable)")
            else:
                print(f"  ✅ {script} (not executable)")
        else:
            print(f"  ❌ {script} (missing)")
            all_exist = False
    
    return all_exist


def main():
    """Main validation function."""
    print("🔍 LP Document Parser - Comprehensive Setup Validation")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("API Imports", test_api_imports),
        ("FastAPI App", test_fastapi_app),
        ("Database Models", test_database_models),
        ("Configuration", test_configuration),
        ("Directory Structure", test_directory_structure),
        ("Critical Files", test_critical_files),
        ("Utility Scripts", test_scripts),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test optional dependencies
    optional_results = test_optional_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Validation Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Core Tests: {passed}/{len(results)} passed")
    print(f"🔧 Optional Dependencies: {sum(optional_results)}/{len(optional_results)} available")
    
    if passed == len(results):
        print("\n🎉 All core tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Copy env.example to .env and configure database")
        print("2. Install optional dependencies: pip install -r requirements.txt")
        print("3. Run: python scripts/setup_db.py")
        print("4. Start the application: python main.py")
    else:
        print("\n⚠️  Some core tests failed. Please fix the issues above.")
        
        failed_tests = [name for name, result in results if not result]
        if "Core Imports" in failed_tests:
            print("\n💡 Core import issues:")
            print("- Install required dependencies: pip install sqlalchemy fastapi uvicorn")
        if "Configuration" in failed_tests:
            print("\n💡 Configuration issues:")
            print("- Check app/core/config.py for syntax errors")
        if "Directory Structure" in failed_tests or "Critical Files" in failed_tests:
            print("\n💡 File structure issues:")
            print("- Ensure all required files and directories exist")


if __name__ == "__main__":
    main()
