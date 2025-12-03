#!/usr/bin/env python3
"""
Augur Omega: Main Build Entry Point
Coordinates the complete multi-platform build process
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the build system"""
    print("🌟 Augur Omega: Advanced AI Business Platform")
    print("🚀 Multi-Platform Build System")
    print("="*60)
    
    try:
        # Import the enhanced build system
        from enhanced_build_system import BuildSystem
        
        # Create and run the build system
        builder = BuildSystem()
        
        # Run the complete build process
        builder.build_all()
        
    except ImportError as e:
        print(f"❌ Failed to import build system: {e}")
        print("💡 Make sure you're running from the project root directory")
        print("💡 Ensure all requirements are installed: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()