"""
Dynamic Error Injection and Propagation
Core logic for randomly generating and propagating errors through the DAG
"""

import random
from typing import Dict, Tuple, List
from pipeline_debug_env.models import TaskDefinition, NodeInfo


class ErrorInjector:
    """
    Dynamically injects errors into pipeline nodes and propagates them downstream.
    
    Core concept: Errors travel from upstream → downstream
    - Root cause error originates at one random node
    - Error affects all downstream nodes
    - Hard task adds independent decoy error
    """
    
    ERROR_TYPES = [
        "missing_column",      # Essential column missing from node
        "type_mismatch",       # Column data type changed (e.g., float→int)
        "renamed_column",      # Column name changed
        "schema_conflict",     # Incompatible schema with downstream
        "data_loss"            # Rows dropped or data lost
    ]
    
    def __init__(self, seed: int = None):
        """Initialize error injector with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
    
    def inject_error(self, task: TaskDefinition, difficulty: str) -> Tuple[str, str, Dict[str, List[str]]]:
        """
        Inject error into task and return propagation map.
        
        Args:
            task: TaskDefinition to modify
            difficulty: "easy", "medium", or "hard"
        
        Returns:
            (error_node, error_type, propagation_map)
            where propagation_map[node] = [list of affected downstream nodes]
        """
        # Choose random node (excluding output)
        available_nodes = [n for n in task.nodes.keys() if n != "output"]
        error_node = random.choice(available_nodes)
        error_type = random.choice(self.ERROR_TYPES)
        
        # Calculate error propagation
        propagation_map = self._calculate_propagation(error_node, task)
        
        # Apply error to root node and propagate
        self._apply_error_to_node(task.nodes[error_node], error_type)
        self._propagate_error_downstream(error_node, task, error_type)
        
        return error_node, error_type, propagation_map
    
    def inject_decoy_error(self, task: TaskDefinition, error_node: str) -> Tuple[str, str]:
        """
        Inject Independent error at different node (Hard task only).
        This error does NOT affect the pipeline outcome.
        
        Args:
            task: TaskDefinition to modify
            error_node: The node with real root cause (to avoid placing decoy there)
        
        Returns:
            (decoy_node, decoy_error_type)
        """
        # Choose node different from root cause and output
        available = [n for n in task.nodes.keys() 
                     if n != error_node and n != "output"]
        
        if not available:
            return "", ""
        
        decoy_node = random.choice(available)
        decoy_error_type = random.choice(self.ERROR_TYPES)
        
        # Apply decoy error (doesn't propagate to output)
        self._apply_error_to_node(task.nodes[decoy_node], decoy_error_type)
        
        return decoy_node, decoy_error_type
    
    def _calculate_propagation(self, root_node: str, task: TaskDefinition) -> Dict[str, List[str]]:
        """
        Calculate which nodes are affected by error at root_node.
        
        Returns:
            Map: affected_node -> [list of downstream nodes that inherit error]
        """
        propagation = {}
        affected = self._get_all_descendants(root_node, task)
        propagation[root_node] = affected
        
        return propagation
    
    def _get_all_descendants(self, node_id: str, task: TaskDefinition) -> List[str]:
        """Get all downstream nodes from a given node using DFS"""
        descendants = []
        visited = set()
        
        def dfs(current):
            if current in visited:
                return
            visited.add(current)
            
            node = task.nodes.get(current)
            if node:
                for child in node.children:
                    descendants.append(child)
                    dfs(child)
        
        dfs(node_id)
        return descendants
    
    def _apply_error_to_node(self, node: NodeInfo, error_type: str):
        """
        Apply error transformation to a node's schema.
        
        This modifies the node's schema_info to reflect the error.
        """
        if error_type == "missing_column":
            # Remove a column
            if node.schema_info:
                col_to_remove = random.choice(list(node.schema_info.keys()))
                del node.schema_info[col_to_remove]
        
        elif error_type == "type_mismatch":
            # Change a column type (often to less precise)
            if node.schema_info:
                col_to_change = random.choice(list(node.schema_info.keys()))
                # Change types strategically
                type_map = {
                    "float": "int",           # Precision loss
                    "str": "int",             # Type error
                    "datetime": "str",        # Loss of type info
                    "int": "str"              # Type mismatch
                }
                old_type = node.schema_info[col_to_change]
                new_type = type_map.get(old_type, "str")
                node.schema_info[col_to_change] = new_type
        
        elif error_type == "renamed_column":
            # Rename a column
            if node.schema_info:
                old_name = random.choice(list(node.schema_info.keys()))
                col_type = node.schema_info[old_name]
                del node.schema_info[old_name]
                # Generate new name
                new_name = f"{old_name}_renamed"
                node.schema_info[new_name] = col_type
        
        elif error_type == "schema_conflict":
            # Create incompatibility with parent schema
            if node.schema_info:
                # Add unexpected column or remove expected one
                if random.choice([True, False]):
                    node.schema_info["unexpected_col"] = "str"
                else:
                    if node.schema_info:
                        del list(node.schema_info.items())[0]
        
        elif error_type == "data_loss":
            # Mark that rows were lost (schema unchanged but data affected)
            # Could add metadata field, but for simplicity we just mark description
            node.description = f"[DATA LOSS] {node.description}"
    
    def _propagate_error_downstream(self, error_node: str, task: TaskDefinition, error_type: str):
        """
        Propagate error to all descendant nodes.
        
        Downstream nodes inherit the error effects.
        """
        descendants = self._get_all_descendants(error_node, task)
        
        for descendant in descendants:
            if descendant in task.nodes:
                node = task.nodes[descendant]
                
                # Don't re-apply same error type, but mark as affected
                # The node's schema already reflects issues from upstream
                if error_type != "data_loss":
                    # Propagate schema changes
                    parent_node = task.nodes.get(error_node)
                    if parent_node:
                        # Child gets parent's potentially broken schema
                        # This simulates natural error propagation
                        pass
                
                # Update description to indicate downstream effect
                node.description = f"[AFFECTED BY UPSTREAM ERROR] {node.description}"


class ErrorLogGenerator:
    """Generate realistic error log messages based on injected error"""
    
    @staticmethod
    def generate_error_log(error_node: str, error_type: str, 
                          descendants: List[str]) -> str:
        """
        Generate error log message that describes symptoms (not root cause).
        
        The log shows effects at output level, not the root cause.
        
        Returns:
            Error log string describing symptoms
        """
        error_messages = {
            "missing_column": (
                f"ERROR: Pipeline execution failed at output. "
                f"Missing required columns in data. "
                f"Error originated from upstream processing."
            ),
            "type_mismatch": (
                f"ERROR: Type mismatch detected in pipeline. "
                f"Column type incompatibility between branches. "
                f"Expected different type but got different type."
            ),
            "renamed_column": (
                f"ERROR: Column name mismatch in output. "
                f"Schemas don't align - columns were renamed upstream. "
                f"Join/merge operation failed due to unmatched column names."
            ),
            "schema_conflict": (
                f"ERROR: Schema conflict in merge operation. "
                f"Incompatible columns from different branches. "
                f"Cannot merge datasets with different structure."
            ),
            "data_loss": (
                f"ERROR: Data loss detected in pipeline. "
                f"Fewer records than expected in output. "
                f"Rows were dropped during upstream processing."
            )
        }
        
        return error_messages.get(error_type, "ERROR: Pipeline processing failed")


def create_pipeline_with_error(task: TaskDefinition, difficulty: str) -> TaskDefinition:
    """
    Create a copy of task with dynamically injected error.
    
    This is the main entry point for error injection.
    """
    import copy
    task_copy = copy.deepcopy(task)
    
    injector = ErrorInjector()
    error_node, error_type, propagation = injector.inject_error(task_copy, difficulty)
    
    # Add decoy for hard task
    decoy_node, decoy_type = "", ""
    if difficulty == "hard":
        decoy_node, decoy_type = injector.inject_decoy_error(task_copy, error_node)
    
    # Generate error log
    error_log = ErrorLogGenerator.generate_error_log(
        error_node, error_type, propagation.get(error_node, [])
    )
    
    return task_copy, error_node, error_type, decoy_node, decoy_type, error_log
