"""
Pipeline Debugging Environment
Core environment for agent-based pipeline debugging
"""

import copy
from typing import Dict, Tuple
from pipeline_debug_env.models import (
    Observation, Action, ActionType, StepResult, EnvironmentState, TaskDefinition
)
from pipeline_debug_env.tasks import get_task, list_tasks
from pipeline_debug_env.grader import PipelineGrader
from pipeline_debug_env.error_engine import create_pipeline_with_error
import logging

logger = logging.getLogger(__name__)


class PipelineDebugEnv:
    """
    Environment for debugging data pipelines using agent reasoning.
    
    The agent explores a DAG of processing nodes to find the root cause of an error.
    """
    
    def __init__(self, task_id: str = "task_1"):
        """
        Initialize the environment.
        
        Args:
            task_id: ID of the task to run ("task_1", "task_2", or "task_3")
        """
        self.task_id = task_id
        self.state = None
        self.grader = PipelineGrader()
    
    def reset(self) -> Observation:
        """
        Reset the environment to initial state.
        Dynamically injects error into the task.
        
        Returns:
            Initial observation
        """
        # Get base task
        base_task = get_task(self.task_id)
        
        # Create deep copy and inject error dynamically
        task_with_error, error_node, error_type, decoy_node, decoy_type, error_log = \
            create_pipeline_with_error(base_task, base_task.difficulty)
        
        # Update task with error information
        task_with_error.correct_root_cause = error_node
        task_with_error.error_log = error_log
        
        # Initialize state with error-injected task
        self.state = EnvironmentState(
            current_task=task_with_error,
            current_node=task_with_error.start_node,
            visited_nodes={task_with_error.start_node},
            total_reward=0.0,
            step_count=0,
            done=False,
            injected_error_node=error_node,
            injected_error_type=error_type,
            decoy_error_node=decoy_node,
            decoy_error_type=decoy_type,
            episode_actions=[]
        )
        
        return self._get_observation()
    
    def step(self, action_dict: Dict) -> StepResult:
        """
        Take an action in the environment.
        
        Args:
            action_dict: Dict with action_type and node
                {
                    "action_type": "inspect_node",
                    "node": "B"
                }
        
        Returns:
            StepResult with observation, reward, done, info
        """
        try:
            # Parse and validate action
            action = self._parse_action(action_dict)
            self.state.step_count += 1
            self.state.episode_actions.append(action)
            
            # Execute action
            reward, info = self._execute_action(action)
            
            # Update state
            self.state.total_reward += reward
            
            # Check if episode is done
            done = self.state.done or self.state.step_count >= 20
            self.state.done = done
            
            observation = self._get_observation()
            
            return StepResult(
                observation=observation,
                reward=reward,
                done=done,
                info=info
            )
        
        except Exception as e:
            logger.error(f"Error in step: {e}")
            return StepResult(
                observation=self._get_observation(),
                reward=-0.2,
                done=False,
                info={"error": str(e)}
            )
    
    def _parse_action(self, action_dict: Dict) -> Action:
        """Parse and validate action dictionary"""
        action_type = action_dict.get("action_type")
        node = action_dict.get("node")
        
        if not action_type or not node:
            raise ValueError("Action must have 'action_type' and 'node'")
        
        try:
            action_enum = ActionType(action_type)
        except ValueError:
            raise ValueError(f"Invalid action type: {action_type}")
        
        return Action(
            action_type=action_enum,
            node=node,
            step_number=self.state.step_count
        )
    
    def _execute_action(self, action: Action) -> Tuple[float, Dict]:
        """
        Execute an action and return reward and info.
        
        Reward structure:
        - +1.0: Correct root cause found
        - +0.2: Valid inspection or exploration
        - -0.2: Invalid node or useless action
        - -0.5: Wrong root cause submitted
        """
        task = self.state.current_task
        info = {"action": str(action.action_type.value)}
        
        # Validate node exists
        if action.node not in task.nodes:
            return -0.2, {"error": f"Node {action.node} does not exist"}
        
        if action.action_type == ActionType.INSPECT_NODE:
            return self._handle_inspect_node(action, info)
        
        elif action.action_type == ActionType.MOVE_TO_PARENT:
            return self._handle_move_to_parent(action, info)
        
        elif action.action_type == ActionType.CHECK_SCHEMA:
            return self._handle_check_schema(action, info)
        
        elif action.action_type == ActionType.SUBMIT_ROOT_CAUSE:
            return self._handle_submit_root_cause(action, info)
        
        return -0.2, {"error": "Unknown action type"}
    
    def _handle_inspect_node(self, action: Action, info: Dict) -> Tuple[float, Dict]:
        """Handle inspect_node action"""
        task = self.state.current_task
        node = task.nodes[action.node]
        
        # Check if already visited
        already_visited = action.node in self.state.visited_nodes
        
        # Mark as visited
        self.state.visited_nodes.add(action.node)
        self.state.current_node = action.node
        
        info["node_type"] = node.node_type
        info["description"] = node.description
        info["schema"] = node.schema_info
        
        # Reward: new nodes +0.2, revisits -0.05 (discourages repeated inspection)
        if already_visited:
            return -0.05, {**info, "msg": f"Revisited node {action.node}"}
        else:
            return 0.2, {**info, "msg": f"Inspected new node {action.node}"}
    
    def _handle_move_to_parent(self, action: Action, info: Dict) -> Tuple[float, Dict]:
        """Handle move_to_parent action"""
        task = self.state.current_task
        node = task.nodes[action.node]
        
        if not node.parents:
            return -0.2, {"error": f"Node {action.node} has no parents"}
        
        self.state.visited_nodes.add(action.node)
        self.state.current_node = action.node
        
        info["parents"] = node.parents
        info["msg"] = f"Moved to {action.node}. Parents are: {node.parents}"
        
        return 0.2, info
    
    def _handle_check_schema(self, action: Action, info: Dict) -> Tuple[float, Dict]:
        """Handle check_schema action"""
        task = self.state.current_task
        node = task.nodes[action.node]
        
        # Mark as visited
        already_visited = action.node in self.state.visited_nodes
        self.state.visited_nodes.add(action.node)
        self.state.current_node = action.node
        
        info["schema"] = node.schema_info
        info["node_type"] = node.node_type
        info["msg"] = f"Schema for {action.node}: {node.schema_info}"
        
        # Small reward for schema inspection
        return 0.1, info
    
    def _handle_submit_root_cause(self, action: Action, info: Dict) -> Tuple[float, Dict]:
        """Handle submit_root_cause action"""
        task = self.state.current_task
        predicted = action.node
        correct = task.correct_root_cause
        
        # Grade the prediction
        grade = self.grader.grade(predicted, correct, task.nodes)
        
        self.state.done = True
        
        if grade == 1.0:
            reward = 1.0
            info["result"] = "CORRECT"
        elif grade >= 0.5:
            reward = 0.5
            info["result"] = "PARTIALLY CORRECT"
        elif grade > 0:
            reward = 0.25
            info["result"] = "CLOSE"
        else:
            reward = -0.5
            info["result"] = "INCORRECT"
        
        info["predicted"] = predicted
        info["correct"] = correct
        info["grade"] = grade
        
        return reward, info
    
    def _get_observation(self) -> Observation:
        """
        Get current observation for agent.
        
        Observation includes current node info but NOT the root cause location.
        """
        task = self.state.current_task
        current_node_id = self.state.current_node
        node = task.nodes[current_node_id]
        
        return Observation(
            current_node=current_node_id,
            node_type=node.node_type,
            error_log=task.error_log,  # Shows symptoms at output
            visited_nodes=self.state.visited_nodes.copy(),
            parents=node.parents,
            children=node.children,
            schema_info=node.schema_info,
            node_description=node.description
        )
    
    def state(self) -> EnvironmentState:
        """Return current environment state"""
        return self.state
    
    def get_task_info(self) -> Dict:
        """Get information about current task"""
        task = self.state.current_task
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "difficulty": task.difficulty,
            "description": task.description,
            "error_log": task.error_log,
            "num_nodes": len(task.nodes),
            "correct_root_cause": task.correct_root_cause
        }


# Convenience functions
def make_env(task_id: str = "task_1") -> PipelineDebugEnv:
    """Create an environment instance"""
    return PipelineDebugEnv(task_id)


def available_tasks() -> Dict[str, str]:
    """List available tasks"""
    return list_tasks()
