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
    print("\nStarting Gradio UI...")
    print("Listening on: http://localhost:7860")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        from ui import build_interface
        app = build_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            share=False
        )
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
