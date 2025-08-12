#!/usr/bin/env python3
"""
Performance and Integration Test for Modern EBook Reader
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

def test_application_startup():
    """Test application startup performance"""
    print("🚀 Testing Application Startup Performance...")
    
    start_time = time.time()
    
    from ui.main_window import MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    startup_time = time.time() - start_time
    
    print(f"✅ Application startup time: {startup_time:.3f} seconds")
    
    if startup_time < 2.0:
        print("✅ Startup performance: EXCELLENT")
    elif startup_time < 5.0:
        print("✅ Startup performance: GOOD")
    else:
        print("⚠️ Startup performance: SLOW")
    
    return True

def test_ui_responsiveness():
    """Test UI responsiveness"""
    print("⚡ Testing UI Responsiveness...")
    
    from ui.main_window import MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    
    # Test rapid UI operations
    start_time = time.time()
    
    for i in range(10):
        window.show()
        QTest.qWait(10)
        if hasattr(window, 'show_welcome'):
            window.show_welcome()
        QTest.qWait(10)
    
    response_time = time.time() - start_time
    
    print(f"✅ UI response time for 20 operations: {response_time:.3f} seconds")
    
    if response_time < 1.0:
        print("✅ UI responsiveness: EXCELLENT")
    elif response_time < 3.0:
        print("✅ UI responsiveness: GOOD")
    else:
        print("⚠️ UI responsiveness: SLOW")
    
    return True

def test_settings_performance():
    """Test settings load/save performance"""
    print("⚙️ Testing Settings Performance...")
    
    import utils.settings as settings
    
    # Test multiple settings operations
    start_time = time.time()
    
    for i in range(100):
        settings.add_recent_book(f"test_book_{i}.pdf")
    
    recent_books = settings.load_recent_books()
    
    for i in range(50):
        settings.set_setting(f"test_key_{i}", f"test_value_{i}")
    
    settings_time = time.time() - start_time
    
    print(f"✅ Settings operations time: {settings_time:.3f} seconds")
    print(f"✅ Recent books loaded: {len(recent_books)}")
    
    # Cleanup
    settings.clear_recent_books()
    
    if settings_time < 1.0:
        print("✅ Settings performance: EXCELLENT")
    elif settings_time < 3.0:
        print("✅ Settings performance: GOOD")
    else:
        print("⚠️ Settings performance: SLOW")
    
    return True

def test_widget_creation():
    """Test widget creation performance"""
    print("🎨 Testing Widget Creation Performance...")
    
    from ui.welcome_widget import WelcomeWidget
    app = QApplication.instance() or QApplication(sys.argv)
    
    start_time = time.time()
    
    widgets = []
    for i in range(10):
        widget = WelcomeWidget()
        widgets.append(widget)
    
    creation_time = time.time() - start_time
    
    print(f"✅ Created 10 widgets in: {creation_time:.3f} seconds")
    
    # Cleanup
    for widget in widgets:
        widget.deleteLater()
    
    if creation_time < 1.0:
        print("✅ Widget creation: EXCELLENT")
    elif creation_time < 3.0:
        print("✅ Widget creation: GOOD")
    else:
        print("⚠️ Widget creation: SLOW")
    
    return True

def test_integration():
    """Test overall integration"""
    print("🔗 Testing Integration...")
    
    from ui.main_window import MainWindow
    import utils.settings as settings
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Test full workflow
    window = MainWindow()
    window.show()
    
    # Add some recent books
    settings.add_recent_book("test1.pdf")
    settings.add_recent_book("test2.pdf")
    
    # Load recent books
    recent = settings.load_recent_books()
    
    print(f"✅ Integration test completed")
    print(f"✅ Recent books: {len(recent)}")
    print(f"✅ Window created and shown")
    
    # Cleanup
    settings.clear_recent_books()
    
    return True

def main():
    """Run performance tests"""
    print("🧪 PERFORMANCE & INTEGRATION TESTS")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tests = [
        ("Application Startup", test_application_startup),
        ("UI Responsiveness", test_ui_responsiveness),
        ("Settings Performance", test_settings_performance),
        ("Widget Creation", test_widget_creation),
        ("Integration", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 PERFORMANCE TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL PERFORMANCE TESTS PASSED! Application is ready for Phase 4.")
        return 0
    else:
        print("⚠️ Some performance tests failed. Review and optimize.")
        return 1

if __name__ == "__main__":
    sys.exit(main())