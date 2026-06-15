#!/usr/bin/env python
"""
MeshClean UI Launcher
Start the web interface on localhost:7860
"""

import sys
import os

def main():
    """Launch the UI"""
    print("\n" + "="*60)
    print("[*] MeshClean Pipeline Debugging Environment")
    print("="*60)
    print("\nStarting Flask UI...")
    print("Listening on: http://localhost:7860")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        from ui_minimal import app
        app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting UI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
