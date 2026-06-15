import sys

# Force UTF-8 encoding on Windows standard output to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_imports():
    """Test 1: Module imports"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTS")
    print("="*60)
    try:
        from pipeline_debug_env import (
            PipelineDebugEnv, 
            get_task, 
            list_tasks,
            ErrorInjector,
            ErrorLogGenerator
        )
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_tasks():
    """Test 2: Task loading and inspection"""
    print("\n" + "="*60)
    print("TEST 2: TASK LOADING")
    print("="*60)
    try:
        from pipeline_debug_env import list_tasks, get_task
        
        tasks = list_tasks()
        print("Available tasks:")
        for task_id, task_name in tasks.items():
            print(f"  • {task_id}: {task_name}")
        
        # Load each task
        print("\nLoading tasks (base structures):")
        for task_id in tasks.keys():
            task = get_task(task_id)
            print(f"  ✓ {task_id} -> {len(task.nodes)} nodes, difficulty: {task.difficulty}")
        
        return True
    except Exception as e:
        print(f"✗ Task loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_creation():
    """Test 3: Environment initialization and error injection"""
    print("\n" + "="*60)
    print("TEST 3: ENVIRONMENT CREATION & ERROR INJECTION")
    print("="*60)
    try:
        from pipeline_debug_env import PipelineDebugEnv
        
        for task_id in ["task_1", "task_2", "task_3"]:
            env = PipelineDebugEnv(task_id)
            obs = env.reset()
            
            print(f"\n{task_id}:")
            print(f"  ✓ Environment created")
            print(f"  ✓ Error injected:")
            print(f"    - Root cause at: {env.state.injected_error_node}")
            print(f"    - Error type: {env.state.injected_error_type}")
            
            if env.state.decoy_error_node:
                print(f"    - Decoy error at: {env.state.decoy_error_node}")
                print(f"    - Decoy type: {env.state.decoy_error_type}")
            
            print(f"  ✓ Current observation:")
            print(f"    - Current node: {obs.current_node}")
            print(f"    - Node type: {obs.node_type}")
            print(f"    - Parents: {obs.parents}")
            print(f"    - Children: {obs.children}")
            print(f"    - Error log: {obs.error_log[:60]}...")
        
        return True
    except Exception as e:
        print(f"✗ Environment creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_episode():
    """Test 4: Run a complete episode"""
    print("\n" + "="*60)
    print("TEST 4: FULL EPISODE EXECUTION")
    print("="*60)
    try:
        from pipeline_debug_env import PipelineDebugEnv
        
        env = PipelineDebugEnv("task_1")
        obs = env.reset()
        
        print(f"\nInitial State:")
        print(f"  Task: {env.state.current_task.task_name}")
        print(f"  Root cause (hidden from agent): {env.state.injected_error_node}")
        print(f"  Error log: {env.state.current_task.error_log}")
        print(f"  Start node: {obs.current_node}")
        
        # Simulate agent actions
        actions = [
            {"action_type": "inspect_node", "node": "A_source"},
            {"action_type": "check_schema", "node": "A_source"},
            {"action_type": "move_to_parent", "node": "B_processor"},
            {"action_type": "inspect_node", "node": "B_processor"},
            {"action_type": "submit_root_cause", "node": env.state.injected_error_node},
        ]
        
        print(f"\nExecuting {len(actions)} actions:")
        total_reward = 0
        
        for i, action in enumerate(actions, 1):
            result = env.step(action)
            total_reward += result.reward
            
            print(f"\n  Step {i}: {action['action_type'].replace('_', ' ').title()}")
            print(f"    Node: {action['node']}")
            print(f"    Reward: {result.reward:+.2f}")
            print(f"    Current node: {result.observation.current_node}")
            print(f"    Done: {result.done}")
            
            if "grade" in result.info:
                print(f"    Grade: {result.info['grade']} ({result.info.get('result', 'N/A')})")
            if "msg" in result.info:
                print(f"    Message: {result.info['msg']}")
        
        print(f"\n  Total Reward: {total_reward:.2f}")
        print(f"  Episode Done: {result.done}")
        
        return True
    except Exception as e:
        print(f"✗ Episode execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hard_task():
    """Test 5: Hard task with decoy error"""
    print("\n" + "="*60)
    print("TEST 5: HARD TASK (WITH DECOY ERROR)")
    print("="*60)
    try:
        from pipeline_debug_env import PipelineDebugEnv
        
        env = PipelineDebugEnv("task_3")
        obs = env.reset()
        
        print(f"\nTask: {env.state.current_task.task_name}")
        print(f"Difficulty: {env.state.current_task.difficulty}")
        print(f"DAG Nodes: {len(env.state.current_task.nodes)}")
        
        print(f"\nError Configuration:")
        print(f"  Root cause at: {env.state.injected_error_node}")
        print(f"  Root error type: {env.state.injected_error_type}")
        print(f"  Decoy error at: {env.state.decoy_error_node}")
        print(f"  Decoy error type: {env.state.decoy_error_type}")
        
        print(f"\nPipeline Structure:")
        for node_id, node in env.state.current_task.nodes.items():
            print(f"  {node_id}: {node.node_type:<12} | Parents: {node.parents or ['None']} | Children: {node.children or ['None']}")
        
        return True
    except Exception as e:
        print(f"✗ Hard task test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grading():
    """Test 6: Grading and distance calculation"""
    print("\n" + "="*60)
    print("TEST 6: GRADING & DISTANCE CALCULATION")
    print("="*60)
    try:
        from pipeline_debug_env import PipelineDebugEnv
        
        env = PipelineDebugEnv("task_2")
        obs = env.reset()
        
        grader = env.grader
        task = env.state.current_task
        true_node = env.state.injected_error_node
        
        print(f"\nTrue root cause: {true_node}")
        print(f"\nGrade predictions:")
        
        # Test various predictions
        test_predictions = [
            true_node,  # Correct
            list(task.nodes.keys())[0],  # Could be adjacent/far
            list(task.nodes.keys())[-1],  # Likely far
        ]
        
        for pred in test_predictions:
            grade = grader.grade(pred, true_node, task.nodes)
            distance = grader._graph_distance(pred, true_node, task.nodes)
            print(f"  Prediction: {pred:<15} | Grade: {grade:.2f} | Distance: {distance}")
        
        return True
    except Exception as e:
        print(f"✗ Grading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  MESHCLEAN SYSTEM COMPREHENSIVE TEST SUITE  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Imports": test_imports(),
        "Task Loading": test_tasks(),
        "Environment & Error Injection": test_environment_creation(),
        "Full Episode": test_episode(),
        "Hard Task": test_hard_task(),
        "Grading System": test_grading(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASSED" if passed_flag else "✗ FAILED"
        print(f"{status:10} | {test_name}")
    
    print("\n" + "-"*60)
    print(f"Result: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS RUNNING CORRECTLY! 🎉\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - see details above\n")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
