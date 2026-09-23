#!/usr/bin/env python
"""
MeshClean Enterprise Observability Console & Autonomous Debugger
Top-tier enterprise data platform style (Datadog / Snowflake / Dagster)
"""

import time
import io
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import gradio as gr

# Force UTF-8 encoding on Windows standard output
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Task mappings supporting both rich labels and short identifiers
TASK_MAP = {
    "🟢 Easy: Linear Pipeline (3 Nodes)": "task_1",
    "🟡 Medium: Branching ETL (7 Nodes)": "task_2",
    "🔴 Hard: Convergent DAG + Decoy (8 Nodes)": "task_3",
    "Easy": "task_1",
    "Medium": "task_2",
    "Hard": "task_3"
}

TASK_METADATA = {
    "task_1": {
        "title": "Simple Linear Pipeline",
        "difficulty": "Easy",
        "badge_color": "#10B981",
        "nodes": 3,
        "topology": "Direct Sequential (A -> B -> Out)",
        "scenario": "Missing values or null record dropping in upstream ingestion causing downstream row count discrepancy.",
        "fault_type": "Schema / Ingestion Anomaly"
    },
    "task_2": {
        "title": "Branching Pipeline with Merge",
        "difficulty": "Medium",
        "badge_color": "#F59E0B",
        "nodes": 7,
        "topology": "Dual-Branch Diamond Merge",
        "scenario": "Transformation stage introduces numeric type precision loss or column alias collision before terminal merge.",
        "fault_type": "Type Casting & Alias Drift"
    },
    "task_3": {
        "title": "Complex Multi-Path DAG",
        "difficulty": "Hard",
        "badge_color": "#EF4444",
        "nodes": 8,
        "topology": "Multi-Convergence DAG with Decoys",
        "scenario": "Comprises a genuine upstream root-cause fault accompanied by an independent downstream decoy error.",
        "fault_type": "Corrupted Upstream Source + Decoy"
    }
}

# ============================================================================
# GRAPH VISUALIZATION GENERATOR
# ============================================================================

def get_dag_positions(task):
    """Compute symmetric, hierarchical layout coordinates for any pipeline DAG"""
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
        y = float(max_layer - layer) * 2.2
        n_nodes = len(nodes_in_layer)
        for i, node in enumerate(sorted(nodes_in_layer)):
            if n_nodes == 1:
                x = 0.0
            else:
                x = (i - (n_nodes - 1) / 2.0) * 2.5
            pos[node] = (x, y)
            
    for nid in task.nodes:
        if nid not in pos:
            pos[nid] = (0.0, 0.0)
            
    return pos

def draw_dag_image(task, current_node=None, visited_nodes=None, predicted_node=None, actual_root_cause=None, show_result=False):
    """Render high-DPI executive DAG topology visualization with dark glass styling"""
    if visited_nodes is None:
        visited_nodes = set()
        
    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=140, facecolor='#0B0F19')
    ax.set_facecolor('#0B0F19')
    
    G = nx.DiGraph()
    for nid, node in task.nodes.items():
        G.add_node(nid)
        for child in node.children:
            G.add_edge(nid, child)
            
    pos = get_dag_positions(task)
    if not pos or any(node not in pos for node in G.nodes()):
        pos = nx.spring_layout(G)
        
    # Draw sleek directional edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color='#334155',
        width=2.0,
        arrows=True,
        arrowstyle='-|>',
        arrowsize=16,
        connectionstyle='arc3,rad=0.04',
        node_size=1200
    )
    
    # Outer glow halo for active / visited nodes
    halo_colors = []
    halo_sizes = []
    for node in G.nodes():
        if show_result and node == actual_root_cause:
            halo_colors.append('#10B98166')  # Emerald glow
            halo_sizes.append(1800)
        elif node == current_node:
            halo_colors.append('#EF444466')  # Rose glow
            halo_sizes.append(1800)
        elif node in visited_nodes:
            halo_colors.append('#F59E0B44')  # Amber glow
            halo_sizes.append(1500)
        else:
            halo_colors.append('#1E293B00')  # Transparent
            halo_sizes.append(1200)
            
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=halo_colors,
        node_size=halo_sizes,
        linewidths=0
    )
    
    # Main node core colors
    node_colors = []
    edge_colors = []
    for node in G.nodes():
        if show_result and node == actual_root_cause:
            node_colors.append('#059669')  # Confirmed Root Cause (Green)
            edge_colors.append('#34D399')
        elif node == current_node:
            node_colors.append('#DC2626')  # Active Probe / Error Symptom (Red)
            edge_colors.append('#F87171')
        elif node in visited_nodes:
            node_colors.append('#D97706')  # Inspected Stage (Amber)
            edge_colors.append('#FBBF24')
        else:
            node_colors.append('#1E293B')  # Healthy Upstream Stage (Slate)
            edge_colors.append('#38BDF8')
            
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=1100,
        edgecolors=edge_colors,
        linewidths=2.2
    )
    
    # Dual-line labels: Node ID + Stage Role Badge
    labels = {}
    for nid, node in task.nodes.items():
        role = node.node_type.upper().replace('_', ' ')
        if nid == 'output':
            role = 'OUTPUT'
        elif 'source' in nid.lower() or node.node_type == 'data_source':
            role = 'SOURCE'
        elif 'merge' in nid.lower():
            role = 'MERGE'
        else:
            role = 'STAGE'
        labels[nid] = f"{nid}\n[{role}]"
        
    nx.draw_networkx_labels(
        G, pos, labels=labels, ax=ax,
        font_size=7.5,
        font_color='#F8FAFC',
        font_family='sans-serif',
        font_weight='bold'
    )
    
    ax.axis('off')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=140, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

# ============================================================================
# REMEDIATION ADVISOR
# ============================================================================

def get_remediation_plan(task_id, root_cause_node):
    """Generate prescriptive Data Engineering remediation strategy & code patch"""
    remediations = {
        "task_1": f"""### 🛠️ Production Remediation: Upstream Null Audit & Imputation
**Root Cause Node:** `{root_cause_node}`
**Failure Category:** Dropped Records / Data Loss Discrepancy

```python
# Remediation in Data Cleaning Stage
# Replace aggressive row drops with deterministic default imputation
df_cleaned = df.fillna({{
    'name': 'UNKNOWN_ENTITY',
    'value': df['value'].median()
}})

# Add schema validation assertion
assert len(df_cleaned) == len(df), f"Critical: {{len(df) - len(df_cleaned)}} rows dropped at {root_cause_node}"
```

**Production Action Items:**
1. Deploy data quality pre-flight checks at `{root_cause_node}` using Great Expectations or Soda.
2. Route dropped records to a quarantine dead-letter table instead of silently discarding.""",
        "task_2": f"""### 🛠️ Production Remediation: Schema Type Coercion & Precision Safeguard
**Root Cause Node:** `{root_cause_node}`
**Failure Category:** Type Mismatch / Precision Truncation

```python
# Explicit type casting at ingestion boundary
from pyspark.sql.types import DecimalType

df_aligned = df.withColumn(
    'amount',
    df['amount'].cast(DecimalType(18, 4))
)

# Harmonize column naming before merge stage
df_aligned = df_aligned.withColumnRenamed('amt_clean', 'amount')
```

**Production Action Items:**
1. Enforce strict Pydantic / Great Expectations schema contracts before the merge stage.
2. Reconcile decimal separator locale handling in upstream parser.""",
        "task_3": f"""### 🛠️ Production Remediation: Deduplication & Cardinality Check
**Root Cause Node:** `{root_cause_node}`
**Failure Category:** Primary Key Duplication & Downstream Decoy Noise

```python
# Deduplicate on business primary key with audit watermark
df_deduped = df.dropDuplicates(subset=['customer_id', 'date'])

# Verify join cardinality before merge
cardinality_check = df_deduped.groupBy('customer_id').count().filter('count > 1')
if cardinality_check.count() > 0:
    raise ValueError(f"Cardinality violation detected at {root_cause_node}")
```

**Production Action Items:**
1. Apply deduplication window at ingestion source `{root_cause_node}` before branching.
2. Ignore downstream decoy warning at secondary processor — it is a symptom of duplicate fan-out."""
    }
    return remediations.get(task_id, f"Diagnosis completed. Apply schema and cardinality validation at node `{root_cause_node}`.")

# ============================================================================
# EVENT HANDLERS & STEP GENERATOR
# ============================================================================

def on_task_change(task_name):
    """Handle task selection and return initial reset values"""
    task_id = TASK_MAP.get(task_name, "task_1")
    from pipeline_debug_env import PipelineDebugEnv
    env = PipelineDebugEnv(task_id)
    obs = env.reset()
    task = env.state.current_task
    meta = TASK_METADATA.get(task_id, {})
    
    initial_img = draw_dag_image(task, current_node=task.start_node)
    
    meta_html = f"""
    <div class="meta-card">
        <div class="meta-header">
            <span class="meta-badge" style="background: {meta.get('badge_color', '#3B82F6')}22; color: {meta.get('badge_color', '#3B82F6')}; border: 1px solid {meta.get('badge_color', '#3B82F6')}44;">
                {meta.get('difficulty', 'Normal')}
            </span>
            <span class="meta-nodes">● {meta.get('nodes', 0)} Pipeline Nodes</span>
            <span class="meta-topo">● {meta.get('topology', '')}</span>
        </div>
        <p class="meta-desc">{meta.get('scenario', '')}</p>
        <div class="meta-footer">
            <span class="meta-key">Injected Fault Domain:</span> <code>{meta.get('fault_type', 'General')}</code>
        </div>
    </div>
    """
    
    init_logs = (
        f"[SYSTEM] Pipeline mounted: {meta.get('title', task_name)}\n"
        f"[SYSTEM] Failure detected at terminal node '{obs.current_node}'\n"
        f"[SYSTEM] Autonomous heuristic agent ready. Click '▶ Run Autonomous Debugger' to start traversal."
    )
    
    init_analysis = (
        f"### 🎯 Initial Pipeline Triage\n"
        f"- **Terminal Failure Detected At:** `{obs.current_node}`\n"
        f"- **Pipeline Symptoms:** Pipeline output breached data quality expectations.\n"
        f"- **Exploration Plan:** Systematic backward DAG traversal from terminal output node toward root data sources."
    )
    
    return (
        task.error_log,
        initial_img,
        init_logs,
        init_analysis,
        0,
        meta_html,
        "--",
        "0",
        "0.00",
        "Ready",
        "Awaiting autonomous debugging run to generate remediation blueprint..."
    )

def run_debug_generator(task_name):
    """Step-by-step generator yielding live updates to the Gradio UI"""
    task_id = TASK_MAP.get(task_name, "task_1")
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
    
    logs.append(f"[INIT] Mounted pipeline '{task.task_name}'")
    logs.append(f"[ALERT] Terminal error caught at node '{obs.current_node}'")
    logs.append(f"[PLAN] Backward traversal plan: {' -> '.join(strategy_plan)}")
    visited.add(obs.current_node)
    
    img = draw_dag_image(task, current_node=obs.current_node, visited_nodes=visited)
    analysis = (
        f"### 🔍 Phase 1: Failure Localization\n"
        f"- **Inspecting:** `{obs.current_node}`\n"
        f"- **Hypothesis:** Pipeline failed at terminal node; initiating upstream dependency walk."
    )
    
    yield (
        "\n".join(logs),
        img,
        analysis,
        5,
        "--",
        "0",
        "0.00",
        "Diagnosing...",
        "Evaluating pipeline telemetry..."
    )
    time.sleep(0.8)
    
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
            
            logs.append(f"[STEP {step}] inspect_node({node}) -> reward: {reward:+.2f} | total: {total_reward:+.2f}")
            progress = min(90, int((step / (len(strategy_plan) + 2)) * 100))
            
            img = draw_dag_image(task, current_node=node, visited_nodes=visited)
            analysis = (
                f"### 🔍 Step {step}: Probing `{node}`\n"
                f"- **Node Role:** `{obs.node_type}`\n"
                f"- **Parents:** `{obs.parents if obs.parents else 'None (Root Source)'}`\n"
                f"- **Observation:** Validating transformation invariants and parent schemas."
            )
            
            yield (
                "\n".join(logs),
                img,
                analysis,
                progress,
                f"Probing {node}...",
                str(step),
                f"{total_reward:+.2f}",
                "In Progress",
                "Observing intermediate stage outputs..."
            )
            time.sleep(0.7)
            
            # Action 2: Check schema
            if node in obs.parents or obs.node_type == "data_source":
                step += 1
                action_result = env.step({
                    "action_type": "check_schema",
                    "node": node
                })
                reward = action_result.reward
                total_reward += reward
                
                logs.append(f"[STEP {step}] check_schema({node}) -> reward: {reward:+.2f} | total: {total_reward:+.2f}")
                progress = min(90, int((step / (len(strategy_plan) + 2)) * 100))
                
                img = draw_dag_image(task, current_node=node, visited_nodes=visited)
                analysis = (
                    f"### 📋 Step {step}: Schema Validation on `{node}`\n"
                    f"- **Schema Integrity:** Checked column names and data types.\n"
                    f"- **Result:** Audited schema alignment against downstream consumption expectations."
                )
                
                yield (
                    "\n".join(logs),
                    img,
                    analysis,
                    progress,
                    f"Checking schema...",
                    str(step),
                    f"{total_reward:+.2f}",
                    "In Progress",
                    "Auditing field definitions and nullability..."
                )
                time.sleep(0.7)
                
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
    grade = info.get('grade', 0.0)
    result_text = info.get('result', 'UNKNOWN')
    
    logs.append(f"[DIAGNOSIS] submit_root_cause({predicted_root_cause}) -> {result_text}")
    logs.append(f"[SUMMARY] Final Diagnostic Score: {grade:.0%} | Total Exploration Reward: {total_reward:+.2f}")
    
    img = draw_dag_image(
        task, 
        current_node=predicted_root_cause, 
        visited_nodes=visited, 
        predicted_node=predicted_root_cause, 
        actual_root_cause=actual_cause, 
        show_result=True
    )
    
    analysis = (
        f"### 🎯 Root Cause Confirmed\n"
        f"- **Diagnosed Root Cause:** `{predicted_root_cause}`\n"
        f"- **Actual Fault Injection Point:** `{actual_cause}`\n"
        f"- **Diagnostic Accuracy:** **{grade:.0%}** ({result_text})\n"
        f"- **Efficiency:** Finished in **{step} steps** with **{total_reward:+.2f}** cumulative reward."
    )
    
    grade_label = f"🎯 {grade:.0%} ({result_text})"
    remediation_text = get_remediation_plan(task_id, predicted_root_cause)
    
    yield (
        "\n".join(logs),
        img,
        analysis,
        100,
        predicted_root_cause,
        str(step),
        f"{total_reward:+.2f}",
        grade_label,
        remediation_text
    )

# ============================================================================
# BUILD INTERFACE
# ============================================================================

def build_interface():
    """Build the enterprise-grade Gradio interface adhering to strict observability design standards"""
    css_styles = """
    /* Design Tokens */
    :root {
        --bg-canvas: #090B0F;
        --bg-surface: #111827;
        --bg-surface-elevated: #161F30;
        --border-subtle: #1F2937;
        --border-active: #3B82F6;
        --text-primary: #F9FAFB;
        --text-secondary: #9CA3AF;
        --accent-blue: #3B82F6;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #EF4444;
    }
    
    body, .gradio-container {
        background-color: #090B0F !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: #C9D1D9 !important;
        max-width: 1560px !important;
        margin: 0 auto !important;
    }
    
    /* Header Observatory Banner */
    .company-header {
        background: linear-gradient(180deg, #111827 0%, #0D131F 100%);
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .company-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .company-title {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .company-subtitle {
        font-size: 13px;
        color: #8B949E;
        margin-top: 2px;
    }
    
    .pulse-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10B981;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 9999px;
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: beacon 2s infinite;
    }
    
    @keyframes beacon {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 14px #10B981; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }
    
    /* Panel Cards */
    .panel-card {
        background: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
    }
    
    .panel-header-title {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        color: #58A6FF !important;
        margin-bottom: 12px !important;
        text-transform: uppercase !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    
    /* Metadata card */
    .meta-card {
        background: #0D131F;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 14px;
    }
    
    .meta-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    
    .meta-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    
    .meta-nodes, .meta-topo {
        font-size: 11px;
        color: #8B949E;
    }
    
    .meta-desc {
        font-size: 12px;
        line-height: 1.5;
        color: #C9D1D9;
        margin-bottom: 8px;
    }
    
    .meta-footer {
        font-size: 11px;
        color: #8B949E;
        border-top: 1px solid #1F2937;
        padding-top: 6px;
    }
    
    .meta-footer code {
        color: #F59E0B;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Terminal logs */
    .terminal-box textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        background-color: #06090E !important;
        color: #E6EDF3 !important;
        border: 1px solid #21262D !important;
        border-radius: 6px !important;
        line-height: 1.6 !important;
    }
    
    /* Buttons */
    .btn-run {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    
    .btn-run:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-1px) !important;
    }
    
    /* KPI Metric Cards */
    .kpi-row {
        margin-bottom: 16px;
    }
    
    /* Legend pill */
    .legend-bar {
        display: flex;
        justify-content: center;
        gap: 16px;
        padding: 8px;
        background: #0D131F;
        border: 1px solid #1F2937;
        border-radius: 6px;
        font-size: 11px;
        color: #8B949E;
        margin-top: 8px;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    """
    
    with gr.Blocks(title="MeshClean | Pipeline Observability") as app:
        app._custom_theme = gr.themes.Default(primary_hue="blue", neutral_hue="slate")
        app._custom_css = css_styles
        
        # Enterprise Header
        gr.HTML("""
        <div class="company-header">
            <div class="company-logo">
                <div>
                    <div class="company-title">
                        🛡️ MeshClean <span style="font-weight: 300; color: #58A6FF;">Observability</span>
                    </div>
                    <div class="company-subtitle">
                        Autonomous Data Pipeline Debugging & Root-Cause Remediation Engine
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <div class="pulse-badge">
                    <span class="pulse-dot"></span>
                    <span>ONLINE • AGENT ACTIVE</span>
                </div>
            </div>
        </div>
        """)
        
        # KPI Metric Summary Row
        with gr.Row(elem_classes=["kpi-row"]):
            with gr.Column(scale=1):
                grade_out = gr.Textbox(
                    value="Ready", 
                    label="🎯 Diagnostic Accuracy", 
                    interactive=False
                )
            with gr.Column(scale=1):
                root_cause_out = gr.Textbox(
                    value="--", 
                    label="🔍 Root Cause Node", 
                    interactive=False
                )
            with gr.Column(scale=1):
                steps_out = gr.Textbox(
                    value="0", 
                    label="⏱️ Exploration Steps", 
                    interactive=False
                )
            with gr.Column(scale=1):
                reward_out = gr.Textbox(
                    value="0.00", 
                    label="💎 Cumulative Reward", 
                    interactive=False
                )
                
        with gr.Row():
            # LEFT PANEL (Control & Configuration - 32%)
            with gr.Column(scale=32):
                gr.Markdown("<div class='panel-header-title'>⚡ PIPELINE CONFIGURATION</div>")
                
                task_select = gr.Radio(
                    choices=[
                        "🟢 Easy: Linear Pipeline (3 Nodes)",
                        "🟡 Medium: Branching ETL (7 Nodes)",
                        "🔴 Hard: Convergent DAG + Decoy (8 Nodes)"
                    ],
                    value="🟢 Easy: Linear Pipeline (3 Nodes)",
                    label="Debugging Scenario Selection",
                    info="Select target pipeline architecture and error injection difficulty"
                )
                
                meta_html_box = gr.HTML()
                
                gr.Markdown("<div class='panel-header-title' style='margin-top: 16px;'>⚠️ INJECTED FAILURE TELEMETRY</div>")
                
                error_log = gr.Textbox(
                    value="",
                    label="Terminal Failure Log Trace",
                    interactive=False,
                    lines=5,
                    elem_classes=["terminal-box"]
                )
                
                run_btn = gr.Button("▶ Run Autonomous Debugger", variant="primary", elem_classes=["btn-run"])
                
                progress_bar = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    label="Agent Exploration Progress (%)",
                    interactive=False
                )
                
            # RIGHT PANEL (Observability & Diagnosis - 68%)
            with gr.Column(scale=68):
                with gr.Row():
                    # Left subcolumn: DAG Canvas
                    with gr.Column(scale=50):
                        gr.Markdown("<div class='panel-header-title'>🗺️ PIPELINE TOPOLOGY & PROBE TRAVERSAL</div>")
                        
                        viz_output = gr.Image(
                            label="Live Pipeline Graph",
                            interactive=False
                        )
                        
                        gr.HTML("""
                        <div class="legend-bar">
                            <span class="legend-item"><span class="legend-dot" style="background:#38BDF8;"></span> Healthy Node</span>
                            <span class="legend-item"><span class="legend-dot" style="background:#F59E0B;"></span> Inspected Stage</span>
                            <span class="legend-item"><span class="legend-dot" style="background:#EF4444;"></span> Failure Probe</span>
                            <span class="legend-item"><span class="legend-dot" style="background:#10B981;"></span> Root Cause</span>
                        </div>
                        """)
                        
                    # Right subcolumn: Live Reasoning & Thought Terminal
                    with gr.Column(scale=50):
                        gr.Markdown("<div class='panel-header-title'>💻 AGENT THOUGHT STREAM & EXECUTION LOGS</div>")
                        
                        logs_output = gr.Textbox(
                            label="Telemetry Log Stream",
                            interactive=False,
                            lines=9,
                            elem_classes=["terminal-box"],
                            placeholder="Awaiting pipeline debugging run..."
                        )
                        
                        analysis_output = gr.Markdown(
                            value="### 🎯 Initial Pipeline Triage\nAwaiting debugging session start."
                        )
                        
                # Remediation Section
                with gr.Accordion("🛠️ Prescriptive Data Engineering Remediation Plan", open=True):
                    remediation_box = gr.Markdown(
                        value="Run the debugger to generate an automated schema and code remediation plan."
                    )
                    
        # Event bindings
        task_select.change(
            on_task_change,
            inputs=[task_select],
            outputs=[
                error_log,
                viz_output,
                logs_output,
                analysis_output,
                progress_bar,
                meta_html_box,
                root_cause_out,
                steps_out,
                reward_out,
                grade_out,
                remediation_box
            ]
        )
        
        run_btn.click(
            run_debug_generator,
            inputs=[task_select],
            outputs=[
                logs_output,
                viz_output,
                analysis_output,
                progress_bar,
                root_cause_out,
                steps_out,
                reward_out,
                grade_out,
                remediation_box
            ]
        )
        
        app.load(
            on_task_change,
            inputs=[task_select],
            outputs=[
                error_log,
                viz_output,
                logs_output,
                analysis_output,
                progress_bar,
                meta_html_box,
                root_cause_out,
                steps_out,
                reward_out,
                grade_out,
                remediation_box
            ]
        )
        
    return app

# ============================================================================
# LAUNCHER
# ============================================================================

def launch():
    """Launch the enterprise UI"""
    try:
        print("\n" + "="*60)
        print("MESHCLEAN ENTERPRISE OBSERVABILITY CONSOLE")
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
