#!/usr/bin/env python3
"""
Final Verification Script for Modern EBook Reader
Comprehensive check before Phase 4
"""

import sys
import os
from pathlib import Path

def check_file_structure():
    """Verify all required files exist"""
    print("📁 Checking File Structure...")
    
    required_files = [
        "main.py",
        "src/ui/main_window.py",
        "src/ui/welcome_widget.py",
        "src/ui/document_viewer.py",
        "src/readers/document_manager.py",
        "src/readers/pdf_reader.py",
        "src/utils/settings.py",
        "src/utils/logger.py",
        "requirements.txt",
        "test_document.pdf"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def check_dependencies():
    """Check if all dependencies are available"""
    print("📦 Checking Dependencies...")
    
    required_modules = [
        "PyQt5",
        "qfluentwidgets"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {missing_modules}")
        return False
    
    print("✅ All dependencies available")
    return True

def check_imports():
    """Test all critical imports"""
    print("🔗 Checking Imports...")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from ui.main_window import MainWindow
        from ui.welcome_widget import WelcomeWidget
        from ui.document_viewer import DocumentViewer
        from readers.document_manager import DocumentManager
        from readers.pdf_reader import PDFReader
        import utils.settings as settings
        from utils.logger import setup_logging
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def check_functionality():
    """Test basic functionality"""
    print("⚙️ Checking Basic Functionality...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        
        from ui.main_window import MainWindow
        window = MainWindow()
        
        # Test settings
        import utils.settings as settings
        settings.add_recent_book("test.pdf")
        recent = settings.load_recent_books()
        settings.clear_recent_books()
        
        print("✅ Basic functionality working")
        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

def check_code_quality():
    """Check code quality indicators"""
    print("🔍 Checking Code Quality...")
    
    # Check for basic code quality indicators
    main_window_path = Path("src/ui/main_window.py")
    if main_window_path.exists():
        content = main_window_path.read_text(encoding='utf-8')
        
        quality_checks = [
            ("Docstrings", '"""' in content),
            ("Error handling", "try:" in content and "except" in content),
            ("Logging", "logger" in content or "logging" in content),
            ("Type hints", ":" in content and "->" in content),
        ]
        
        passed_checks = sum(1 for _, check in quality_checks if check)
        
        print(f"✅ Code quality checks: {passed_checks}/{len(quality_checks)} passed")
        
        for check_name, passed in quality_checks:
            status = "✅" if passed else "⚠️"
            print(f"  {status} {check_name}")
        
        return passed_checks >= len(quality_checks) // 2
    
    return False

def main():
    """Run final verification"""
    print("🧪 FINAL VERIFICATION FOR PHASE 4")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Imports", check_imports),
        ("Functionality", check_functionality),
        ("Code Quality", check_code_quality),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_func():
                print(f"✅ {check_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {check_name}: FAILED")
        except Exception as e:
            print(f"❌ {check_name}: FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 FINAL VERIFICATION: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED!")
        print("🚀 APPLICATION IS READY FOR PHASE 4!")
        print("\nPhase 4 Features to Implement:")
        print("• Advanced search and indexing")
        print("• Bookmarks and annotations")
        print("• Reading statistics and progress tracking")
        print("• Export and sharing capabilities")
        print("• Advanced theming and customization")
        print("• Plugin system for extensibility")
        return 0
    else:
        print("⚠️ Some checks failed. Address issues before Phase 4.")
        return 1

if __name__ == "__main__":
    sys.exit(main())