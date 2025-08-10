#!/usr/bin/env python3
"""
Quick validation script for the Swagger API
"""

import sys
import traceback

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test core FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        # Test models
        from app.models.user import User, UserRole
        print("✅ User model imported successfully")
        
        from app.models.property import Property
        print("✅ Property model imported successfully")
        
        # Test services
        from app.services.auth_service import hash_password, create_access_token
        print("✅ Auth service imported successfully")
        
        # Test controllers
        from app.controllers.user_controller import UserController
        print("✅ User controller imported successfully")
        
        # Test database
        from app.database.database import get_db
        print("✅ Database module imported successfully")
        
        print("\n🎉 All core modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    try:
        from app.config.settings import settings
        print(f"✅ Settings loaded - App: {settings.APP_NAME}")
        print(f"✅ Database URL configured: {bool(settings.SUPABASE_DB_URL)}")
        print(f"✅ Secret key configured: {bool(settings.SECRET_KEY)}")
        return True
    except Exception as e:
        print(f"❌ Config error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Validating Swagger API structure...\n")
    
    all_good = True
    
    # Test imports
    if not test_imports():
        all_good = False
    
    print("\n" + "="*50)
    
    # Test config
    if not test_config():
        all_good = False
    
    print("\n" + "="*50)
    
    if all_good:
        print("✅ All tests passed! Your API structure is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
