#!/usr/bin/env python
"""
Minimal Flask UI without Jinja2 - pure HTML/JS
"""

from flask import Flask, jsonify
import traceback

app = Flask(__name__, static_folder=None)

# Pre-load HTML
HTML = """<!DOCTYPE html>
<html><head>
<title>MeshClean Debugger</title>
<meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f0f0f;color:#d0d0d0;line-height:1.6}
.container{max-width:1400px;margin:0 auto;padding:24px}
header{margin-bottom:24px}
h1{font-size:20px;font-weight:600;margin-bottom:2px;letter-spacing:-0.5px}
p{color:#888;font-size:13px}
.layout{display:grid;grid-template-columns:35% 65%;gap:24px}
.panel{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;padding:18px}
.panel h2{font-size:12px;text-transform:uppercase;color:#4a9eff;margin-bottom:14px;letter-spacing:0.8px;font-weight:600}
select,textarea,button{font-family:'Monaco','Consolas',monospace;font-size:12px}
select,textarea{background:#0f0f0f;border:1px solid #2a2a2a;color:#d0d0d0;padding:10px;border-radius:4px;width:100%}
textarea{resize:vertical;line-height:1.6;letter-spacing:0.3px}
select{height:36px}
button{background:#4a9eff;color:white;padding:10px 18px;border:none;border-radius:4px;cursor:pointer;font-weight:500;font-size:13px}
button:hover{background:#357abd}
button:disabled{opacity:0.5;cursor:not-allowed}
.progress-container{margin-top:12px}
.progress-bar{width:100%;height:4px;background:#2a2a2a;border-radius:2px;overflow:hidden}
.progress-fill{height:100%;background:#4a9eff;width:0%;transition:width 0.3s ease;border-radius:2px}
.progress-text{font-size:11px;color:#888;margin-top:4px}
.error{display:none;color:#ff6b6b;font-size:13px;margin-top:12px;padding:10px;background:#1f1010;border-left:3px solid #ff6b6b;border-radius:2px}
.loading{display:none;color:#888;font-size:13px;margin-top:10px}
.right-column{display:grid;grid-auto-rows:fit-content;gap:24px}
.logs-section{grid-column:1}
.graph-section{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;padding:18px}
#graphContainer{width:100%;height:280px;position:relative;background:#0a0a0a;border-radius:4px;display:flex;align-items:center;justify-content:center;overflow:hidden}
svg{width:100%;height:100%;display:block}
.node-rect{fill:#1e3a5f;stroke:#4a9eff;stroke-width:2;rx:6}
.node-label{font-size:11px;text-anchor:middle;dominant-baseline:middle;fill:#e0e0e0;font-weight:600;pointer-events:none}
.edge-path{stroke:#4a9eff;stroke-width:2.5;fill:none;opacity:0.7;marker-end:url(#arrowhead)}
.edge-label{font-size:9px;fill:#888;text-anchor:middle}
#arrowhead{fill:#4a9eff}
.step-item{margin:8px 0;padding:8px;background:#0f0f0f;border-left:3px solid #2a2a2a;border-radius:2px;font-size:11px}
.step-number{color:#4a9eff;font-weight:600;min-width:45px;display:inline-block}
.step-action{color:#d0d0d0}
.step-reward{color:#88d498;font-weight:400}
.analysis-summary{display:grid;grid-template-columns:1fr 1fr;gap:24px}
@media(max-width:1200px){.layout{grid-template-columns:1fr}.analysis-summary{grid-template-columns:1fr}}
</style>
</head><body>
<div class="container">
<header>
<h1>MeshClean Debugger</h1>
<p>AI-powered root cause analysis for data pipelines</p>
</header>

<div class="layout">
<div style="display:flex;flex-direction:column;gap:24px">
<div class="panel">
<h2>Configuration</h2>
<select id="taskSelect" onchange="updateTask()">
<option value="task_1">Task 1: Easy</option>
<option value="task_2">Task 2: Medium</option>
<option value="task_3">Task 3: Hard</option>
</select>
</div>

<div class="panel">
<h2>Error Details</h2>
<textarea id="errorLog" readonly style="min-height:100px"></textarea>
</div>

<div class="panel">
<h2>Execution</h2>
<button id="runBtn" onclick="runDebugger()">Run Debugger</button>
<div id="loading" class="loading">Running...</div>
<div id="error" class="error"></div>
<div class="progress-container" id="progressContainer" style="display:none">
<div class="progress-bar">
<div class="progress-fill" id="progressFill"></div>
</div>
<div class="progress-text"><span id="progressText">0%</span> Complete</div>
</div>
</div>

<div class="panel">
<h2>Task Info</h2>
<textarea id="taskInfo" readonly style="min-height:100px"></textarea>
</div>
</div>

<div class="right-column">
<div class="panel logs-section">
<h2>Execution Steps</h2>
<div id="logs" style="height:380px;overflow-y:auto;font-family:'Monaco','Consolas',monospace;font-size:11px;line-height:1.6"></div>
</div>

<div class="panel graph-section">
<h2>Pipeline Graph</h2>
<div id="graphContainer"></div>
</div>

<div class="analysis-summary">
<div class="panel">
<h2>Analysis</h2>
<textarea id="analysis" readonly style="min-height:140px"></textarea>
</div>
<div class="panel">
<h2>Summary</h2>
<textarea id="summary" readonly style="min-height:140px"></textarea>
</div>
</div>
</div>
</div>
</div>

<script>
const API = {
  task: url => fetch(url).then(r => r.json()),
  run: url => fetch(url).then(r => r.json())
};

function showErr(msg) {
  const el = document.getElementById('error');
  el.textContent = 'Error: ' + msg;
  el.style.display = 'block';
}

function clearErr() {
  document.getElementById('error').style.display = 'none';
}

function formatLogs(logText) {
  if (!logText) return '';
  const lines = logText.split('\\n');
  return lines.map(line => {
    if (line.match(/^\\[STEP \\d+\\]/)) {
      return '<div class="step-item">' + line.replace(
        /^(\\[STEP \\d+\\])(.*?)(reward=.*)$/,
        '<span class="step-number">$1</span><span class="step-action">$2</span><span class="step-reward">$3</span>'
      ) + '</div>';
    }
    return '<div style="margin:4px 0;padding:4px;color:#888;font-size:11px">' + line + '</div>';
  }).join('');
}

function drawGraph(taskName) {
  const container = document.getElementById('graphContainer');
  
  // Advanced graph configurations per task
  const graphConfigs = {
    'Easy: Simple Linear Pipeline': {
      width: 320, height: 280,
      nodes: [
        {id: 'A_source', label: 'Data Source', x: 30, y: 140, w: 70, h: 50},
        {id: 'B_processor', label: 'Data Cleaner', x: 145, y: 140, w: 70, h: 50},
        {id: 'output', label: 'Output', x: 260, y: 140, w: 70, h: 50}
      ],
      edges: [
        {from: 'A_source', to: 'B_processor', label: 'clean'},
        {from: 'B_processor', to: 'output', label: 'validate'}
      ]
    },
    'Medium: ETL Pipeline': {
      width: 350, height: 280,
      nodes: [
        {id: 'extract', label: 'Extract', x: 20, y: 140, w: 60, h: 50},
        {id: 'transform', label: 'Transform', x: 110, y: 140, w: 60, h: 50},
        {id: 'validate', label: 'Validate', x: 200, y: 140, w: 60, h: 50},
        {id: 'output', label: 'Load', x: 290, y: 140, w: 60, h: 50}
      ],
      edges: [
        {from: 'extract', to: 'transform', label: 'parse'},
        {from: 'transform', to: 'validate', label: 'check'},
        {from: 'validate', to: 'output', label: 'store'}
      ]
    },
    'Complex DAG - Duplicate': {
      width: 340, height: 280,
      nodes: [
        {id: 'raw_data', label: 'Raw Data', x: 30, y: 140, w: 70, h: 50},
        {id: 'clean', label: 'Clean', x: 130, y: 80, w: 60, h: 50},
        {id: 'filter', label: 'Filter', x: 130, y: 190, w: 60, h: 50},
        {id: 'enrich', label: 'Enrich', x: 220, y: 80, w: 60, h: 50},
        {id: 'merge', label: 'Merge', x: 220, y: 190, w: 60, h: 50},
        {id: 'output', label: 'Output', x: 300, y: 140, w: 70, h: 50}
      ],
      edges: [
        {from: 'raw_data', to: 'clean', label: ''},
        {from: 'raw_data', to: 'filter', label: ''},
        {from: 'clean', to: 'enrich', label: ''},
        {from: 'filter', to: 'merge', label: ''},
        {from: 'enrich', to: 'output', label: ''},
        {from: 'merge', to: 'output', label: ''}
      ]
    }
  };
  
  const config = graphConfigs[taskName] || graphConfigs['Easy: Simple Linear Pipeline'];
  
  // Create SVG
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${config.width} ${config.height}`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  
  // Define arrow marker
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
  marker.setAttribute('id', 'arrowhead');
  marker.setAttribute('markerWidth', '10');
  marker.setAttribute('markerHeight', '10');
  marker.setAttribute('refX', '8');
  marker.setAttribute('refY', '3');
  marker.setAttribute('orient', 'auto');
  const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
  polygon.setAttribute('points', '0 0, 10 3, 0 6');
  polygon.setAttribute('fill', '#4a9eff');
  marker.appendChild(polygon);
  defs.appendChild(marker);
  svg.appendChild(defs);
  
  // Draw background grid
  const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  bg.setAttribute('width', config.width);
  bg.setAttribute('height', config.height);
  bg.setAttribute('fill', '#0a0a0a');
  svg.appendChild(bg);
  
  // Draw edges (connections)
  config.edges.forEach(edge => {
    const fromNode = config.nodes.find(n => n.id === edge.from);
    const toNode = config.nodes.find(n => n.id === edge.to);
    
    const x1 = fromNode.x + fromNode.w / 2;
    const y1 = fromNode.y + fromNode.h / 2;
    const x2 = toNode.x + toNode.w / 2;
    const y2 = toNode.y + toNode.h / 2;
    
    // Draw connection line
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const midX = (x1 + x2) / 2;
    const d = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
    path.setAttribute('d', d);
    path.setAttribute('class', 'edge-path');
    svg.appendChild(path);
  });
  
  // Draw nodes
  config.nodes.forEach(node => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', node.x);
    rect.setAttribute('y', node.y);
    rect.setAttribute('width', node.w);
    rect.setAttribute('height', node.h);
    rect.setAttribute('class', 'node-rect');
    svg.appendChild(rect);
    
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', node.x + node.w / 2);
    label.setAttribute('y', node.y + node.h / 2);
    label.setAttribute('class', 'node-label');
    label.textContent = node.label;
    svg.appendChild(label);
  });
  
  container.innerHTML = '';
  container.appendChild(svg);
}

function updateTask() {
  const id = document.getElementById('taskSelect').value;
  clearErr();
  API.task(`/task/${id}`).then(data => {
    if (data.error) {
      showErr(data.error);
    } else {
      document.getElementById('errorLog').value = data.error_log || 'No error';
      document.getElementById('taskInfo').value = `Task: ${data.name}\\nDifficulty: ${data.difficulty.toUpperCase()}\\nNodes: ${data.num_nodes || 3}`;
      drawGraph(data.name);
    }
  }).catch(err => showErr('Load failed: ' + err.message));
}

function runDebugger() {
  const id = document.getElementById('taskSelect').value;
  const btn = document.getElementById('runBtn');
  clearErr();
  btn.disabled = true;
  document.getElementById('loading').style.display = 'block';
  document.getElementById('progressContainer').style.display = 'block';
  
  API.run(`/run/${id}`).then(data => {
    if (data.error) {
      showErr(data.error);
    } else {
      document.getElementById('logs').innerHTML = formatLogs(data.logs) || '<div style="color:#888">No steps</div>';
      document.getElementById('analysis').value = data.analysis || '';
      document.getElementById('summary').value = data.summary || '';
      document.getElementById('progressFill').style.width = '100%';
      document.getElementById('progressText').textContent = '100%';
    }
  }).catch(err => showErr('Execution failed: ' + err.message))
    .finally(() => {
      btn.disabled = false;
      document.getElementById('loading').style.display = 'none';
    });
}

window.onload = updateTask;
</script>
</body></html>
"""

@app.route('/')
def index():
    return HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/task/<task_id>')
def get_task(task_id):
    try:
        from pipeline_debug_env import PipelineDebugEnv
        env = PipelineDebugEnv(task_id)
        env.reset()
        return jsonify({
            'name': env.state.current_task.task_name,
            'difficulty': env.state.current_task.difficulty,
            'error_log': env.state.current_task.error_log,
            'num_nodes': len(env.state.current_task.nodes),
            'error': None
        })
    except Exception as e:
        print(f"Task error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'name': '', 'difficulty': '', 'error_log': '', 'num_nodes': 0}), 500

@app.route('/run/<task_id>')
def run(task_id):
    try:
        from inference import DebugAgent
        agent = DebugAgent(task_id)
        result = agent.run()
        
        # Get actions (step history)
        actions = result.get('actions', [])
        logs = '\n'.join(actions) if isinstance(actions, list) else str(actions)
        
        predicted = result.get('predicted_root_cause', 'Unknown')
        actual = result.get('correct_root_cause', 'Unknown')
        grade = result.get('grade', 0.0)
        
        analysis = f"Predicted: {predicted}\nActual: {actual}\nGrade: {grade:.1%}"
        summary = f"Total Reward: {result.get('total_reward', 0):.2f}\nSteps: {result.get('steps', 0)}\nGrade: {grade:.1%}"
        
        return jsonify({
            'logs': logs,
            'analysis': analysis,
            'summary': summary,
            'error': None
        })
    except Exception as e:
        print(f"Run error: {e}")
        traceback.print_exc()
        return jsonify({
            'logs': '',
            'analysis': '',
            'summary': '',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[*] MeshClean Pipeline Debugging Environment")
    print("="*60)
    print("\nStarting Flask UI (Minimal)...")
    print("Open browser: http://localhost:7860")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)
