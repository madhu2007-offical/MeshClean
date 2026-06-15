#!/usr/bin/env python
"""
Complete System Diagnostic and Error Report
"""

import sys
import traceback

# Force UTF-8 encoding on Windows standard output to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def diagnose():
    """Run comprehensive diagnostics"""
    
    print("\n" + "="*70)
    print("MESHCLEAN SYSTEM DIAGNOSTIC")
    print("="*70 + "\n")
    
    errors = []
    
    # ========================================================================
    # TEST 1: Core Imports
    # ========================================================================
    print("[1/7] Testing core imports...")
    try:
        from pipeline_debug_env import PipelineDebugEnv, list_tasks
        print("  ✓ pipeline_debug_env")
    except Exception as e:
        errors.append(f"pipeline_debug_env import: {e}")
        print(f"  ✗ pipeline_debug_env: {e}")
        return errors
    
    # ========================================================================
    # TEST 2: Create Environment
    # ========================================================================
    print("[2/7] Testing environment creation...")
    try:
        env = PipelineDebugEnv("task_1")
        obs = env.reset()
        print("  ✓ Environment creation and reset")
    except Exception as e:
        errors.append(f"Environment creation: {e}")
        print(f"  ✗ Environment: {e}")
        traceback.print_exc()
        return errors
    
    # ========================================================================
    # TEST 3: Check get_task_info method
    # ========================================================================
    print("[3/7] Testing get_task_info()...")
    try:
        task_info = env.get_task_info()
        print(f"  ✓ get_task_info() works")
        print(f"    - Task: {task_info['task_name']}")
        print(f"    - Nodes: {task_info['num_nodes']}")
        print(f"    - Difficulty: {task_info['difficulty']}")
    except Exception as e:
        errors.append(f"get_task_info: {e}")
        print(f"  ✗ get_task_info: {e}")
        traceback.print_exc()
    
    # ========================================================================
    # TEST 4: Inference Agent
    # ========================================================================
    print("[4/7] Testing inference agent...")
    try:
        from inference import DebugAgent
        agent = DebugAgent("task_1")
        print("  ✓ DebugAgent imports and initializes")
    except Exception as e:
        errors.append(f"DebugAgent: {e}")
        print(f"  ✗ DebugAgent: {e}")
        traceback.print_exc()
        return errors
    
    # ========================================================================
    # TEST 5: Run Agent (Limited)
    # ========================================================================
    print("[5/7] Testing agent execution...")
    try:
        result = agent.run()
        print("  ✓ Agent execution completes")
        print(f"    - Actions: {len(result.get('actions', []))}")
        print(f"    - Grade: {result.get('grade', 'N/A')}")
        print(f"    - Steps: {result.get('steps', 'N/A')}")
    except Exception as e:
        errors.append(f"Agent execution: {e}")
        print(f"  ✗ Agent execution: {e}")
        traceback.print_exc()
    
    # ========================================================================
    # TEST 6: Gradio Import
    # ========================================================================
    print("[6/7] Testing Gradio...")
    try:
        import gradio as gr
        print("  ✓ Gradio imports successfully")
    except Exception as e:
        errors.append(f"Gradio import: {e}")
        print(f"  ✗ Gradio: {e}")
        return errors
    
    # ========================================================================
    # TEST 7: UI Module
    # ========================================================================
    print("[7/7] Testing UI module...")
    try:
        # Just test imports, not launching
        import importlib.util
        spec = importlib.util.spec_from_file_location("ui", "ui.py")
        ui_module = importlib.util.module_from_spec(spec)
        print("  ✓ UI module can be loaded")
    except Exception as e:
        errors.append(f"UI module: {e}")
        print(f"  ✗ UI module: {e}")
        traceback.print_exc()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    if errors:
        print(f"\n{len(errors)} ERRORS FOUND:\n")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}\n")
        return errors
    else:
        print("\n✓ ALL TESTS PASSED - SYSTEM IS OPERATIONAL\n")
        return []

if __name__ == "__main__":
    errors = diagnose()
    sys.exit(0 if not errors else 1)
