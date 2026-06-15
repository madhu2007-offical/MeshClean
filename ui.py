"""
MeshClean Debugger - Professional UI
Clean, hackathon-level interface for pipeline debugging
Uses Gradio with 2-column layout design
"""

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# SESSION MANAGER (Deferred imports to avoid OpenBLAS issues)
# ============================================================================

class DebugSession:
    """Manage debugging session state"""
    
    def __init__(self):
        self.task_id = None
        self.env = None
        self.task_info = {}
    
    def load_task(self, task_id: str) -> bool:
        """Load and initialize task"""
        try:
            from pipeline_debug_env import PipelineDebugEnv
            
            self.task_id = task_id
            self.env = PipelineDebugEnv(task_id)
            obs = self.env.reset()
            
            self.task_info = {
                "name": self.env.state.current_task.task_name,
                "difficulty": self.env.state.current_task.difficulty,
                "error_log": self.env.state.current_task.error_log,
                "root_cause": self.env.state.injected_error_node,
                "error_type": self.env.state.injected_error_type,
            }
            
            return True
        except Exception as e:
            logger.error(f"Task load error: {e}")
            return False
    
    def run_session(self, task_id: str) -> Tuple[str, str, str, str, str, int]:
        """Execute full debugging session"""
        try:
            from inference import DebugAgent
            
            # Load task
            if not self.load_task(task_id):
                return ("Error loading task", "", "", "", "", 0)
            
            # Run agent
            agent = DebugAgent(task_id)
            result = agent.run()
            
            # Format outputs
            logs, viz, analysis, summary = self._format_results(result)
            error_log = self.task_info["error_log"]
            steps = result.get("steps", 0)
            progress = min(100, int((steps / 15) * 100)) if steps > 0 else 0
            
            return logs, viz, analysis, summary, error_log, progress
        
        except Exception as e:
            logger.error(f"Execution error: {e}")
            import traceback
            traceback.print_exc()
            return (f"Error: {str(e)}", "", "", "", "", 0)
    
    def _format_results(self, result: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """Format all result sections"""
        predicted = result.get("predicted_root_cause", "")
        grade = result.get("grade", 0)
        error_type = self.task_info.get("error_type", "unknown")
        actual = self.task_info.get("root_cause", "")
        
        logs = self._format_logs(result)
        viz = self._format_visualization()
        analysis = self._format_analysis(result, predicted, error_type)
        summary = self._format_summary(result, predicted, actual, grade)
        
        return logs, viz, analysis, summary
    
    def _format_logs(self, result: Dict[str, Any]) -> str:
        """Format step logs"""
        lines = ["\n" + "="*60, "DEBUGGING PROCESS LOGS", "="*60 + "\n"]
        
        if "actions" in result:
            for i, action in enumerate(result.get("actions", []), 1):
                lines.append(f"{action}")
        else:
            lines.append("No actions recorded.")
        
        lines.extend(["", "="*60 + "\n"])
        return "\n".join(lines)
    
    def _format_visualization(self) -> str:
        """Format pipeline visualization"""
        if not self.env:
            return "Pipeline not loaded."
        
        lines = ["\n" + "="*60, "PIPELINE STRUCTURE", "="*60 + "\n"]
        
        for node_id, node in self.env.state.current_task.nodes.items():
            parents = ", ".join(node.parents) if node.parents else "NO INPUTS"
            children = ", ".join(node.children) if node.children else "NO OUTPUTS"
            lines.append(f"{node_id:20} |  From: {parents:25} |  To: {children}")
        
        lines.extend(["", "="*60 + "\n"])
        return "\n".join(lines)
    
    def _format_analysis(self, result: Dict[str, Any], predicted: str, error_type: str) -> str:
        """Format agent analysis"""
        lines = ["\n" + "="*70, "AGENT ANALYSIS AND REASONING", "="*70 + "\n"]
        
        lines.extend([
            "EXPLORATION STRATEGY:",
            "  Step 1: Start at output node (error visible location)",
            "  Step 2: Inspect parent nodes and schemas",
            "  Step 3: Move upstream to identify inconsistencies",
            "  Step 4: Determine root cause based on error propagation",
            "",
            "ERROR TYPE:",
            f"  {error_type.replace('_', ' ').title()}",
            "",
            "DIAGNOSIS:",
            f"  Root cause node:  {predicted}",
            "  Error propagation: Cascades downstream from root cause",
            "  Analysis method:   Systematic upstream traversal",
            "",
            "="*70 + "\n"
        ])
        
        return "\n".join(lines)
    
    def _format_summary(self, result: Dict[str, Any], predicted: str, actual: str, grade: float) -> str:
        """Format final results"""
        is_correct = predicted == actual
        status = "CORRECT" if is_correct else "INCORRECT"
        steps = result.get("steps", 0)
        
        lines = ["\n" + "="*60, "FINAL RESULTS", "="*60 + "\n"]
        lines.extend([
            f"Status:                {status}",
            f"Grade:                 {grade:.2f} / 1.00",
            "",
            "PREDICTION:",
            f"  Predicted root cause: {predicted}",
            f"  Actual root cause:    {actual}",
            f"  Match:                {'Yes' if is_correct else 'No'}",
            "",
            "METRICS:",
            f"  Steps executed:       {steps}",
            f"  Final grade:          {grade:.1%}",
            "",
            "="*60 + "\n"
        ])
        
        return "\n".join(lines)


# ============================================================================
# BUILD INTERFACE
# ============================================================================

def build_interface():
    """Build the Gradio interface"""
    # Import Gradio only here to defer loading heavy libraries
    import gradio as gr
    from pipeline_debug_env import PipelineDebugEnv
    
    session = DebugSession()
    
    # Event handlers
    def get_initial_state():
        """Get default state"""
        session.load_task("task_1")
        error_log = session.task_info.get("error_log", "Select a task and click 'Run Debugger' to start")
        task_info = f"Task: {session.task_info.get('name', 'Task 1')}\nDifficulty: Easy"
        viz = session._format_visualization()
        return error_log, task_info, viz, 0
    
    def update_task(task_id):
        """Handle task selection change"""
        session.load_task(task_id)
        error_log = session.task_info.get("error_log", "No error log")
        task_info = f"Task: {session.task_info.get('name', 'N/A')}\nDifficulty: {session.task_info.get('difficulty', 'N/A').upper()}"
        viz = session._format_visualization()
        return error_log, task_info, viz, 0
    
    def run_debug(task_id):
        """Execute debugging session"""
        logs, viz, analysis, summary, error_log, progress = session.run_session(task_id)
        return logs, viz, analysis, summary, progress
    
    # Build interface
    with gr.Blocks(title="MeshClean Debugger") as app:
        
        # Header
        gr.Markdown("# MeshClean Debugger\n**AI-Powered Data Pipeline Debugging Environment**")
        
        with gr.Row():
            # LEFT PANEL (30%)
            with gr.Column(scale=30, min_width=280):
                
                gr.Markdown("**Task Configuration**")
                task_select = gr.Dropdown(
                    choices=["task_1", "task_2", "task_3"],
                    value="task_1",
                    label="Select Task",
                    info="Choose difficulty level"
                )
                
                gr.Markdown("**Error Log**")
                error_display = gr.Textbox(
                    value="Select a task and click Run Debugger",
                    label="Current Error",
                    lines=6,
                    interactive=False,
                    show_label=False
                )
                
                gr.Markdown("**Execution**")
                run_btn = gr.Button("Run Debugger", variant="primary")
                
                progress_bar = gr.Slider(
                    minimum=0, maximum=100, value=0, step=1,
                    label="Progress", interactive=False
                )
                
                gr.Markdown("**Task Information**")
                task_info_display = gr.Textbox(
                    value="Task: Not loaded\nDifficulty: N/A",
                    label="Details",
                    lines=3,
                    interactive=False,
                    show_label=False
                )
            
            # RIGHT PANEL (70%)
            with gr.Column(scale=70):
                
                gr.Markdown("**Debugging Process**")
                logs_output = gr.Textbox(
                    value="Click 'Run Debugger' to begin execution.",
                    label="Step-by-Step Logs",
                    lines=10,
                    interactive=False,
                    show_label=False
                )
                
                gr.Markdown("**Pipeline Structure**")
                viz_output = gr.Textbox(
                    value=session._format_visualization(),
                    label="DAG Visualization",
                    lines=10,
                    interactive=False,
                    show_label=False
                )
                
                gr.Markdown("**Agent Analysis**")
                analysis_output = gr.Textbox(
                    value="Waiting for execution...",
                    label="Reasoning",
                    lines=10,
                    interactive=False,
                    show_label=False
                )
                
                gr.Markdown("**Result Summary**")
                summary_output = gr.Textbox(
                    value="No results yet.",
                    label="Summary",
                    lines=8,
                    interactive=False,
                    show_label=False
                )
        
        # Connect events
        task_select.change(
            update_task,
            inputs=[task_select],
            outputs=[error_display, task_info_display, viz_output, progress_bar]
        )
        
        run_btn.click(
            run_debug,
            inputs=[task_select],
            outputs=[logs_output, viz_output, analysis_output, summary_output, progress_bar]
        )
    
    return app


# ============================================================================
# LAUNCHER
# ============================================================================

def launch():
    """Launch the UI"""
    try:
        print("\n" + "="*60)
        print("MESHCLEAN DEBUGGER - STARTING UI")
        print("="*60)
        print("\nOpen in browser: http://localhost:7860")
        print("Press Ctrl+C to stop\n")
        
        import gradio as gr
        app = build_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            share=False,
            theme=gr.themes.Base()
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    launch()
