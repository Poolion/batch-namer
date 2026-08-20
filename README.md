# batch-namer

A lightweight CLI tool for batch renaming files using patterns and various naming schemes. Perfect for organizing photo libraries, scripts, or any collection of files that need consistent renaming.

## What It Does

`batch-namer` finds files matching a glob pattern in a directory and renames them using one of four methods:
- **Prefix**: Add a custom prefix to all filenames
- **UUID**: Replace names with unique identifiers
- **Date**: Use current timestamp as a prefix
- **Sequential**: Number files sequentially

## Installation

```bash
# Clone or download this repo
cd batch-namer

# Make executable (Linux/Mac)
chmod +x file_renamer.py

# Add to PATH or run directly
python3 file_renamer.py --help
```

## Usage

Basic syntax:
```bash
file_renamer.py --source <path> --dest <path> --pattern <glob> [options]
```

### Examples

#### Rename all JPGs with a date prefix:
```bash
python3 file_renaner.py --source photos/ --dest photos/ --prefix "IMG_2024-10-30_120000" "*.jpg"
```

#### Replace filenames with UUIDs:
```bash
python3 file_renamer.py --source temp/ --dest backup/ --uuid "*.py"
```

#### Sort documents with sequential numbers:
```bash
python3 file_renamer.py --source projects/docs/ --dest projects/docs_renamed/ --number "*.md"
```

### Options

- `--source, -s`   : Source directory
- `--dest, -d`     : Destination directory (can be same as source)
- `--pattern, -p`  : Glob pattern (e.g., `"*.jpg"`, `"*.py"`)
- `--prefix, -px`  : Add this prefix to filenames
- `--uuid`         : Rename files with UUIDs instead of a prefix
- `--date, -dt`    : Use timestamp (format: YYYYMMDD_HHMMSS)
- `--number`       : Sequential numbering
- `--dry-run, -n`  : Preview changes without renaming

### Dry Run Mode

See exactly what would happen without making changes:
```bash
python3 file_renamer.py --source photos/ --dest photos/ --pattern "*.jpg" --prefix "BACKUP_" --dry-run
```

## Why I Built This

I needed a simple, dependency-free tool to batch rename files without installing heavy dependencies. Existing solutions were either too complex or required Python installations that change system paths. `batch-namer` is a single script you can copy anywhere and run immediately.

It handles common edge cases automatically:
- Skips `.git*`, `.DS_Store`, hidden files when using patterns like `"*.jpg"`
- Prevents filename conflicts by incrementing numbers if needed
- Works on filenames with special characters (spaces, hyphens)
- Safe mode with `--dry-run` to preview changes

## Notable Implementation Details

The tool uses glob-to-regex conversion for pattern matching. The `pattern_to_regex()` function escapes regex-special characters while preserving glob wildcards (`*`, `?`) and excluding directory traversal (`..`).

Conflict resolution happens automatically: if a target filename exists, the app increments a counter rather than overwriting. This prevents data loss even when multiple files get the same name (e.g., after downloading duplicates).

No external dependencies beyond Python 3 standard library. Safe for scripts you drop into any container or shared environment.

## If you find this useful, you can support development: https://www.buymeacoffee.com/poolion
