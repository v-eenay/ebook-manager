#!/usr/bin/env python3
"""
Create a test PDF for testing the document viewer
"""

try:
    import fitz  # PyMuPDF
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Add a page
    page = doc.new_page()
    
    # Add some text
    text = """
    Modern EBook Reader Test Document
    
    This is a test PDF document created to verify the document viewing functionality 
    of the Modern EBook Reader application.
    
    Features being tested:
    • PDF document loading
    • Page rendering with PyMuPDF
    • Microsoft Fluent Design System integration
    • Ribbon toolbar functionality
    • Navigation controls
    
    Page 1 of 3
    """
    
    # Insert text
    page.insert_text((50, 100), text, fontsize=12, color=(0, 0, 0))
    
    # Add second page
    page2 = doc.new_page()
    text2 = """
    Modern EBook Reader Test Document - Page 2
    
    This is the second page of the test document.
    
    Testing navigation functionality:
    • Previous page button
    • Next page button
    • Page counter display
    
    The ribbon toolbar should show:
    • File operations (Open, Close)
    • View controls (Zoom In, Zoom Out, Fit Window)
    • Navigation (Previous, Next)
    
    Page 2 of 3
    """
    page2.insert_text((50, 100), text2, fontsize=12, color=(0, 0, 0))
    
    # Add third page
    page3 = doc.new_page()
    text3 = """
    Modern EBook Reader Test Document - Page 3
    
    This is the final page of the test document.
    
    Theme testing:
    • Light theme with high contrast
    • Dark theme with proper visibility
    • Theme toggle functionality
    
    Document viewer features:
    • Scroll area for large documents
    • Proper scaling and display
    • Professional appearance
    
    Page 3 of 3 - End of Document
    """
    page3.insert_text((50, 100), text3, fontsize=12, color=(0, 0, 0))
    
    # Save the document
    doc.save("test_document.pdf")
    doc.close()
    
    print("✅ Test PDF created successfully: test_document.pdf")
    
except ImportError:
    print("❌ PyMuPDF not available. Cannot create test PDF.")
except Exception as e:
    print(f"❌ Error creating test PDF: {e}")
