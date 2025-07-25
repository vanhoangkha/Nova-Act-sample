#!/usr/bin/env python3
"""
Nova Act Demo: File Upload and Download Operations
==================================================

This demo shows how to handle file uploads and downloads using Nova Act,
as described in the Nova Act README.
"""

import os
import sys
import tempfile
from pathlib import Path
from nova_act import NovaAct

def create_sample_files():
    """Create sample files for upload testing"""
    sample_dir = "./demo/sample_files"
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create a sample text file
    text_file = os.path.join(sample_dir, "sample_document.txt")
    with open(text_file, "w") as f:
        f.write("This is a sample document for Nova Act file upload testing.\n")
        f.write("Created for demonstration purposes.\n")
        f.write("Contains multiple lines of text content.\n")
    
    # Create a sample CSV file
    csv_file = os.path.join(sample_dir, "sample_data.csv")
    with open(csv_file, "w") as f:
        f.write("Name,Age,City\n")
        f.write("John Doe,30,New York\n")
        f.write("Jane Smith,25,Los Angeles\n")
        f.write("Bob Johnson,35,Chicago\n")
    
    # Create a sample image file (simple text-based representation)
    image_file = os.path.join(sample_dir, "sample_image.txt")
    with open(image_file, "w") as f:
        f.write("This represents a sample image file for upload testing.\n")
        f.write("In a real scenario, this would be an actual image file.\n")
    
    return {
        "text": text_file,
        "csv": csv_file,
        "image": image_file
    }

def file_upload_demo():
    """
    Demo for uploading files to a website
    """
    print("📤 Starting File Upload Demo")
    print("=" * 35)
    
    # Create sample files
    sample_files = create_sample_files()
    
    try:
        # Using a file upload testing site
        with NovaAct(
            starting_page="https://file.io/",  # Free file upload service
            logs_directory="./demo/logs/file_upload"
        ) as nova:
            print("🌐 Navigating to file upload site...")
            
            # Upload text file
            print("📄 Uploading text file...")
            upload_filename = sample_files["text"]
            
            # Use Playwright's file upload capability
            nova.page.set_input_files('input[type="file"]', upload_filename)
            
            # Wait for upload to complete
            nova.act("wait for the upload to complete or click upload button if needed")
            
            # Get the download link or confirmation
            result = nova.act("What is the download link or upload confirmation message?")
            print(f"✅ Upload result: {result.response}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during file upload: {e}")
        return False

def file_download_demo():
    """
    Demo for downloading files from a website
    """
    print("\n📥 Starting File Download Demo")
    print("=" * 35)
    
    try:
        with NovaAct(
            starting_page="https://sample-files.com/zip/10/mp3/mp3-64kbps.zip",
            logs_directory="./demo/logs/file_download"
        ) as nova:
            print("🌐 Navigating to download page...")
            
            # Create downloads directory
            download_dir = "./demo/downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # Method 1: Download via button click
            print("📥 Attempting download via button...")
            
            try:
                with nova.page.expect_download() as download_info:
                    nova.act("click on the download button or link")
                
                # Save the downloaded file
                download_path = os.path.join(download_dir, "downloaded_file.zip")
                download_info.value.save_as(download_path)
                
                print(f"✅ File downloaded successfully to: {download_path}")
                print(f"📊 File size: {os.path.getsize(download_path)} bytes")
                
                return True
                
            except Exception as e:
                print(f"⚠️ Button download failed: {e}")
                
                # Method 2: Direct download using page request
                print("📥 Attempting direct download...")
                
                response = nova.page.request.get(nova.page.url)
                download_path = os.path.join(download_dir, "direct_download.zip")
                
                with open(download_path, "wb") as f:
                    f.write(response.body())
                
                print(f"✅ Direct download successful to: {download_path}")
                print(f"📊 File size: {os.path.getsize(download_path)} bytes")
                
                return True
                
    except Exception as e:
        print(f"❌ Error during file download: {e}")
        return False

def pdf_download_demo():
    """
    Demo for downloading PDF files
    """
    print("\n📄 Starting PDF Download Demo")
    print("=" * 35)
    
    try:
        with NovaAct(
            starting_page="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            logs_directory="./demo/logs/pdf_download"
        ) as nova:
            print("📄 Downloading PDF file...")
            
            # Create downloads directory
            download_dir = "./demo/downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # Download the PDF using page request
            response = nova.page.request.get(nova.page.url)
            pdf_path = os.path.join(download_dir, "sample.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(response.body())
            
            print(f"✅ PDF downloaded successfully to: {pdf_path}")
            print(f"📊 File size: {os.path.getsize(pdf_path)} bytes")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during PDF download: {e}")
        return False

def html_content_save_demo():
    """
    Demo for saving HTML content from web pages
    """
    print("\n💾 Starting HTML Content Save Demo")
    print("=" * 40)
    
    try:
        with NovaAct(
            starting_page="https://example.com",
            logs_directory="./demo/logs/html_save"
        ) as nova:
            print("🌐 Loading web page...")
            
            # Get the rendered DOM content
            html_content = nova.page.content()
            
            # Save to file
            save_dir = "./demo/saved_content"
            os.makedirs(save_dir, exist_ok=True)
            
            html_path = os.path.join(save_dir, "example_page.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"✅ HTML content saved to: {html_path}")
            print(f"📊 Content length: {len(html_content)} characters")
            
            # Also save page screenshot
            screenshot_path = os.path.join(save_dir, "example_page.png")
            nova.page.screenshot(path=screenshot_path)
            
            print(f"📸 Screenshot saved to: {screenshot_path}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error saving HTML content: {e}")
        return False

def bulk_file_operations_demo():
    """
    Demo for handling multiple file operations
    """
    print("\n📦 Starting Bulk File Operations Demo")
    print("=" * 45)
    
    # Create multiple sample files
    sample_files = create_sample_files()
    
    try:
        with NovaAct(
            starting_page="https://file.io/",
            logs_directory="./demo/logs/bulk_operations"
        ) as nova:
            print("📤 Performing bulk file uploads...")
            
            upload_results = []
            
            for file_type, file_path in sample_files.items():
                try:
                    print(f"📄 Uploading {file_type} file: {os.path.basename(file_path)}")
                    
                    # Navigate back to upload page for each file
                    nova.go_to_url("https://file.io/")
                    
                    # Upload file
                    nova.page.set_input_files('input[type="file"]', file_path)
                    
                    # Wait for upload
                    nova.act("wait for upload to complete")
                    
                    # Get result
                    result = nova.act("What is the upload status or download link?")
                    
                    upload_results.append({
                        "file_type": file_type,
                        "file_name": os.path.basename(file_path),
                        "result": result.response
                    })
                    
                    print(f"✅ {file_type} upload completed")
                    
                except Exception as e:
                    print(f"❌ Error uploading {file_type} file: {e}")
                    upload_results.append({
                        "file_type": file_type,
                        "file_name": os.path.basename(file_path),
                        "error": str(e)
                    })
            
            # Summary
            print("\n📊 Bulk Upload Results:")
            print("=" * 25)
            
            successful = 0
            for result in upload_results:
                if "error" not in result:
                    print(f"✅ {result['file_type']}: {result['file_name']}")
                    successful += 1
                else:
                    print(f"❌ {result['file_type']}: {result['error']}")
            
            print(f"\n📈 Success rate: {successful}/{len(upload_results)} files")
            
            return upload_results
            
    except Exception as e:
        print(f"❌ Error during bulk operations: {e}")
        return []

def file_validation_demo():
    """
    Demo for validating file operations
    """
    print("\n✅ Starting File Validation Demo")
    print("=" * 40)
    
    sample_files = create_sample_files()
    
    # Validate sample files exist and have content
    print("🔍 Validating sample files...")
    
    for file_type, file_path in sample_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_type} file: {os.path.basename(file_path)} ({file_size} bytes)")
        else:
            print(f"❌ {file_type} file not found: {file_path}")
    
    # Validate downloads directory
    download_dir = "./demo/downloads"
    if os.path.exists(download_dir):
        downloaded_files = os.listdir(download_dir)
        print(f"\n📥 Downloaded files ({len(downloaded_files)}):")
        for file_name in downloaded_files:
            file_path = os.path.join(download_dir, file_name)
            file_size = os.path.getsize(file_path)
            print(f"  📄 {file_name} ({file_size} bytes)")
    else:
        print("\n📥 No downloads directory found")
    
    return True

def main():
    """Main function to run all file operation demos"""
    print("Nova Act File Operations Demo Suite")
    print("===================================")
    
    # Check for API key
    if not os.getenv('NOVA_ACT_API_KEY'):
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        print("   export NOVA_ACT_API_KEY='your_api_key'")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("./demo/logs", exist_ok=True)
    os.makedirs("./demo/downloads", exist_ok=True)
    os.makedirs("./demo/saved_content", exist_ok=True)
    
    print("\n📁 File Operations Demo Options:")
    print("1. File upload demonstration")
    print("2. File download demonstration")
    print("3. PDF download demonstration")
    print("4. HTML content save demonstration")
    print("5. Bulk file operations demonstration")
    print("6. File validation demonstration")
    print("7. Run all demos")
    
    choice = input("\nSelect demo (1-7): ").strip()
    
    if choice == "1":
        file_upload_demo()
    elif choice == "2":
        file_download_demo()
    elif choice == "3":
        pdf_download_demo()
    elif choice == "4":
        html_content_save_demo()
    elif choice == "5":
        bulk_file_operations_demo()
    elif choice == "6":
        file_validation_demo()
    elif choice == "7":
        # Run all demos
        results = []
        results.append(file_upload_demo())
        results.append(file_download_demo())
        results.append(pdf_download_demo())
        results.append(html_content_save_demo())
        results.append(bulk_file_operations_demo())
        results.append(file_validation_demo())
        
        successful = sum(1 for result in results if result)
        total = len(results)
        
        print(f"\n📊 File Operations Demo Summary: {successful}/{total} successful")
        
        if successful == total:
            print("🎉 All file operation demos completed successfully!")
        else:
            print("⚠️ Some demos encountered issues. Check the logs for details.")
    else:
        print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
