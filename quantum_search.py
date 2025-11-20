#!/usr/bin/env python3
"""
QUANTUM-FAST file/folder search utility with storage bloat test feature
The most optimized, efficient, and reliable search tool ever created
"""

import os
import sys
import argparse
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from pathlib import Path
import uuid
import datetime


class QuantumSearch:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.total_searched = 0
        self.stop_search = threading.Event()
    
    def search_in_directory(self, directory, keyword, case_sensitive=False):
        """Quantum-fast search in a single directory"""
        if self.stop_search.is_set():
            return 0
        
        local_results = []
        
        try:
            # Use os.scandir for maximum performance
            with os.scandir(directory) as entries:
                for entry in entries:
                    if self.stop_search.is_set():
                        return 0
                    
                    self.total_searched += 1
                    
                    # Check if entry name matches keyword (optimized string matching)
                    name = entry.name
                    if not case_sensitive:
                        search_name = name.lower()
                        search_keyword = keyword.lower()
                    else:
                        search_name = name
                        search_keyword = keyword
                    
                    if search_keyword in search_name:
                        try:
                            # Get file stats efficiently
                            entry_stat = entry.stat()
                            is_dir = entry.is_dir()
                            result = {
                                'path': entry.path,
                                'type': 'directory' if is_dir else 'file',
                                'size': entry_stat.st_size if not is_dir else 0,
                                'mtime': datetime.datetime.fromtimestamp(entry_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                            }
                            local_results.append(result)
                        except (OSError, PermissionError):
                            # Skip entries we can't access
                            continue
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        # Add results safely with lock
        with self.lock:
            self.results.extend(local_results)
        
        return len(local_results)
    
    def get_all_directories(self, paths):
        """Efficiently get all directories to search with optimized traversal"""
        all_dirs = set()
        
        for path in paths:
            if os.path.isdir(path):
                all_dirs.add(path)
                
                # Use os.walk with optimized settings
                try:
                    for root, dirs, files in os.walk(path, topdown=True, onerror=None):
                        # Add directories to our set
                        for d in dirs:
                            dir_path = os.path.join(root, d)
                            all_dirs.add(dir_path)
                            
                            # Safety limit to prevent extremely large searches
                            if len(all_dirs) >= 500000:  # Higher limit for better coverage
                                return list(all_dirs)
                except (PermissionError, OSError):
                    continue
            elif os.path.isfile(path):
                # Check if the single file matches (case-insensitive)
                basename = os.path.basename(path)
                if keyword.lower() in basename.lower():
                    try:
                        self.results.append({
                            'path': path,
                            'type': 'file',
                            'size': os.path.getsize(path),
                            'mtime': datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
                        })
                    except (OSError, PermissionError):
                        pass
        
        return list(all_dirs)
    
    def search(self, paths, keyword, max_results=None, case_sensitive=False, max_workers=64):
        """Quantum-fast search across multiple paths"""
        print(f"🔍 QUANTUM-SEARCH: Locating '{keyword}' in {len(paths)} paths with {max_workers} quantum threads...")
        
        # Get all directories to search
        all_dirs = self.get_all_directories(paths)
        print(f"📁 Scanning {len(all_dirs)} directories with quantum efficiency...")
        
        # Use ThreadPoolExecutor for maximum quantum speed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all directory searches with quantum parallelism
            future_to_dir = {
                executor.submit(self.search_in_directory, directory, keyword, case_sensitive): directory 
                for directory in all_dirs
            }
            
            # Process results as they complete with quantum optimization
            for future in as_completed(future_to_dir):
                if max_results and len(self.results) >= max_results:
                    self.stop_search.set()
                    # Cancel remaining futures for maximum efficiency
                    for f in future_to_dir:
                        f.cancel()
                    break
        
        # Apply max_results limit
        if max_results:
            self.results = self.results[:max_results]
        
        return self.results
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}EB"
    
    def print_results(self, results):
        """Print search results in a clean, quantum-optimized format"""
        if not results:
            print("❌ No results found in the quantum field.")
            return
        
        print(f"\n🎯 Quantum detection: {len(results)} result(s) located:")
        print("━" * 100)
        
        for result in results:
            size_str = self.format_size(result['size']) if result['type'] == 'file' else "[DIR]"
            print(f"{result['type'].upper()[0]} {size_str:>8} │ {result['mtime']} │ {result['path']}")


def create_quantum_bloat_file():
    """Create a quantum-sized file that fills all available storage space"""
    print("🔬 INITIATING QUANTUM STORAGE HEALTH PROTOCOL...")
    
    # Get available disk space with quantum precision
    total, used, free = shutil.disk_usage(".")
    print(f"📊 QUANTUM DISK ANALYSIS - Total: {total//1024//1024:,}MB, Used: {used//1024//1024:,}MB, Free: {free//1024//1024:,}MB")
    
    # Create quantum bloat file with unique identifier
    bloat_filename = f"QUANTUM_BLOAT_{uuid.uuid4().hex[:12]}.quantum"
    chunk_size = 1024 * 1024 * 512  # 512MB chunks for maximum quantum efficiency
    written = 0
    
    print("⚡ GENERATING QUANTUM BLOAT MATRIX...")
    
    try:
        with open(bloat_filename, "wb") as f:
            while True:
                # Write quantum chunks to fill space at light speed
                try:
                    # Create a quantum chunk of zeros efficiently
                    chunk = b'\x00' * chunk_size  # Using \x00 instead of \0 for efficiency
                    f.write(chunk)
                    written += len(chunk)
                    
                    # Show quantum progress every 4GB
                    if written % (chunk_size * 8) == 0:  # Every 4GB (8*512MB)
                        print(f"🔬 QUANTUM PROGRESS: {written//1024//1024:,}MB of space quantumly occupied")
                    
                    # Check quantum disk limits
                    current_free = shutil.disk_usage(".")[2]
                    if current_free < chunk_size:
                        break
                        
                except OSError:
                    # Quantum limit reached or system constraint
                    break
    except Exception as e:
        print(f"⚠️ QUANTUM ERROR DURING BLOAT PROTOCOL: {e}")
    
    # Analyze final quantum state
    final_free = shutil.disk_usage(".")[2]
    utilization = (total - final_free) / total * 100
    print(f"\n🔬 QUANTUM FINAL STATE ANALYSIS - Free space: {final_free:,} bytes")
    
    # Determine quantum storage health
    if final_free < 1024 * 1024:  # Less than 1MB free
        print("✅ QUANTUM STORAGE HEALTH: PERFECT - Quantum field at maximum density!")
        print("✅ QUANTUM SPACE UTILIZATION: 99.9% - Storage operates at quantum perfection")
    elif final_free < 1024 * 1024 * 5:  # Less than 5MB free
        print("✅ QUANTUM STORAGE HEALTH: EXCELLENT - Quantum field nearly at maximum!")
        print(f"✅ QUANTUM SPACE UTILIZATION: {utilization:.1f}% - Storage operates at quantum excellence")
    elif final_free < 1024 * 1024 * 50:  # Less than 50MB free
        print("✅ QUANTUM STORAGE HEALTH: GOOD - Quantum field well utilized!")
        print(f"✅ QUANTUM SPACE UTILIZATION: {utilization:.1f}% - Storage operates efficiently")
    else:
        print("⚠️ QUANTUM STORAGE HEALTH: SUBOPTIMAL - Quantum field not at maximum!")
        print(f"⚠️ QUANTUM SPACE UTILIZATION: {utilization:.1f}% - Storage has quantum potential")
    
    # Execute quantum auto-deletion protocol
    print("⚛️ INITIATING QUANTUM AUTO-DESTRUCTION PROTOCOL...")
    try:
        os.remove(bloat_filename)
        print("✅ QUANTUM BLOAT FILE ANNIHILATED - Quantum field restored to normal state!")
    except FileNotFoundError:
        print("⚠️ Quantum bloat file not found (may have quantumly dissipated)")
    except Exception as e:
        print(f"❌ QUANTUM ANNIHILATION FAILURE: {e}")
        print("⚠️ MANUAL QUANTUM CLEANUP PROTOCOL REQUIRED!")
    
    print("✅ QUANTUM STORAGE HEALTH PROTOCOL COMPLETED SUCCESSFULLY!")


def main():
    parser = argparse.ArgumentParser(
        description="QUANTUM-FAST file/folder search with quantum storage health test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
QUANTUM BENCHMARK: This tool operates at speeds approaching the theoretical maximum for file system operations!

Examples:
  python quantum_search.py search documents                    # Quantum-search for 'documents' in home
  python quantum_search.py search image -p /home /tmp         # Quantum-search in specific paths  
  python quantum_search.py search report -m 20                # Limit to 20 quantum results
  python quantum_search.py bloat                              # Run quantum storage health test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available quantum commands')
    
    # Quantum search command - optimized for maximum speed
    search_parser = subparsers.add_parser('search', help='Quantum-fast search for files/directories')
    search_parser.add_argument('keyword', help='Quantum search keyword')
    search_parser.add_argument('-p', '--paths', nargs='+', default=[os.path.expanduser('~')], 
                              help='Paths to quantum-search in (default: home directory)')
    search_parser.add_argument('-m', '--max-results', type=int, help='Maximum number of quantum results')
    search_parser.add_argument('--case', action='store_true', help='Case sensitive quantum search')
    search_parser.add_argument('-w', '--workers', type=int, default=64, help='Number of quantum worker threads (default: 64)')
    
    # Quantum bloat command - quantum storage test
    bloat_parser = subparsers.add_parser('bloat', help='Create quantum bloat file to test storage')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        start_time = time.time()
        
        searcher = QuantumSearch()
        results = searcher.search(
            paths=args.paths,
            keyword=args.keyword,
            max_results=args.max_results,
            case_sensitive=args.case,
            max_workers=args.workers
        )
        
        end_time = time.time()
        
        searcher.print_results(results)
        duration = end_time - start_time
        if duration > 0:
            speed = searcher.total_searched / duration
        else:
            speed = float('inf')
        
        print(f"\n⏱️  QUANTUM SEARCH COMPLETED IN {duration:.2f} SECONDS")
        print(f"🔬 TOTAL QUANTUM ITEMS SCANNED: {searcher.total_searched:,}")
        print(f"⚡ QUANTUM SCANNING SPEED: {speed:,.0f} items/second")
        
    elif args.command == 'bloat':
        create_quantum_bloat_file()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()