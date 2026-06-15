"""
Grading Logic for Pipeline Debugging
Evaluates if predicted root cause is correct
"""

from typing import Dict


class PipelineGrader:
    """Grades predictions with distance-based scoring"""
    
    @staticmethod
    def grade(predicted_root_cause: str, correct_root_cause: str, 
              graph_nodes: Dict) -> float:
        """
        Grade the prediction with nuanced scoring.
        
        Args:
            predicted_root_cause: The node agent identified as root cause
            correct_root_cause: The true root cause
            graph_nodes: Dictionary of all nodes in the graph
            
        Returns:
            Score between 0.0 (completely wrong) and 1.0 (correct)
        """
        if predicted_root_cause == correct_root_cause:
            return 1.0
        
        # If wrong, check if it's at least a nearby node
        # This prevents completely wrong answers from getting credit
        
        correct_node = graph_nodes.get(correct_root_cause)
        predicted_node = graph_nodes.get(predicted_root_cause)
        
        if not correct_node or not predicted_node:
            return 0.0
        
        # Distance-based scoring
        distance = PipelineGrader._graph_distance(
            predicted_root_cause, correct_root_cause, graph_nodes
        )
        
        if distance == 1:
            # Adjacent node (parent or child)
            return 0.5
        elif distance == 2:
            # Two steps away
            return 0.25
        else:
            # Too far away
            return 0.0
    
    @staticmethod
    def _graph_distance(node1: str, node2: str, graph_nodes: Dict) -> int:
        """
        Calculate minimum distance between two nodes in DAG.
        Using BFS approach.
        """
        if node1 == node2:
            return 0
        
        from collections import deque
        
        visited = {node1}
        queue = deque([(node1, 0)])
        
        while queue:
            current, dist = queue.popleft()
            current_node = graph_nodes.get(current)
            
            if not current_node:
                continue
            
            # Check parents
            for parent in current_node.parents:
                if parent == node2:
                    return dist + 1
                if parent not in visited:
                    visited.add(parent)
                    queue.append((parent, dist + 1))
            
            # Check children
            for child in current_node.children:
                if child == node2:
                    return dist + 1
                if child not in visited:
                    visited.add(child)
                    queue.append((child, dist + 1))
        
        return float('inf')  # Not reachable
