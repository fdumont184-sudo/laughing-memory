# Lightning Fast File/Folder Search Script

This powerful script searches for files and folders across your system using a single keyword with incredible speed! It's designed to find what you're looking for as fast as the "speed of light" - utilizing parallel processing and optimized search algorithms.

## Features

- ⚡ **Lightning fast** - Uses multi-threading for rapid search
- 🔍 **Keyword-based** - Find files/folders with just one keyword
- 📁 **Both files and folders** - Searches for both files and directories
- 🌐 **System-wide** - Can search across your entire system
- 🛡️ **Safe** - Handles permissions gracefully, skips inaccessible directories
- 🎯 **Flexible** - Case-sensitive or case-insensitive search
- ⏱️ **Fast** - Optimized to return results in seconds

## Installation

The script is ready to use in this directory. Just make sure you have Python 3 installed.

## Usage

### Basic Usage
```bash
./fastfind <keyword>
```

### Advanced Usage
```bash
# Search in specific paths
./fastfind documents -p /home /tmp

# Limit results
./fastfind report -m 50

# Case-sensitive search
./fastfind PDF --case

# Search system directories too (requires permissions)
./fastfind config --system

# Help
./fastfind
```

## Examples

```bash
# Find all files/folders containing "documents"
./fastfind documents

# Find up to 25 items containing "project" in your home and documents folders
./fastfind project -p /home/user /home/user/Documents -m 25

# Case-sensitive search for "Python" (not "python")
./fastfind Python --case

# Search across system directories for "config" files
./fastfind config --system
```

## How It Works

1. **Parallel Processing**: The script uses multiple threads to search different directories simultaneously
2. **Optimized Walking**: Uses `os.walk()` with error handling for maximum efficiency
3. **Early Termination**: Stops searching once maximum results are found
4. **Memory Efficient**: Limits results to prevent excessive memory usage
5. **Permission Safe**: Gracefully skips directories without read permissions

## Files Included

- `fast_file_search.py` - Main Python script with all search functionality
- `fastfind` - Bash wrapper for easier execution
- `README.md` - This documentation file

## Requirements

- Python 3.6+
- Standard Python libraries (no external dependencies)

## Performance Tips

- For fastest results, specify specific directories instead of searching system-wide
- Use case-sensitive search if you know the exact case
- Limit the number of results if you only need a few matches
- The script automatically stops when it finds the maximum number of results

## Customization

You can modify the script to:
- Change default search paths
- Adjust the number of worker threads
- Modify the maximum search timeout
- Add custom file filters
