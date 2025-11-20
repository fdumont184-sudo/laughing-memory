#!/usr/bin/env python3
"""
Lightning Fast File/Folder Search Script
Searches for files and folders using a single keyword across your system
"""

import os
import sys
import argparse
import time
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch

class FastFileSearch:
    def __init__(self, keyword, search_paths=None, max_results=100, case_sensitive=False):
        self.keyword = keyword if case_sensitive else keyword.lower()
        self.search_paths = search_paths or [str(Path.home())]  # Default to home directory
        self.max_results = max_results
        self.case_sensitive = case_sensitive
        self.results = []
        self.lock = threading.Lock()
        self.stop_search = threading.Event()

    def matches_keyword(self, name):
        """Check if a filename/directory name matches the keyword"""
        target = name if self.case_sensitive else name.lower()
        return self.keyword in target

    def search_in_directory(self, directory):
        """Search for files/folders in a single directory"""
        if self.stop_search.is_set():
            return []
        
        local_results = []
        
        try:
            for root, dirs, files in os.walk(directory, onerror=lambda e: None):
                if self.stop_search.is_set():
                    break
                    
                # Check directories
                for d in dirs:
                    if self.matches_keyword(d):
                        full_path = os.path.join(root, d)
                        local_results.append(('directory', full_path))
                
                # Check files
                for f in files:
                    if self.matches_keyword(f):
                        full_path = os.path.join(root, f)
                        local_results.append(('file', full_path))
                
                # Limit results to prevent excessive memory usage
                if len(local_results) >= self.max_results:
                    break
        except PermissionError:
            # Skip directories we don't have permission to access
            pass
        except Exception:
            # Skip any problematic directories
            pass
        
        return local_results

    def search(self, max_workers=4, timeout=30):
        """Perform the search across all specified paths"""
        print(f"🔍 Searching for '{self.keyword}' in {len(self.search_paths)} location(s)...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit search tasks for each path
            future_to_path = {
                executor.submit(self.search_in_directory, path): path 
                for path in self.search_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path, timeout=timeout):
                if self.stop_search.is_set():
                    break
                    
                try:
                    results = future.result()
                    with self.lock:
                        self.results.extend(results)
                        if len(self.results) >= self.max_results:
                            self.stop_search.set()
                            break
                except Exception:
                    # Skip problematic searches
                    continue
        
        end_time = time.time()
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        
        return self.results[:self.max_results]

def main():
    parser = argparse.ArgumentParser(
        description="Lightning Fast File/Folder Search - Find anything with a single keyword!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fast_file_search.py documents          # Search for files/folders containing 'documents'
  python fast_file_search.py report -p / /tmp  # Search in root and temp directories
  python fast_file_search.py image -m 50       # Find up to 50 items containing 'image'
  python fast_file_search.py PDF --case        # Case-sensitive search for 'PDF'
        """
    )
    
    parser.add_argument('keyword', help='The keyword to search for in filenames and directory names')
    parser.add_argument('-p', '--paths', nargs='+', default=None, 
                       help='Directories to search in (default: home directory)')
    parser.add_argument('-m', '--max-results', type=int, default=100,
                       help='Maximum number of results to return (default: 100)')
    parser.add_argument('--case', action='store_true', 
                       help='Case-sensitive search (default: case-insensitive)')
    parser.add_argument('--system', action='store_true',
                       help='Search in system directories (requires appropriate permissions)')
    
    args = parser.parse_args()
    
    # Determine search paths
    search_paths = args.paths
    if not search_paths:
        search_paths = [str(Path.home())]
    
    if args.system:
        # Add common system directories (adjust as needed for your system)
        system_paths = ['/home', '/opt', '/usr', '/var', '/tmp']
        search_paths.extend(system_paths)
    
    # Remove duplicates while preserving order
    search_paths = list(dict.fromkeys(search_paths))
    
    # Validate search paths exist
    valid_paths = []
    for path in search_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"⚠️  Warning: Path '{path}' does not exist, skipping...")
    
    if not valid_paths:
        print("❌ No valid search paths provided!")
        sys.exit(1)
    
    # Perform the search
    searcher = FastFileSearch(
        keyword=args.keyword,
        search_paths=valid_paths,
        max_results=args.max_results,
        case_sensitive=args.case
    )
    
    try:
        results = searcher.search()
        
        # Display results
        if results:
            print(f"\n🎯 Found {len(results)} result(s) for keyword '{args.keyword}':\n")
            for i, (ftype, path) in enumerate(results, 1):
                icon = "📁" if ftype == 'directory' else "📄"
                print(f"{i:3d}. {icon} {path}")
        else:
            print(f"\n📭 No results found for keyword '{args.keyword}'")
    
    except KeyboardInterrupt:
        print("\n🛑 Search interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()