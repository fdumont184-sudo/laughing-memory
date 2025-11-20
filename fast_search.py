#!/usr/bin/env python3
"""
Ultra-fast file/folder search utility with storage bloat test feature
"""

import os
import sys
import argparse
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from pathlib import Path


class FastSearch:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.total_searched = 0
    
    def search_in_directory(self, directory, keyword, case_sensitive=False):
        """Search for files/directories in a single directory"""
        local_results = []
        
        try:
            for entry in os.scandir(directory):
                self.total_searched += 1
                
                # Check if entry name matches keyword
                name = entry.name
                if not case_sensitive:
                    name = name.lower()
                    search_keyword = keyword.lower()
                else:
                    search_keyword = keyword
                
                if search_keyword in name:
                    local_results.append({
                        'path': entry.path,
                        'type': 'directory' if entry.is_dir() else 'file',
                        'size': entry.stat().st_size if entry.is_file() else 0
                    })
                
                # If it's a directory, continue searching inside (but don't recurse here for speed)
                # We'll let the thread pool handle different directories
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        # Add results safely with lock
        with self.lock:
            self.results.extend(local_results)
        
        return len(local_results)
    
    def search(self, paths, keyword, max_results=None, case_sensitive=False, max_workers=16):
        """Perform fast search across multiple paths"""
        print(f"🔍 Searching for '{keyword}' in {len(paths)} paths with {max_workers} threads...")
        
        # Collect all directories to search
        all_dirs = []
        for path in paths:
            if os.path.isdir(path):
                all_dirs.append(path)
                # Add subdirectories to search
                try:
                    for root, dirs, files in os.walk(path):
                        # Add all subdirectories
                        for d in dirs:
                            all_dirs.append(os.path.join(root, d))
                except (PermissionError, OSError):
                    continue
            elif os.path.isfile(path):
                # Check if the single file matches
                if keyword.lower() in os.path.basename(path).lower():
                    self.results.append({
                        'path': path,
                        'type': 'file',
                        'size': os.path.getsize(path)
                    })
        
        # Remove duplicates
        all_dirs = list(set(all_dirs))
        
        # Use ThreadPoolExecutor for maximum speed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for directory in all_dirs:
                future = executor.submit(self.search_in_directory, directory, keyword, case_sensitive)
                futures.append(future)
            
            # Wait for all searches to complete
            for future in as_completed(futures):
                pass  # Results are already added to self.results
        
        # Apply max_results limit
        if max_results:
            self.results = self.results[:max_results]
        
        return self.results
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}PB"
    
    def print_results(self, results):
        """Print search results in a clean format"""
        if not results:
            print("❌ No results found.")
            return
        
        print(f"\n🎯 Found {len(results)} result(s):")
        print("-" * 80)
        
        for result in results:
            size_str = self.format_size(result['size']) if result['type'] == 'file' else "[DIR]"
            print(f"{result['type'].upper()[0]} {size_str:>8} │ {result['path']}")


def create_bloat_file():
    """Create a file that fills all available storage space"""
    print("💾 Starting storage health test...")
    
    # Get available disk space
    total, used, free = shutil.disk_usage(".")
    print(f"📊 Disk info - Total: {total//1024//1024}MB, Used: {used//1024//1024}MB, Free: {free//1024//1024}MB")
    
    # Create bloat file
    bloat_filename = "TEMP_STORAGE_TEST_FILE_DO_NOT_USE"
    chunk_size = 1024 * 1024 * 100  # 100MB chunks
    written = 0
    
    print("⚡ Creating bloating file...")
    
    try:
        with open(bloat_filename, "wb") as f:
            while True:
                # Write in chunks to avoid memory issues
                try:
                    # Create a large chunk of zeros
                    chunk = b'\0' * min(chunk_size, free - written)
                    if not chunk:
                        break
                    f.write(chunk)
                    written += len(chunk)
                    
                    # Show progress
                    if written % (chunk_size * 10) == 0:  # Every 1GB
                        print(f"📝 Written: {written//1024//1024}MB")
                    
                    # Check if we're approaching disk limit
                    current_free = shutil.disk_usage(".")[2]
                    if current_free < chunk_size:
                        break
                        
                except OSError:
                    # Disk is full
                    break
    except Exception as e:
        print(f"⚠️ Error during bloat: {e}")
    
    # Check final status
    final_free = shutil.disk_usage(".")[2]
    print(f"\n📈 Final disk status - Free space: {final_free} bytes")
    
    if final_free < 1024 * 1024:  # Less than 1MB free
        print("✅ Storage is healthy - successfully filled to capacity!")
    else:
        print("⚠️ Storage test incomplete - still has space available")
    
    # Auto-delete the bloat file
    print("🧹 Cleaning up...")
    try:
        os.remove(bloat_filename)
        print("✅ Bloated file auto-deleted successfully!")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ Could not delete bloat file: {e}")
    
    print("✅ Storage health test completed!")


def main():
    parser = argparse.ArgumentParser(
        description="Ultra-fast file/folder search with storage health test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fast_search.py search documents                    # Search for 'documents' in home
  python fast_search.py search image -p /home /tmp        # Search in specific paths
  python fast_search.py search report -m 20               # Limit to 20 results
  python fast_search.py bloat                             # Run storage health test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for files/directories')
    search_parser.add_argument('keyword', help='Search keyword')
    search_parser.add_argument('-p', '--paths', nargs='+', default=[os.path.expanduser('~')], 
                              help='Paths to search in (default: home directory)')
    search_parser.add_argument('-m', '--max-results', type=int, help='Maximum number of results')
    search_parser.add_argument('--case', action='store_true', help='Case sensitive search')
    
    # Bloat command
    bloat_parser = subparsers.add_parser('bloat', help='Create bloated file to test storage')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        start_time = time.time()
        
        searcher = FastSearch()
        results = searcher.search(
            paths=args.paths,
            keyword=args.keyword,
            max_results=args.max_results,
            case_sensitive=args.case
        )
        
        end_time = time.time()
        
        searcher.print_results(results)
        print(f"\n⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔍 Total items searched: {searcher.total_searched}")
        
    elif args.command == 'bloat':
        create_bloat_file()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()