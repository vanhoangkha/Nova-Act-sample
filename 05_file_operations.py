#!/usr/bin/env python3
"""
Nova Act Demo: Enhanced File Operations
======================================

This demo shows how to handle file uploads, downloads, and file management
operations with Nova Act, including error handling and validation.
"""

import os
import sys
import time
import tempfile
import shutil
from typing import Dict, Any, List
from pathlib import Path
from nova_act import NovaAct

# Import our enhanced framework
from demo_framework import BaseDemo, DemoResult


class FileOperationsDemo(BaseDemo):
    """Enhanced file operations demo with validation and error handling."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.steps_total = 6  # Setup, Create test files, Upload test, Download test, File validation, Cleanup
        self.test_files_dir = "./demo/test_files"
        self.downloads_dir = "./demo/downloads"
        
    def setup(self) -> bool:
        """Setup demo environment and validate prerequisites."""
        self.logger.info("Setting up File Operations Demo")
        
        # Check API key
        if not os.getenv('NOVA_ACT_API_KEY'):
            self.logger.error("NOVA_ACT_API_KEY environment variable not set")
            return False
        
        # Create required directories
        os.makedirs(self.test_files_dir, exist_ok=True)
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        self.logger.info(f"Test files directory: {self.test_files_dir}")
        self.logger.info(f"Downloads directory: {self.downloads_dir}")
        
        return True
    
    def get_fallback_sites(self) -> List[str]:
        """Get fallback sites for file operations."""
        return [
            "https://httpbin.org/forms/post",
            "https://file.io",
            "https://example.com"
        ]
    
    def execute_steps(self) -> Dict[str, Any]:
        """Execute the main demo steps."""
        extracted_data = {}
        
        try:
            # Step 1: Create test files
            test_files = self._step_create_test_files()
            extracted_data.update(test_files)
            self.increment_step("Test files creation completed")
            
            # Step 2: Choose file operation site
            site_info = self._step_choose_file_site()
            extracted_data.update(site_info)
            self.increment_step("File operation site selection completed")
            
            # Step 3: Test file upload
            upload_result = self._step_test_upload(site_info["target_site"], test_files["created_files"])
            extracted_data.update(upload_result)
            self.increment_step("File upload test completed")
            
            # Step 4: Test file download
            download_result = self._step_test_download(site_info["target_site"])
            extracted_data.update(download_result)
            self.increment_step("File download test completed")
            
            # Step 5: Validate file operations
            validation_result = self._step_validate_operations(test_files["created_files"])
            extracted_data.update(validation_result)
            self.increment_step("File operations validation completed")
            
            # Step 6: Cleanup test files
            cleanup_result = self._step_cleanup_files(test_files["created_files"])
            extracted_data.update(cleanup_result)
            self.increment_step("File cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during file operations: {str(e)}")
            raise
        
        return extracted_data
    
    def _step_create_test_files(self) -> Dict[str, Any]:
        """Step 1: Create test files for upload operations."""
        self.logger.log_step(1, "Test Files Creation", "starting")
        
        created_files = []
        
        try:
            # Create a text file
            text_file = os.path.join(self.test_files_dir, "test_document.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write("This is a test document for Nova Act file operations demo.\n")
                f.write(f"Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("This file demonstrates text file upload capabilities.\n")
            created_files.append(text_file)
            
            # Create a small CSV file
            csv_file = os.path.join(self.test_files_dir, "test_data.csv")
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("Name,Age,City\n")
                f.write("John Doe,30,New York\n")
                f.write("Jane Smith,25,Los Angeles\n")
                f.write("Bob Johnson,35,Chicago\n")
            created_files.append(csv_file)
            
            # Create a small JSON file
            json_file = os.path.join(self.test_files_dir, "test_config.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write('{\n')
                f.write('  "demo_name": "Nova Act File Operations",\n')
                f.write('  "version": "1.0",\n')
                f.write(f'  "created": "{time.strftime("%Y-%m-%d %H:%M:%S")}",\n')
                f.write('  "test_mode": true\n')
                f.write('}\n')
            created_files.append(json_file)
            
            # Validate created files
            file_info = []
            for file_path in created_files:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    file_info.append({
                        "path": file_path,
                        "name": os.path.basename(file_path),
                        "size": stat.st_size,
                        "created": True
                    })
                    self.logger.info(f"✅ Created {os.path.basename(file_path)} ({stat.st_size} bytes)")
                else:
                    self.logger.error(f"❌ Failed to create {file_path}")
            
            self.logger.log_step(1, "Test Files Creation", "completed", f"Created {len(file_info)} files")
            self.logger.log_data_extraction("test_files", {"files": file_info}, "file_creation")
            
            return {"created_files": created_files, "file_info": file_info}
            
        except Exception as e:
            self.logger.log_step(1, "Test Files Creation", "failed", str(e))
            return {"created_files": [], "creation_error": str(e)}
    
    def _step_choose_file_site(self) -> Dict[str, Any]:
        """Step 2: Choose appropriate site for file operations."""
        self.logger.log_step(2, "File Site Selection", "starting")
        
        # Sites that support file operations
        file_sites = [
            {
                "url": "https://httpbin.org/forms/post",
                "name": "HTTPBin Form",
                "supports_upload": True,
                "supports_download": False,
                "type": "form_demo"
            },
            {
                "url": "https://file.io",
                "name": "File.io",
                "supports_upload": True,
                "supports_download": True,
                "type": "file_sharing"
            }
        ]
        
        # Choose first accessible site
        target_site = None
        for site in file_sites:
            if self.config_manager.validate_site_access(site["url"]):
                target_site = site
                break
        
        if not target_site:
            # Use fallback
            fallback_sites = self.get_fallback_sites()
            target_site = {
                "url": fallback_sites[0],
                "name": "Fallback Site",
                "supports_upload": True,
                "supports_download": False,
                "type": "fallback"
            }
            self.add_warning("Using fallback site for file operations")
        
        self.logger.log_step(2, "File Site Selection", "completed", f"Selected {target_site['name']}")
        self.logger.log_data_extraction("target_site", target_site, "site_selection")
        
        return {"target_site": target_site}
    
    def _step_test_upload(self, site_info: Dict[str, Any], test_files: List[str]) -> Dict[str, Any]:
        """Step 3: Test file upload functionality."""
        self.logger.log_step(3, "File Upload Test", "starting")
        
        if not site_info.get("supports_upload", False):
            self.logger.log_step(3, "File Upload Test", "skipped", "Site doesn't support upload")
            return {"upload_test": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/file_upload"
            ) as nova:
                
                upload_results = []
                
                if site_info.get("type") == "form_demo":
                    # Handle HTTPBin form upload
                    upload_result = self._handle_form_upload(nova, test_files[0])  # Upload first file
                    upload_results.append(upload_result)
                    
                elif site_info.get("type") == "file_sharing":
                    # Handle file sharing service
                    for file_path in test_files[:2]:  # Upload first 2 files
                        upload_result = self._handle_file_sharing_upload(nova, file_path)
                        upload_results.append(upload_result)
                        time.sleep(1)  # Brief pause between uploads
                
                else:
                    # Generic upload handling
                    upload_result = self._handle_generic_upload(nova, test_files[0])
                    upload_results.append(upload_result)
                
                successful_uploads = len([r for r in upload_results if r.get("success", False)])
                
                self.logger.log_step(3, "File Upload Test", "completed", 
                                   f"{successful_uploads}/{len(upload_results)} uploads successful")
                
                return {"upload_test": {"results": upload_results, "successful_count": successful_uploads}}
                
        except Exception as e:
            self.logger.log_step(3, "File Upload Test", "failed", str(e))
            return {"upload_test": {"failed": True, "error": str(e)}}
    
    def _handle_form_upload(self, nova, file_path: str) -> Dict[str, Any]:
        """Handle form-based file upload."""
        try:
            # Look for file input
            nova.act("look for a file upload input or browse button")
            
            # Use Playwright to set the file
            nova.page.set_input_files('input[type="file"]', file_path)
            
            # Fill other form fields if present
            nova.act("if there are other form fields, fill them with test data")
            
            # For demo safety, don't actually submit
            self.add_warning("File selected but form not submitted for demo safety")
            
            return {
                "success": True,
                "method": "form_upload",
                "file": os.path.basename(file_path),
                "submitted": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "method": "form_upload",
                "file": os.path.basename(file_path),
                "error": str(e)
            }
    
    def _handle_file_sharing_upload(self, nova, file_path: str) -> Dict[str, Any]:
        """Handle file sharing service upload."""
        try:
            # Look for upload area
            nova.act("look for an upload area, drag and drop zone, or upload button")
            
            # Try to find file input
            file_inputs = nova.page.query_selector_all('input[type="file"]')
            if file_inputs:
                file_inputs[0].set_input_files(file_path)
                
                # Wait for upload to process
                nova.act("wait for the upload to complete or show progress")
                
                return {
                    "success": True,
                    "method": "file_sharing",
                    "file": os.path.basename(file_path),
                    "uploaded": True
                }
            else:
                return {
                    "success": False,
                    "method": "file_sharing",
                    "file": os.path.basename(file_path),
                    "error": "No file input found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "file_sharing",
                "file": os.path.basename(file_path),
                "error": str(e)
            }
    
    def _handle_generic_upload(self, nova, file_path: str) -> Dict[str, Any]:
        """Handle generic file upload."""
        try:
            # Generic approach
            nova.act("look for any file upload functionality on this page")
            
            # Try to find and use file input
            try:
                nova.page.set_input_files('input[type="file"]', file_path)
                success = True
            except:
                success = False
            
            return {
                "success": success,
                "method": "generic_upload",
                "file": os.path.basename(file_path),
                "note": "Generic upload attempt"
            }
            
        except Exception as e:
            return {
                "success": False,
                "method": "generic_upload",
                "file": os.path.basename(file_path),
                "error": str(e)
            }
    
    def _step_test_download(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Test file download functionality."""
        self.logger.log_step(4, "File Download Test", "starting")
        
        if not site_info.get("supports_download", False):
            self.logger.log_step(4, "File Download Test", "skipped", "Site doesn't support download")
            return {"download_test": {"skipped": True, "reason": "not_supported"}}
        
        try:
            with NovaAct(
                starting_page=site_info["url"],
                logs_directory="./demo/logs/file_download"
            ) as nova:
                
                download_results = []
                
                # Look for downloadable content
                nova.act("look for any downloadable files or download links")
                
                # Try to download using Playwright
                try:
                    with nova.page.expect_download() as download_info:
                        nova.act("click on a download link or button if available")
                    
                    # Save the downloaded file
                    download_path = os.path.join(self.downloads_dir, "downloaded_file")
                    download_info.value.save_as(download_path)
                    
                    download_results.append({
                        "success": True,
                        "method": "playwright_download",
                        "saved_path": download_path,
                        "size": os.path.getsize(download_path) if os.path.exists(download_path) else 0
                    })
                    
                except Exception as e:
                    # Try alternative download method
                    try:
                        # Download current page content
                        content = nova.page.content()
                        download_path = os.path.join(self.downloads_dir, "page_content.html")
                        with open(download_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        download_results.append({
                            "success": True,
                            "method": "page_content",
                            "saved_path": download_path,
                            "size": os.path.getsize(download_path)
                        })
                        
                    except Exception as e2:
                        download_results.append({
                            "success": False,
                            "method": "failed",
                            "error": str(e2)
                        })
                
                successful_downloads = len([r for r in download_results if r.get("success", False)])
                
                self.logger.log_step(4, "File Download Test", "completed", 
                                   f"{successful_downloads} downloads successful")
                
                return {"download_test": {"results": download_results, "successful_count": successful_downloads}}
                
        except Exception as e:
            self.logger.log_step(4, "File Download Test", "failed", str(e))
            return {"download_test": {"failed": True, "error": str(e)}}
    
    def _step_validate_operations(self, test_files: List[str]) -> Dict[str, Any]:
        """Step 5: Validate file operations."""
        self.logger.log_step(5, "File Operations Validation", "starting")
        
        validation_results = {
            "test_files_exist": [],
            "download_files_exist": [],
            "file_integrity_checks": []
        }
        
        # Check test files still exist
        for file_path in test_files:
            exists = os.path.exists(file_path)
            validation_results["test_files_exist"].append({
                "file": os.path.basename(file_path),
                "exists": exists,
                "size": os.path.getsize(file_path) if exists else 0
            })
        
        # Check downloaded files
        if os.path.exists(self.downloads_dir):
            for file_name in os.listdir(self.downloads_dir):
                file_path = os.path.join(self.downloads_dir, file_name)
                if os.path.isfile(file_path):
                    validation_results["download_files_exist"].append({
                        "file": file_name,
                        "exists": True,
                        "size": os.path.getsize(file_path)
                    })
        
        # Basic integrity checks
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        validation_results["file_integrity_checks"].append({
                            "file": os.path.basename(file_path),
                            "readable": True,
                            "content_length": len(content),
                            "has_content": len(content) > 0
                        })
                except Exception as e:
                    validation_results["file_integrity_checks"].append({
                        "file": os.path.basename(file_path),
                        "readable": False,
                        "error": str(e)
                    })
        
        self.logger.log_step(5, "File Operations Validation", "completed", "Validation checks completed")
        self.logger.log_data_extraction("validation_results", validation_results, "file_validation")
        
        return {"validation": validation_results}
    
    def _step_cleanup_files(self, test_files: List[str]) -> Dict[str, Any]:
        """Step 6: Cleanup test files."""
        self.logger.log_step(6, "File Cleanup", "starting")
        
        cleanup_results = {
            "files_removed": [],
            "directories_cleaned": [],
            "cleanup_errors": []
        }
        
        # Remove test files
        for file_path in test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleanup_results["files_removed"].append(os.path.basename(file_path))
                    self.logger.info(f"✅ Removed {os.path.basename(file_path)}")
            except Exception as e:
                cleanup_results["cleanup_errors"].append({
                    "file": os.path.basename(file_path),
                    "error": str(e)
                })
                self.logger.error(f"❌ Failed to remove {file_path}: {e}")
        
        # Clean up empty directories (optional)
        try:
            if os.path.exists(self.test_files_dir) and not os.listdir(self.test_files_dir):
                os.rmdir(self.test_files_dir)
                cleanup_results["directories_cleaned"].append("test_files")
        except Exception as e:
            cleanup_results["cleanup_errors"].append({
                "directory": "test_files",
                "error": str(e)
            })
        
        self.logger.log_step(6, "File Cleanup", "completed", 
                           f"Removed {len(cleanup_results['files_removed'])} files")
        
        return {"cleanup": cleanup_results}


def run_file_operations_demo():
    """Run the file operations demo."""
    print("📁 Starting Enhanced File Operations Demo")
    print("=" * 50)
    
    # Create demo instance
    demo = FileOperationsDemo()
    
    # Run demo
    result = demo.run()
    
    # Print results
    if result.success:
        print("✅ Demo completed successfully!")
        print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
        print(f"📊 Steps completed: {result.steps_completed}/{result.steps_total}")
        
        if result.data_extracted:
            print("\n📋 File Operations Summary:")
            
            # Test files info
            if "file_info" in result.data_extracted:
                files = result.data_extracted["file_info"]
                print(f"   📄 Test files created: {len(files)}")
                for file_info in files:
                    print(f"      • {file_info['name']} ({file_info['size']} bytes)")
            
            # Upload results
            if "upload_test" in result.data_extracted:
                upload = result.data_extracted["upload_test"]
                if not upload.get("skipped"):
                    successful = upload.get("successful_count", 0)
                    total = len(upload.get("results", []))
                    print(f"   ⬆️  Upload tests: {successful}/{total} successful")
            
            # Download results
            if "download_test" in result.data_extracted:
                download = result.data_extracted["download_test"]
                if not download.get("skipped"):
                    successful = download.get("successful_count", 0)
                    print(f"   ⬇️  Download tests: {successful} successful")
            
            # Cleanup results
            if "cleanup" in result.data_extracted:
                cleanup = result.data_extracted["cleanup"]
                removed = len(cleanup.get("files_removed", []))
                print(f"   🗑️  Files cleaned up: {removed}")
    else:
        print("❌ Demo encountered issues:")
        for error in result.errors:
            print(f"   • {error.error_type}: {error.message}")
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    print(f"📄 Detailed logs: {result.log_path}")
    
    return result


def main():
    """Main function to run the demo."""
    print("Nova Act Enhanced File Operations Demo")
    print("=" * 50)
    
    # Run the demo
    result = run_file_operations_demo()
    
    if result.success:
        print("\n🎉 File operations demo completed successfully!")
        print("This demo showcased:")
        print("  • Test file creation and validation")
        print("  • File upload with multiple strategies")
        print("  • File download and content capture")
        print("  • File integrity checking")
        print("  • Automatic cleanup and resource management")
    else:
        print("\n⚠️ Demo encountered some issues, but this demonstrates:")
        print("  • Robust error handling in file operations")
        print("  • Safe file handling with validation")
        print("  • Graceful degradation when operations fail")
    
    print("\n💡 Production Tips:")
    print("  • Always validate file types and sizes before upload")
    print("  • Implement virus scanning for uploaded files")
    print("  • Use secure file storage with proper permissions")
    print("  • Monitor disk space and implement cleanup policies")
    print("  • Log all file operations for audit trails")


if __name__ == "__main__":
    main()