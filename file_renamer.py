#!/usr/bin/env python3
"""
batch-namer: A CLI tool for batch renaming files using patterns.
Usage examples:
  - Rename all images with a date prefix:
    file_renamer.py --source photos/ --dest photos/ --prefix "IMG_2024-" "*.jpg"
  - Replace filenames with UUIDs:
    file_renamer.py --source temp/ --dest backup/ --uuid "*.py"
"""

import os
import sys
import argparse
import datetime
import uuid
import shutil
from pathlib import Path


def pattern_to_regex(pattern: str) -> str:
    """Convert a glob pattern to regex."""
    # Escape special characters except for the * and ? globs
    regex = ""
    for char in pattern:
        if char == "*":
            regex += "[^/]*"
        elif char == "?":
            regex += "."
        elif char in r"\.^$+={}[]|()<>\\":
            regex += "\\" + char
        else:
            regex += char
    return f"^{regex}$"


def get_files(patterns, directory):
    """Get list of files matching patterns."""
    path = Path(directory)
    files = []
    
    for pattern in patterns:
        expanded = path.glob(pattern)
        files.extend(expanded)
    
    return sorted(files, key=lambda f: f.name.lower())


def rename_with_prefix(files, prefix):
    """Rename files by adding a prefix to their names."""
    for file_path in files:
        new_name = f"{prefix}{file_path.stem}{file_path.suffix}"
        new_path = file_path.parent / new_name
        
        # Handle filename conflicts
        counter = 1
        while new_path.exists():
            name_without_ext = file_path.stem[:-len(file_path.suffix) if file_path.suffix else len(file_path.name)]
            base, ext = os.path.splitext(file_path.name)
            new_name = f"{prefix}{base}_{counter}{ext}"
            new_path = file_path.parent / new_name
            counter += 1
        
        shutil.move(str(file_path), str(new_path))
        print(f"Renamed: {file_path.name} -> {new_name}")


def rename_with_uuid(files):
    """Rename files with unique UUIDs."""
    for file_path in files:
        if file_path.suffix:
            uuid_name = f"{uuid.uuid4().hex[:16]}{file_path.suffix}"
        else:
            uuid_name = f"{uuid.uuid4().hex[:16]}"
        
        new_path = file_path.parent / uuid_name
        
        # Handle filename conflicts
        counter = 1
        while new_path.exists():
            name_without_ext = file_path.stem[:-len(file_path.suffix) if file_path.suffix else len(file_path.name)]
            base, ext = os.path.splitext(file_path.name)
            
            if file_path.suffix:
                uuid_name = f"{uuid.uuid4().hex[:16]}{ext}"
            else:
                uuid_name = f"{uuid.uuid4().hex[:16]}"
            
            new_path = file_path.parent / uuid_name
            counter += 1
        
        shutil.move(str(file_path), str(new_path))
        print(f"Renamed: {file_path.name} -> {uuid_name}")


def rename_with_date(files, date_format="%Y%m%d_%H%M%S"):
    """Rename files with current timestamp."""
    for file_path in files:
        timestamp = datetime.datetime.now().strftime(date_format)
        
        if file_path.suffix:
            new_name = f"{timestamp}{file_path.stem}.{file_path.suffix}"
        else:
            new_name = f"{timestamp}_file"
        
        new_path = file_path.parent / new_name
        
        # Handle filename conflicts
        counter = 1
        while new_path.exists():
            name_without_ext = file_path.stem[:-len(file_path.suffix) if file_path.suffix else len(file_path.name)]
            base, ext = os.path.splitext(file_path.name)
            
            if file_path.suffix:
                new_name = f"{timestamp}{base}.{ext}"
            else:
                new_name = f"{timestamp}_file{counter}"
            
            new_path = file_path.parent / new_name
            counter += 1
        
        shutil.move(str(file_path), str(new_path))
        print(f"Renamed: {file_path.name} -> {new_name}")


def rename_with_sequence(files, start=1):
    """Rename files with sequential numbers."""
    for idx, file_path in enumerate(files, start=start):
        if file_path.suffix:
            new_name = f"{start + idx - 1}{file_path.suffix}"
        else:
            new_name = f"{start + idx - 1}"
        
        new_path = file_path.parent / new_name
        
        # Handle filename conflicts
        counter = start + len(files)
        while new_path.exists():
            name_without_ext = file_path.stem[:-len(file_path.suffix) if file_path.suffix else len(file_path.name)]
            base, ext = os.path.splitext(file_path.name)
            
            if file_path.suffix:
                new_name = f"{counter}{ext}"
            else:
                new_name = str(counter)
            
            new_path = file_path.parent / new_name
            counter += 1
        
        shutil.move(str(file_path), str(new_path))
        print(f"Renamed: {file_path.name} -> {new_name}")


def rename_with_number(files):
    """Replace filename with a number (simple case)."""
    return rename_with_sequence(files)


def main():
    parser = argparse.ArgumentParser(
        description="Batch rename files using patterns and various naming schemes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rename all images with date prefix
  %(prog)s --source photos/ --dest photos/ --prefix "IMG_2024-10-30_120000" "*.jpg"
  
  # Renamed all .py files with UUIDs
  %(prog)s --source /home/user/scripts/ --dest /tmp/ --uuid "*.py"
  
  # Rename docs with sequential numbers
  %(prog)s --source projects/docs/ --dest projects/docs_renamed/ --sequence-docs "*.md"
  """
    )
    
    parser.add_argument("--source", "-s", required=True, help="Source directory or single file")
    parser.add_argument("--dest", "-d", required=True, help="Destination directory (can be same as source)")
    parser.add_argument("--pattern", "-p", required=True, 
                        help="Glob pattern to match files (e.g., '*.jpg', '*.py', '!*.git*')")
    parser.add_argument("--prefix", "-px", metavar="NAME", 
                        help="Add this prefix to filenames (with or without extension)")
    parser.add_argument("--uuid", action="store_true", help="Rename with UUID")
    parser.add_argument("--date", "-dt", metavar="FORMAT", default="%Y%m%d_%H%M%S",
                       help="Use timestamp for naming (format: YYYYMMDD_HHMMSS)")
    parser.add_argument("--number", action="store_true", help="Sequential numbering")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be renamed without making changes")
    
    args = parser.parse_args()
    
    # Validate source directory
    if args.source.endswith('/') or args.source == ".":
        source_dir = Path(args.source.rstrip('/')).resolve()
    else:
        source_dir = Path("./").resolve() / args.source.lstrip('./~')
        
        if not source_dir.is_dir():
            print(f"Error: Source path does not exist or is not a directory: {source_dir}")
            sys.exit(1)
    
    dest_dir = Path(args.dest.rstrip('/')).resolve() if args.dest.endswith('/') else Path(".").resolve() / args.dest.lstrip('./~')
    
    # If dry-run, resolve to absolute paths for accurate display
    if args.dry_run:
        # Get pattern files (for display only in dry-run)
        pattern_files = get_files([args.pattern], source_dir)
        
        if args.prefix:
            prefix = f"{args.prefix}/" if not args.pattern.endswith(".") else args.prefix
            
        if args.uuid:
            print("\n=== UUID Mode (Dry Run) ===")
            for file in pattern_files:
                new_uuid = uuid.uuid4().hex[:16] + file.suffix if file.suffix else uuid.uuid4().hex[:16]
                print(f"  {file.name} -> {new_uuid}")
        elif args.date:
            print("\n=== Date Mode (Dry Run) ===")
            timestamp = datetime.datetime.now().strftime(args.date)
            for file in pattern_files:
                if file.suffix:
                    new_name = f"{timestamp}{file.stem}.{file.suffix}"
                else:
                    new_name = f"{timestamp}_file"
                print(f"  {file.name} -> {new_name}")
        elif args.number:
            print("\n=== Number Mode (Dry Run) ===")
            for idx, file in enumerate(pattern_files, start=1):
                if file.suffix:
                    new_name = f"{idx}{file.suffix}"
                else:
                    new_name = str(idx)
                print(f"  {file.name} -> {new_name}")
        else:
            print("\n=== Prefix Mode (Dry Run) ===")
            for file in pattern_files:
                new_name = f"{args.prefix}{file.stem}{file.suffix}" if args.pattern.endswith(".") else args.prefix + file
                print(f"  {file.name} -> {new_name}")
    else:
        # Dry-run: just show what would be done and skip actual renaming if dry run
        pattern_files = get_files([args.pattern], source_dir)
        
        if not pattern_files:
            print(f"No files found matching pattern '{args.pattern}' in {source_dir}/")
            sys.exit(0)
        
        if args.prefix:
            print(f"\nRenaming {len(pattern_files)} files with prefix: {args.prefix}")
            rename_with_prefix(pattern_files, args.prefix)
        elif args.uuid:
            print(f"\nRenaming {len(pattern_files)} files with UUIDs")
            rename_with_uuid(pattern_files)
        elif args.date:
            print(f"\nRenaming {len(pattern_files)} files with date prefix")
            rename_with_date(pattern_files, args.date)
        elif args.number:
            print(f"\nRenaming {len(pattern_files)} files with sequential numbers")
            rename_with_number(pattern_files)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
