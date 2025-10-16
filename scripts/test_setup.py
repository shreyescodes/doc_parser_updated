#!/usr/bin/env python3
"""
Test script to validate the LP Document Parser setup.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from app.core.config import settings
        print("  ✅ Configuration imported")
    except Exception as e:
        print(f"  ❌ Configuration import failed: {e}")
        return False
    
    try:
        from app.db.database import engine, SessionLocal
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
        from app.services.document_processor import DocumentProcessor
        from app.services.lp_extractor import LPDocumentExtractor
        print("  ✅ Services imported")
    except Exception as e:
        print(f"  ❌ Services import failed: {e}")
        return False
    
    try:
        from app.api.auth import router as auth_router
        from app.api.documents import router as docs_router
        print("  ✅ API modules imported")
    except Exception as e:
        print(f"  ❌ API import failed: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Check required settings
        required_settings = [
            'database_url', 'secret_key', 'upload_dir', 
            'max_file_size', 'allowed_extensions'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                print(f"  ✅ {setting}: {getattr(settings, setting)}")
            else:
                print(f"  ❌ {setting}: Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\n📁 Testing directories...")
    
    required_dirs = [
        'app', 'app/api', 'app/core', 'app/db', 'app/models',
        'app/schemas', 'app/services', 'app/tasks',
        'deployment/docker', 'scripts', 'docs', 'tests'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} (missing)")
            all_exist = False
    
    return all_exist


def test_files():
    """Test if required files exist."""
    print("\n📄 Testing files...")
    
    required_files = [
        'requirements.txt', 'main.py', 'alembic.ini',
        'app/main.py', 'app/core/config.py', 'app/db/database.py',
        'deployment/docker/docker-compose.yml',
        'deployment/docker/Dockerfile'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist


def test_database_connection():
    """Test database connection (if configured)."""
    print("\n🗄️  Testing database connection...")
    
    try:
        from app.core.config import settings
        
        # Check if database URL is configured
        if settings.database_url == "postgresql://username:password@localhost:5432/doc_parser":
            print("  ⚠️  Using default database URL - configure .env file")
            return False
        
        from app.db.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            if result:
                print("  ✅ Database connection successful")
                return True
            else:
                print("  ❌ Database connection failed")
                return False
                
    except Exception as e:
        print(f"  ❌ Database connection test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 LP Document Parser - Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Directory Test", test_directories),
        ("File Test", test_files),
        ("Database Connection Test", test_database_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Copy env.example to .env and configure database")
        print("2. Run: python scripts/setup_db.py")
        print("3. Start the application: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        
        if not results[4][1]:  # Database connection test
            print("\n💡 Database setup help:")
            print("1. Install PostgreSQL")
            print("2. Copy env.example to .env")
            print("3. Configure database credentials in .env")
            print("4. Run: python scripts/setup_db.py")


if __name__ == "__main__":
    main()
