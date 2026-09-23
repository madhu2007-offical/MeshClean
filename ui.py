#!/usr/bin/env python
"""
MeshClean Debugger Environment - Professional Gradio UI
Matches strict design constraints (no icons, no emojis, dark theme, structured layout)
"""

import time
import io
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import gradio as gr

# Force UTF-8 encoding on Windows standard output to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Map UI names to internal task IDs
TASK_MAP = {
    "Easy": "task_1",
    "Medium": "task_2",
    "Hard": "task_3"
}

# ============================================================================
# GRAPH VISUALIZATION GENERATOR
# ============================================================================

def get_dag_positions(task):
    """Compute symmetric, layered layout coordinates for any pipeline DAG"""
    G = nx.DiGraph()
    for nid, node in task.nodes.items():
        G.add_node(nid)
        for child in node.children:
            G.add_edge(nid, child)
    
    layers = {}
    try:
        top_order = list(nx.topological_sort(G))
    except Exception:
        top_order = list(G.nodes())
        
    for node in top_order:
        preds = list(G.predecessors(node))
        if not preds:
            layers[node] = 0
        else:
            layers[node] = max(layers.get(p, 0) for p in preds) + 1
            
    max_layer = max(layers.values()) if layers else 1
    
    by_layer = {}
    for node, layer in layers.items():
        by_layer.setdefault(layer, []).append(node)
        
    pos = {}
    for layer, nodes_in_layer in by_layer.items():
        y = float(max_layer - layer) * 2.0
        n_nodes = len(nodes_in_layer)
        for i, node in enumerate(sorted(nodes_in_layer)):
            if n_nodes == 1:
                x = 0.0
            else:
                x = (i - (n_nodes - 1) / 2.0) * 2.0
            pos[node] = (x, y)
            
    for nid in task.nodes:
        if nid not in pos:
            pos[nid] = (0.0, 0.0)
            
    return pos

def draw_dag_image(task, current_node=None, visited_nodes=None, predicted_node=None, actual_root_cause=None, show_result=False):
    """Draw and return the DAG visualization with state-specific node colors"""
    if visited_nodes is None:
        visited_nodes = set()
        
    fig, ax = plt.subplots(figsize=(6, 5), facecolor='#090B0F')
    ax.set_facecolor('#090B0F')
    
    G = nx.DiGraph()
    for nid, node in task.nodes.items():
        G.add_node(nid)
        for child in node.children:
            G.add_edge(nid, child)
            
    pos = get_dag_positions(task)
    if not pos or any(node not in pos for node in G.nodes()):
        pos = nx.spring_layout(G)
    
    # Color mapping according to strict design rules:
    # - Red: current node
    # - Yellow: visited nodes
    # - Green: root cause (if final prediction is correct/shown)
    # - Blue: normal nodes
    node_colors = []
    for node in G.nodes():
        if show_result and node == actual_root_cause:
            node_colors.append('#10B981')  # Green for root cause
        elif node == current_node:
            node_colors.append('#EF4444')  # Red for current
        elif node in visited_nodes:
            node_colors.append('#EAB308')  # Yellow for visited
        else:
            node_colors.append('#3B82F6')  # Blue for normal
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color='#21262D',
        width=1.5,
        arrows=True,
        arrowstyle='-|>',
        arrowsize=12,
        node_size=800
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=800,
        edgecolors='#30363D',
        linewidths=1.2
    )
    
    # Draw node labels (using base names for cleaner visual structure)
    labels = {nid: nid.split('_')[0] for nid in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, labels=labels, ax=ax,
        font_size=8,
        font_color='#F0F6FC',
        font_family='sans-serif',
        font_weight='bold'
    )
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save fig to BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

# ============================================================================
# EVENT HANDLERS & GENERATORS
# ============================================================================

def on_task_change(task_name):
    """Handle task selection and return initial reset values"""
    task_id = TASK_MAP[task_name]
    from pipeline_debug_env import PipelineDebugEnv
    env = PipelineDebugEnv(task_id)
    env.reset()
    task = env.state.current_task
    
    initial_img = draw_dag_image(task, current_node=task.start_node)
    
    return task.error_log, initial_img, "Ready. Click Run Debugger to start.", 0, "", "", ""

def run_debug_generator(task_name):
    """Step-by-step generator yielding updates to the Gradio UI"""
    task_id = TASK_MAP[task_name]
    from pipeline_debug_env import PipelineDebugEnv
    from inference import DebugAgent
    
    env = PipelineDebugEnv(task_id)
    obs = env.reset()
    task = env.state.current_task
    actual_cause = env.state.injected_error_node
    
    agent = DebugAgent(task_id)
    agent.env = env
    strategy_plan = agent._plan_exploration(obs)
    
    logs = []
    visited = set()
    step = 0
    total_reward = 0.0
    
    logs.append(f"Step {step}: Initialized pipeline debugger for {task_name} configuration")
    logs.append(f"Step {step}: Injected error detected at node {obs.current_node}")
    visited.add(obs.current_node)
    
    img = draw_dag_image(task, current_node=obs.current_node, visited_nodes=visited)
    analysis = "Agent Analysis:\nError detected at output node\nTraversing upstream dependencies"
    
    yield (
        "\n".join(logs),
        img,
        analysis,
        0,
        "",
        "",
        ""
    )
    time.sleep(1.0)
    
    explored = set()
    for node in strategy_plan:
        if step >= 15:
            break
            
        if node not in explored:
            # Action 1: Inspect node
            step += 1
            action_result = env.step({
                "action_type": "inspect_node",
                "node": node
            })
            reward = action_result.reward
            total_reward += reward
            obs = action_result.observation
            visited.add(node)
            explored.add(node)
            
            logs.append(f"Step {step}: Inspect node {node}")
            progress = int((step / 10) * 100)
            progress = min(95, progress)
            
            img = draw_dag_image(task, current_node=node, visited_nodes=visited)
            analysis = f"Agent Analysis:\nInspecting node {node}\nChecking data consistency and parent schemas"
            
            yield (
                "\n".join(logs),
                img,
                analysis,
                progress,
                "",
                "",
                ""
            )
            time.sleep(1.0)
            
            # Action 2: Check schema (if node is parent or source)
            if node in obs.parents or obs.node_type == "data_source":
                step += 1
                action_result = env.step({
                    "action_type": "check_schema",
                    "node": node
                })
                reward = action_result.reward
                total_reward += reward
                
                logs.append(f"Step {step}: Check schema of node {node}")
                progress = int((step / 10) * 100)
                progress = min(95, progress)
                
                img = draw_dag_image(task, current_node=node, visited_nodes=visited)
                analysis = f"Agent Analysis:\nChecking schema fields for {node}\nValidating column mappings and types"
                
                yield (
                    "\n".join(logs),
                    img,
                    analysis,
                    progress,
                    "",
                    "",
                    ""
                )
                time.sleep(1.0)
                
    # Final step: submit prediction
    step += 1
    predicted_root_cause = agent._predict_root_cause()
    action_result = env.step({
        "action_type": "submit_root_cause",
        "node": predicted_root_cause
    })
    reward = action_result.reward
    total_reward += reward
    info = action_result.info
    
    logs.append(f"Step {step}: Submitted prediction -> {predicted_root_cause} (Result: {info.get('result', 'UNKNOWN')})")
    logs.append("Step Completed: Root cause identified")
    
    img = draw_dag_image(
        task, 
        current_node=predicted_root_cause, 
        visited_nodes=visited, 
        predicted_node=predicted_root_cause, 
        actual_root_cause=actual_cause, 
        show_result=True
    )
    
    analysis = (
        f"Agent Analysis:\n"
        f"Root cause identified at {predicted_root_cause}\n"
        f"Suggested fix: check node implementation or schema alignment"
    )
    
    yield (
        "\n".join(logs),
        img,
        analysis,
        100,
        predicted_root_cause,
        str(step),
        f"{total_reward:.2f}"
    )

# ============================================================================
# BUILD INTERFACE
# ============================================================================

def build_interface():
    """Build the Gradio interface adhering to strict layouts and design styling"""
    # VS Code / Observability Dashboard style CSS overrides
    css_styles = """
    body {
        background-color: #090B0F !important;
    }
    .gradio-container {
        max-width: 1400px !important;
    }
    textarea {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #090D16 !important;
        color: #C9D1D9 !important;
        border-color: #21262D !important;
    }
    input {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #090D16 !important;
        color: #C9D1D9 !important;
        border-color: #21262D !important;
    }
    .panel-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #58A6FF;
        font-weight: 600;
        margin-bottom: 8px;
    }
    """
    
    with gr.Blocks(title="MeshClean Debugger") as app:
        app._custom_theme = gr.themes.Default(primary_hue="blue", neutral_hue="slate")
        app._custom_css = css_styles
        # Title
        gr.Markdown("# MeshClean Debugger")
        gr.Markdown("AI-driven pipeline debugging with visual reasoning.")
        
        with gr.Row():
            # LEFT PANEL (30% width)
            with gr.Column(scale=30):
                gr.Markdown("<div class='panel-header'>TASK CONTROL</div>")
                
                task_select = gr.Dropdown(
                    choices=["Easy", "Medium", "Hard"],
                    value="Easy",
                    label="Task Selector",
                    info="Select pipeline difficulty"
                )
                
                error_log = gr.Textbox(
                    value="",
                    label="Error Log Display",
                    interactive=False,
                    lines=8
                )
                
                run_btn = gr.Button("Run Debugger", variant="primary")
                
                progress_bar = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    label="Progress",
                    interactive=False
                )
                
            # RIGHT PANEL (70% width)
            with gr.Column(scale=70):
                with gr.Row():
                    # Left Column of Main Area
                    with gr.Column(scale=50):
                        gr.Markdown("<div class='panel-header'>PROCESS & REASONING</div>")
                        
                        logs_output = gr.Textbox(
                            label="Debugging Process",
                            interactive=False,
                            lines=12,
                            placeholder="Awaiting execution logs..."
                        )
                        
                        analysis_output = gr.Textbox(
                            label="Agent Analysis",
                            interactive=False,
                            lines=6,
                            placeholder="Awaiting reasoning analysis..."
                        )
                        
                    # Right Column of Main Area
                    with gr.Column(scale=50):
                        gr.Markdown("<div class='panel-header'>VISUAL OBSERVABILITY</div>")
                        
                        viz_output = gr.Image(
                            label="Pipeline Visualization",
                            interactive=False
                        )
                        
                        gr.Markdown("<div class='panel-header'>METRIC SUMMARY</div>")
                        with gr.Row():
                            root_cause_out = gr.Textbox(
                                label="Root Cause", 
                                interactive=False
                            )
                            steps_out = gr.Textbox(
                                label="Steps Taken", 
                                interactive=False
                            )
                        with gr.Row():
                            reward_out = gr.Textbox(
                                label="Total Reward", 
                                interactive=False
                            )
                            
        # Bind change listener to update error log and DAG visualization
        task_select.change(
            on_task_change,
            inputs=[task_select],
            outputs=[error_log, viz_output, logs_output, progress_bar, root_cause_out, steps_out, reward_out]
        )
        
        # Bind click listener to launch step-by-step generator run
        run_btn.click(
            run_debug_generator,
            inputs=[task_select],
            outputs=[logs_output, viz_output, analysis_output, progress_bar, root_cause_out, steps_out, reward_out]
        )
        
        # Initialize default state on load
        app.load(
            on_task_change,
            inputs=[task_select],
            outputs=[error_log, viz_output, logs_output, progress_bar, root_cause_out, steps_out, reward_out]
        )
        
    return app

# ============================================================================
# LAUNCHER
# ============================================================================

def launch():
    """Launch the UI"""
    try:
        print("\n" + "="*60)
        print("MESHCLEAN DEBUGGER - STARTING GRADIO UI")
        print("="*60)
        print("\nOpen in browser: http://localhost:7860")
        print("Press Ctrl+C to stop\n")
        
        app = build_interface()
        theme = getattr(app, "_custom_theme", None)
        css = getattr(app, "_custom_css", None)
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            share=False,
            theme=theme,
            css=css
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch()
