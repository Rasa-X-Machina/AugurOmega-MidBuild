
import os
import json
from pathlib import Path
from datetime import datetime

def get_directory_size(directory):
    """Get size of directory in bytes"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if filepath.exists():
                    total += filepath.stat().st_size
    except:
        pass
    return total

def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def track_build_sizes():
    """Track sizes of all build directories"""
    builds_dir = Path("builds")
    sizes = {}
    
    for platform_dir in builds_dir.iterdir():
        if platform_dir.is_dir():
            size_bytes = get_directory_size(platform_dir)
            sizes[platform_dir.name] = {
                "bytes": size_bytes,
                "human_readable": format_bytes(size_bytes),
                "file_count": len(list(platform_dir.rglob("*")))
            }
    
    # Save to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = builds_dir / "size_tracking" / f"build_sizes_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "build_sizes": sizes,
            "total_size": sum(item["bytes"] for item in sizes.values())
        }, f, indent=2)
    
    print("Build size report:")
    for platform, size_info in sizes.items():
        print(f"  {platform}: {size_info['human_readable']} ({size_info['file_count']} files)")
    
    total = sum(item["bytes"] for item in sizes.values())
    print(f"  Total: {format_bytes(total)}")

if __name__ == "__main__":
    track_build_sizes()
