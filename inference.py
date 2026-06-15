"""
Baseline Inference Agent
Simple strategy-based agent for debugging pipelines
"""

import logging
from typing import List, Dict, Any
from pipeline_debug_env.environment import make_env
from pipeline_debug_env.models import Observation, ActionType

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DebugAgent:
    """
    Simple agent that debugs pipelines by systematic exploration.
    Strategy: Start at error, move upstream to find root cause.
    """
    
    def __init__(self, task_id: str = "task_1"):
        self.task_id = task_id
        self.env = make_env(task_id)
        self.visited_nodes = set()
        self.action_history = []
        self.total_reward = 0.0
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent on a task.
        
        Returns:
            Dictionary with execution summary
        """
        # Print header
        logger.info("[START]")
        
        # Reset environment
        obs = self.env.reset()
        task_info = self.env.get_task_info()
        
        logger.info(f"[INFO] Task: {task_info['task_name']} ({task_info['difficulty']})")
        logger.info(f"[INFO] Error: {task_info['error_log']}")
        logger.info(f"[INFO] Nodes: {task_info['num_nodes']}")
        
        # Strategy: Explore upstream from error node
        strategy_plan = self._plan_exploration(obs)
        logger.info(f"[INFO] Exploration plan: {' -> '.join(strategy_plan)}")
        
        # Execute planned actions
        step = 0
        explored = set()
        
        for node in strategy_plan:
            if step >= 15:  # Limit steps
                break
            
            # Inspect node
            if node not in explored:
                step += 1
                action_result = self.env.step({
                    "action_type": "inspect_node",
                    "node": node
                })
                reward = action_result.reward
                self.total_reward += reward
                obs = action_result.observation
                
                log_line = f"[STEP {step}] action=inspect_node({node}) reward={reward:.1f} total_reward={self.total_reward:.1f}"
                logger.info(log_line)
                self.action_history.append(log_line)
                explored.add(node)
                
                # Check schema for deeper understanding
                if node in obs.parents or obs.node_type == "data_source":
                    step += 1
                    action_result = self.env.step({
                        "action_type": "check_schema",
                        "node": node
                    })
                    reward = action_result.reward
                    self.total_reward += reward
                    
                    log_line = f"[STEP {step}] action=check_schema({node}) reward={reward:.1f} total_reward={self.total_reward:.1f}"
                    logger.info(log_line)
                    self.action_history.append(log_line)
        
        # Make final prediction
        step += 1
        predicted_root_cause = self._predict_root_cause()
        
        action_result = self.env.step({
            "action_type": "submit_root_cause",
            "node": predicted_root_cause
        })
        
        reward = action_result.reward
        self.total_reward += reward
        info = action_result.info
        
        log_line = (
            f"[STEP {step}] action=submit_root_cause({predicted_root_cause}) "
            f"reward={reward:.1f} total_reward={self.total_reward:.1f} "
            f"result={info.get('result', 'UNKNOWN')}"
        )
        logger.info(log_line)
        self.action_history.append(log_line)
        
        # Print final summary
        logger.info(f"[INFO] Episode complete in {step} steps")
        logger.info(f"[INFO] Final reward: {self.total_reward:.1f}")
        logger.info(f"[INFO] Predicted root cause: {predicted_root_cause}")
        logger.info(f"[INFO] Correct root cause: {info.get('correct', 'UNKNOWN')}")
        logger.info(f"[INFO] Grade: {info.get('grade', 0.0):.2f}")
        logger.info("[END]")
        
        return {
            "task_id": self.task_id,
            "steps": step,
            "total_reward": self.total_reward,
            "predicted_root_cause": predicted_root_cause,
            "correct_root_cause": info.get('correct'),
            "grade": info.get('grade', 0.0),
            "result": info.get('result'),
            "actions": self.action_history
        }
    
    def _plan_exploration(self, obs: Observation) -> List[str]:
        """Plan which nodes to explore (upstream first)"""
        plan = [obs.current_node]  # Start at error node
        
        # Add parents to plan (move upstream)
        current = obs.current_node
        visited = {current}
        
        def add_parents_recursively(node_id: str, depth: int = 0):
            if depth > 5:  # Limit depth
                return
            
            task = self.env.state.current_task
            node = task.nodes.get(node_id)
            if not node:
                return
            
            for parent in node.parents:
                if parent not in visited:
                    plan.append(parent)
                    visited.add(parent)
                    add_parents_recursively(parent, depth + 1)
        
        add_parents_recursively(current)
        return plan[:10]  # Limit to 10 nodes
    
    def _predict_root_cause(self) -> str:
        """
        Simple heuristic: identify root cause.
        Strategy: Likely to be a data_source or early processor with issues.
        """
        task = self.env.state.current_task
        
        # Look for data_source nodes (most likely root cause)
        for node_id, node in task.nodes.items():
            if node.node_type == "data_source":
                return node_id
        
        # Fallback: return first visited node
        if self.env.state.visited_nodes:
            return min(self.env.state.visited_nodes)
        
        return list(task.nodes.keys())[0]


def run_inference_on_task(task_id: str = "task_1") -> Dict[str, Any]:
    """
    Run inference on a specific task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Execution summary
    """
    agent = DebugAgent(task_id)
    return agent.run()


def run_all_inference() -> Dict[str, Dict[str, Any]]:
    """Run agent on all tasks"""
    results = {}
    for task_id in ["task_1", "task_2", "task_3"]:
        logger.info("\n" + "="*60)
        results[task_id] = run_inference_on_task(task_id)
    return results


if __name__ == "__main__":
    # Run on single task by default
    import sys
    
    task_id = sys.argv[1] if len(sys.argv) > 1 else "task_1"
    run_inference_on_task(task_id)
