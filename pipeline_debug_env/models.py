"""
Data Models for Pipeline Debugging Environment
Using dataclasses (built-in, no external dependencies)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
from enum import Enum


class ActionType(str, Enum):
    """Valid action types in the environment"""
    INSPECT_NODE = "inspect_node"
    MOVE_TO_PARENT = "move_to_parent"
    CHECK_SCHEMA = "check_schema"
    SUBMIT_ROOT_CAUSE = "submit_root_cause"


@dataclass
class NodeInfo:
    """Information about a pipeline node"""
    node_id: str
    node_type: str  # "data_source", "processor", "output"
    description: str
    schema_info: Dict[str, str]  # column_name -> data_type
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class Action:
    """An action taken by the agent"""
    action_type: ActionType
    node: str
    step_number: int = 0


@dataclass
class TaskDefinition:
    """Definition of a debugging task"""
    task_id: str
    task_name: str
    difficulty: str  # "easy", "medium", "hard"
    description: str
    nodes: Dict[str, NodeInfo]  # node_id -> NodeInfo
    start_node: str  # Where error is visible
    correct_root_cause: str  # Which node has the root cause
    error_log: str  # Error message at output node
    ground_truth_explanation: str  # Why that's the root cause


@dataclass
class Observation:
    """Observation returned to agent"""
    current_node: str
    node_type: str
    error_log: str
    visited_nodes: Set[str] = field(default_factory=set)
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    schema_info: Dict[str, str] = field(default_factory=dict)
    node_description: str = ""


@dataclass
class StepResult:
    """Result of taking a step in the environment"""
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentState:
    """Complete internal state of the environment"""
    current_task: TaskDefinition
    current_node: str
    visited_nodes: Set[str] = field(default_factory=set)
    total_reward: float = 0.0
    step_count: int = 0
    done: bool = False
    episode_actions: List[Action] = field(default_factory=list)
    
    # Dynamic error tracking
    injected_error_node: str = ""  # Which node has the root cause error
    injected_error_type: str = ""  # Type of error (missing_column, type_mismatch, renamed_column, etc.)
    decoy_error_node: str = ""  # Hard task only: unrelated error node
    decoy_error_type: str = ""  # Hard task only: type of decoy error
    error_propagation_map: Dict[str, List[str]] = field(default_factory=dict)  # Lists affected nodes
