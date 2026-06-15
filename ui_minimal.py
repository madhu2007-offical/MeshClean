#!/usr/bin/env python
"""
Minimal Flask UI without Jinja2 - Pure HTML/JS with premium Data Engineer style
"""

from flask import Flask, jsonify
import traceback
import sys

# Force UTF-8 encoding on Windows standard output to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__, static_folder=None)

# Premium Observability Dashboard HTML
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MeshClean Observability Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: #090B0F;
  color: #C9D1D9;
  line-height: 1.5;
  overflow-x: hidden;
}

.container {
  max-width: 1500px;
  margin: 0 auto;
  padding: 24px;
}

/* Header Observatory Status */
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #21262D;
  margin-bottom: 24px;
}

.title-area h1 {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #F0F6FC;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-area h1 span.pulse {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #58A6FF;
  box-shadow: 0 0 8px #58A6FF;
  animation: beacon 2s infinite;
}

@keyframes beacon {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(88, 166, 255, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
}

.title-area p {
  color: #8B949E;
  font-size: 13px;
  margin-top: 2px;
}

.status-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 4px;
  background: #161B22;
  border: 1px solid #30363D;
  color: #8B949E;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: #0D1117;
  border: 1px solid #21262D;
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 90px;
}

.metric-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: #8B949E;
  letter-spacing: 0.5px;
}

.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 600;
  color: #F0F6FC;
  margin-top: 8px;
}

.text-success { color: #56D364 !important; }
.text-warning { color: #E3B341 !important; }
.text-danger { color: #F85149 !important; }
.text-info { color: #58A6FF !important; }

/* Main layout grid */
.layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}

/* Sidebar configs */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel {
  background: #0D1117;
  border: 1px solid #21262D;
  border-radius: 6px;
  padding: 18px;
}

.panel h2 {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: #58A6FF;
  margin-bottom: 14px;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

select {
  background: #161B22;
  border: 1px solid #30363D;
  color: #C9D1D9;
  padding: 8px 12px;
  border-radius: 4px;
  width: 100%;
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  outline: none;
}

select:focus {
  border-color: #58A6FF;
}

.error-details-box {
  background: #161B22;
  border: 1px solid #30363D;
  border-left: 3px solid #F85149;
  border-radius: 4px;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #FF7B72;
  min-height: 120px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.task-info-box {
  background: #161B22;
  border: 1px solid #30363D;
  border-radius: 4px;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #8B949E;
}

.action-btn {
  background: #238636;
  color: #FFFFFF;
  border: 1px solid rgba(240, 246, 252, 0.1);
  padding: 10px 18px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  width: 100%;
  transition: background 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn:hover {
  background: #2ea043;
}

.action-btn:disabled {
  background: #21262D;
  color: #8B949E;
  cursor: not-allowed;
  border-color: #30363D;
}

/* Loading indicators */
.loading-indicator {
  display: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #8B949E;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(88, 166, 255, 0.2);
  border-top-color: #58A6FF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Main Display Panels */
.main-display {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.grid-display {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media(max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
  .grid-display { grid-template-columns: 1fr; }
}

/* Premium Observability Terminal */
.terminal-window {
  background: #090D16;
  border: 1px solid #21262D;
  border-radius: 6px;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  height: 380px;
  overflow-y: auto;
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.85);
  position: relative;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  padding-bottom: 8px;
  border-bottom: 1px solid #1f242c;
  margin-bottom: 12px;
  color: #8B949E;
  font-size: 11px;
}

.terminal-line {
  margin-bottom: 6px;
  line-height: 1.6;
}

.text-cyan { color: #58A6FF; }
.text-blue { color: #79C0FF; }
.text-purple { color: #BC8CFF; }
.text-orange { color: #FFA657; }
.text-green { color: #56D364; }
.text-red { color: #FF7B72; }
.text-yellow { color: #E3B341; }
.text-muted { color: #8B949E; }
.font-bold { font-weight: 600; }

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 15px;
  background: #58A6FF;
  vertical-align: middle;
  margin-left: 4px;
  animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
  50% { opacity: 0; }
}

/* Premium DAG SVG rendering */
.graph-container-box {
  background: #090D16;
  border: 1px solid #21262D;
  border-radius: 6px;
  padding: 12px;
  height: 380px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

#dagSvg {
  width: 100%;
  height: 100%;
  display: block;
}

.node-group {
  cursor: pointer;
}

.node-card {
  fill: #161B22;
  stroke: #30363D;
  stroke-width: 1.5;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.node-group:hover .node-card {
  stroke: #58A6FF;
  fill: #1C212A;
}

.node-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 8px;
  font-weight: 700;
  fill: #8B949E;
  pointer-events: none;
}

.node-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  fill: #C9D1D9;
  pointer-events: none;
}

/* Node Type Colors */
.node-group.source .node-card { stroke: #38bdf8; fill: #0d1e2d; }
.node-group.source .node-badge { fill: #38bdf8; }
.node-group.source:hover .node-card { fill: #102d44; }

.node-group.branch .node-card { stroke: #818cf8; fill: #11142d; }
.node-group.branch .node-badge { fill: #818cf8; }
.node-group.branch:hover .node-card { fill: #191c42; }

.node-group.transform .node-card { stroke: #c084fc; fill: #1b122c; }
.node-group.transform .node-badge { fill: #c084fc; }
.node-group.transform:hover .node-card { fill: #281b42; }

.node-group.merge .node-card { stroke: #fb923c; fill: #27170c; }
.node-group.merge .node-badge { fill: #fb923c; }
.node-group.merge:hover .node-card { fill: #3a2212; }

.node-group.output .node-card { stroke: #f87171; fill: #2a1111; }
.node-group.output .node-badge { fill: #f87171; }
.node-group.output:hover .node-card { fill: #3d1919; }

/* Special highlighted states */
.node-group.inspected .node-card {
  stroke: #56D364;
  stroke-width: 2.5px;
}
.node-group.root-cause .node-card {
  stroke: #FF7B72;
  stroke-width: 3px;
  fill: #2d1316 !important;
}

/* Edge paths and flow animation */
.edge-path {
  stroke: #30363D;
  stroke-width: 2;
  fill: none;
  transition: stroke 0.3s ease;
}

.edge-flow {
  stroke: #58A6FF;
  stroke-width: 1.5;
  stroke-dasharray: 6, 6;
  fill: none;
  animation: edge-data-flow 1.5s linear infinite;
  opacity: 0.6;
}

@keyframes edge-data-flow {
  to { stroke-dashoffset: -24; }
}

.edge-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 8px;
  fill: #8B949E;
  text-anchor: middle;
}

/* Bottom details card */
.details-display-card {
  background: #0D1117;
  border: 1px solid #21262D;
  border-radius: 6px;
  padding: 18px;
}

.details-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.details-label {
  color: #8B949E;
  font-weight: 500;
}

.details-value {
  color: #C9D1D9;
}
</style>
</head>
<body>
<div class="container">
  <!-- Observatory Header -->
  <header>
    <div class="title-area">
      <h1><span class="pulse"></span> MeshClean Observability Console</h1>
      <p>Continuous Pipeline Diagnostic & Root Cause Telemetry</p>
    </div>
    <div class="status-badge">
      <span class="pulse" style="background:#56D364; box-shadow:0 0 6px #56D364; width:8px; height:8px;"></span>
      SYS_ENG: ONLINE
    </div>
  </header>

  <!-- Metrics Grid -->
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-label">System Health</div>
      <div class="metric-value text-success" id="healthVal">HEALTHY</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Step Count</div>
      <div class="metric-value" id="stepsVal">0 / 15</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Accumulative Reward</div>
      <div class="metric-value text-info" id="rewardVal">0.00</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Predicted Cause</div>
      <div class="metric-value text-warning" id="causeVal">NONE</div>
    </div>
  </div>

  <!-- Main Grid Workspace -->
  <div class="layout">
    <!-- Left Configs Column -->
    <div class="sidebar">
      <div class="panel">
        <h2><span>Configuration</span> <span class="text-muted" style="font-size:10px;" id="diffBadge">EASY</span></h2>
        <select id="taskSelect" onchange="updateTask()">
          <option value="task_1">Task 1: Missing Columns</option>
          <option value="task_2">Task 2: Precision Loss</option>
          <option value="task_3">Task 3: Duplicates at Source</option>
        </select>
      </div>

      <div class="panel">
        <h2>Observability Alert</h2>
        <div class="error-details-box" id="errorLog">Select a task configuration to load data logs.</div>
      </div>

      <div class="panel">
        <h2>Diagnostics Engine</h2>
        <button id="runBtn" class="action-btn" onclick="runDebugger()">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 010 1.393z"/>
          </svg>
          Launch Debug Agent
        </button>
        <div class="loading-indicator" id="loadingArea">
          <div class="spinner"></div>
          <span>Traversing DAG pipeline...</span>
        </div>
      </div>

      <div class="panel">
        <h2>Telemetry Reference</h2>
        <div class="task-info-box" id="taskInfo">Loading engine...</div>
      </div>
    </div>

    <!-- Right Telemetry Column -->
    <div class="main-display">
      <div class="grid-display">
        <!-- Terminal Column -->
        <div class="panel" style="padding:0; overflow:hidden;">
          <div class="terminal-window" id="terminalLogs">
            <div class="terminal-header">
              <span>bash - debug_agent@meshclean-node:~</span>
              <span>tty1</span>
            </div>
            <div class="terminal-line text-muted">Ready to initialize agent. Select a task and run.</div>
            <div class="terminal-cursor-line"><span class="terminal-cursor">_</span></div>
          </div>
        </div>

        <!-- DAG Visualizer Column -->
        <div class="graph-container-box">
          <h2 style="font-size:12px; font-weight:600; text-transform:uppercase; color:#58A6FF; padding: 6px 6px 10px 6px; border-bottom:1px solid #1f242c; margin-bottom:8px;">
            Pipeline Topology Map
          </h2>
          <div style="flex: 1; position: relative;">
            <svg id="dagSvg" viewBox="0 0 400 420" preserveAspectRatio="xMidYMid meet">
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#141923" stroke-width="0.5"/>
                </pattern>
                <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="21" refY="3" orient="auto">
                  <polygon points="0 0, 6 3, 0 6" fill="#58A6FF"/>
                </marker>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              <g id="edgesGroup"></g>
              <g id="nodesGroup"></g>
            </svg>
          </div>
        </div>
      </div>

      <!-- Bottom inspected node details panel -->
      <div class="details-display-card">
        <h2 style="font-size:12px; font-weight:600; text-transform:uppercase; color:#58A6FF; margin-bottom:12px;">Node Telemetry Inspector</h2>
        <div class="details-grid" id="inspectorContent">
          <div class="details-label">Select Node:</div>
          <div class="details-value">Click any node in the pipeline graph above to inspect its metadata and schema.</div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
let CURRENT_NODES_DATA = {};
let VISITED_NODES = new Set();
let ROOT_CAUSE_NODE = null;

const API = {
  task: url => fetch(url).then(r => r.json()),
  run: url => fetch(url).then(r => r.json())
};

function formatLogs(logText) {
  if (!logText) return '<div class="terminal-line text-muted">Ready to initialize agent. Select a task and run.</div>';
  const lines = logText.split('\\n');
  return lines.map(line => {
    let cls = 'terminal-line';
    if (line.includes('[START]') || line.includes('[END]')) cls += ' text-cyan font-bold';
    else if (line.includes('[INFO]')) cls += ' text-blue';
    else if (line.includes('action=inspect_node')) cls += ' text-purple';
    else if (line.includes('action=check_schema')) cls += ' text-orange';
    else if (line.includes('action=submit_root_cause')) cls += ' text-green font-bold';
    else if (line.includes('ERROR:') || line.includes('[FAIL]') || line.includes('result=INCORRECT')) cls += ' text-red';
    else if (line.includes('result=CORRECT')) cls += ' text-green';
    else if (line.includes('result=PARTIALLY')) cls += ' text-yellow';
    
    // Extract node highlighting from logs
    if (line.includes('action=inspect_node') || line.includes('action=check_schema')) {
      const match = line.match(/\\(([^)]+)\\)/);
      if (match && match[1]) {
        VISITED_NODES.add(match[1]);
      }
    }
    if (line.includes('action=submit_root_cause')) {
      const match = line.match(/\\(([^)]+)\\)/);
      if (match && match[1]) {
        ROOT_CAUSE_NODE = match[1];
      }
    }
    
    return `<div class="${cls}">${line}</div>`;
  }).join('') + '<div class="terminal-cursor-line"><span class="terminal-cursor">_</span></div>';
}

function layoutDAG(nodesDict) {
  const nodes = [];
  const edges = [];
  
  // Find source (node with no parents)
  const sourceId = Object.keys(nodesDict).find(id => !nodesDict[id].parents || nodesDict[id].parents.length === 0);
  if (!sourceId) return { nodes, edges };
  
  // Level 0: Source
  nodes.push({ id: sourceId, label: sourceId, type: 'source', x: 140, y: 30, w: 120, h: 42 });
  
  const sourceChildren = nodesDict[sourceId].children;
  if (sourceChildren && sourceChildren.length >= 2) {
    const bId = sourceChildren[0];
    const cId = sourceChildren[1];
    
    // Level 1: Branches
    nodes.push({ id: bId, label: bId, type: 'branch', x: 40, y: 110, w: 120, h: 42 });
    nodes.push({ id: cId, label: cId, type: 'branch', x: 240, y: 110, w: 120, h: 42 });
    
    edges.push({ from: sourceId, to: bId });
    edges.push({ from: sourceId, to: cId });
    
    // Level 2: Transforms
    const dId = nodesDict[bId].children ? nodesDict[bId].children[0] : null;
    const eId = nodesDict[cId].children ? nodesDict[cId].children[0] : null;
    if (dId && eId) {
      nodes.push({ id: dId, label: dId, type: 'transform', x: 40, y: 190, w: 120, h: 42 });
      nodes.push({ id: eId, label: eId, type: 'transform', x: 240, y: 190, w: 120, h: 42 });
      
      edges.push({ from: bId, to: dId });
      edges.push({ from: cId, to: eId });
      
      // Level 3: Merge
      const fId = nodesDict[dId].children ? nodesDict[dId].children[0] : null;
      if (fId) {
        nodes.push({ id: fId, label: fId, type: 'merge', x: 140, y: 270, w: 120, h: 42 });
        edges.push({ from: dId, to: fId });
        edges.push({ from: eId, to: fId });
        
        // Level 4: Output
        const outId = nodesDict[fId].children ? nodesDict[fId].children[0] : null;
        if (outId) {
          nodes.push({ id: outId, label: outId, type: 'output', x: 140, y: 350, w: 120, h: 42 });
          edges.push({ from: fId, to: outId });
        }
      }
    }
  }
  
  return { nodes, edges };
}

function drawGraph(nodesDict) {
  const { nodes, edges } = layoutDAG(nodesDict);
  
  const nodesGroup = document.getElementById('nodesGroup');
  const edgesGroup = document.getElementById('edgesGroup');
  
  nodesGroup.innerHTML = '';
  edgesGroup.innerHTML = '';
  
  // Draw edges
  edges.forEach(edge => {
    const parent = nodes.find(n => n.id === edge.from);
    const child = nodes.find(n => n.id === edge.to);
    if (!parent || !child) return;
    
    // Bottom center of parent
    const x1 = parent.x + parent.w / 2;
    const y1 = parent.y + parent.h;
    // Top center of child
    const x2 = child.x + child.w / 2;
    const y2 = child.y;
    
    const midY = (y1 + y2) / 2;
    const d = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
    
    // Edge path background line
    const pathBg = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathBg.setAttribute('d', d);
    pathBg.setAttribute('class', 'edge-path');
    pathBg.setAttribute('marker-end', 'url(#arrowhead)');
    edgesGroup.appendChild(pathBg);
    
    // Glowing edge animation flow
    const pathFlow = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathFlow.setAttribute('d', d);
    pathFlow.setAttribute('class', 'edge-flow');
    edgesGroup.appendChild(pathFlow);
  });
  
  // Draw nodes
  nodes.forEach(node => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    let extraCls = '';
    if (VISITED_NODES.has(node.id)) extraCls += ' inspected';
    if (ROOT_CAUSE_NODE === node.id) extraCls += ' root-cause';
    
    g.setAttribute('class', `node-group ${node.type}${extraCls}`);
    g.setAttribute('onclick', `inspectNode('${node.id}')`);
    
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', node.x);
    rect.setAttribute('y', node.y);
    rect.setAttribute('width', node.w);
    rect.setAttribute('height', node.h);
    rect.setAttribute('class', 'node-card');
    rect.setAttribute('rx', '5');
    
    const badge = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    badge.setAttribute('x', node.x + 8);
    badge.setAttribute('y', node.y + 15);
    badge.setAttribute('class', 'node-badge');
    badge.textContent = node.type.toUpperCase();
    
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', node.x + 8);
    text.setAttribute('y', node.y + 30);
    text.setAttribute('class', 'node-title');
    
    // Truncate label if too long
    let label = node.id;
    if (label.length > 18) label = label.substring(0, 15) + '...';
    text.textContent = label;
    
    g.appendChild(rect);
    g.appendChild(badge);
    g.appendChild(text);
    nodesGroup.appendChild(g);
  });
}

function inspectNode(nodeId) {
  const node = CURRENT_NODES_DATA[nodeId];
  if (!node) return;
  
  const container = document.getElementById('inspectorContent');
  
  let schemaHtml = '';
  if (node.schema_info) {
    schemaHtml = Object.keys(node.schema_info)
      .map(k => `  <span class="text-cyan">${k}</span>: <span class="text-orange">${node.schema_info[k]}</span>`)
      .join('<br>');
  }
  
  container.innerHTML = `
    <div class="details-label">Node ID:</div>
    <div class="details-value text-info font-bold">${node.node_id}</div>
    
    <div class="details-label">Type:</div>
    <div class="details-value"><span class="status-badge" style="display:inline-block; padding:1px 6px;">${node.node_type.toUpperCase()}</span></div>
    
    <div class="details-label">Description:</div>
    <div class="details-value">${node.description || 'No description.'}</div>
    
    <div class="details-label">Schema:</div>
    <div class="details-value task-info-box" style="margin-top:0; background:#090d16;">
${schemaHtml || '  No schema fields.'}
    </div>
  `;
}

function updateTask() {
  const id = document.getElementById('taskSelect').value;
  
  // Clear highlights
  VISITED_NODES.clear();
  ROOT_CAUSE_NODE = null;
  
  // Reset UI metrics
  document.getElementById('healthVal').textContent = 'DEGRADED';
  document.getElementById('healthVal').className = 'metric-value text-danger';
  document.getElementById('stepsVal').textContent = '0 / 15';
  document.getElementById('rewardVal').textContent = '0.00';
  document.getElementById('causeVal').textContent = 'NONE';
  document.getElementById('terminalLogs').innerHTML = `
    <div class="terminal-header">
      <span>bash - debug_agent@meshclean-node:~</span>
      <span>tty1</span>
    </div>
    <div class="terminal-line text-muted">Ready to initialize agent. Select a task and run.</div>
    <div class="terminal-cursor-line"><span class="terminal-cursor">_</span></div>
  `;
  
  API.task(`/task/${id}`).then(data => {
    if (data.error) {
      document.getElementById('errorLog').textContent = data.error;
    } else {
      document.getElementById('errorLog').textContent = data.error_log || 'No error logs logged.';
      
      const diffUpper = data.difficulty.toUpperCase();
      document.getElementById('diffBadge').textContent = diffUpper;
      if (diffUpper === 'EASY') document.getElementById('diffBadge').className = 'text-success';
      else if (diffUpper === 'MEDIUM') document.getElementById('diffBadge').className = 'text-warning';
      else document.getElementById('diffBadge').className = 'text-danger';
      
      document.getElementById('taskInfo').innerHTML = `Task: ${data.name}<br>Difficulty: ${data.difficulty.toUpperCase()}<br>Telemetry Nodes: ${data.num_nodes || 7}`;
      
      CURRENT_NODES_DATA = data.nodes || {};
      drawGraph(CURRENT_NODES_DATA);
      
      // Select source node by default in inspector
      const firstNodeId = Object.keys(CURRENT_NODES_DATA)[0];
      if (firstNodeId) inspectNode(firstNodeId);
    }
  }).catch(err => {
    document.getElementById('errorLog').textContent = 'Load failed: ' + err.message;
  });
}

function runDebugger() {
  const id = document.getElementById('taskSelect').value;
  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  document.getElementById('loadingArea').style.display = 'flex';
  
  // Reset highlights before run
  VISITED_NODES.clear();
  ROOT_CAUSE_NODE = null;
  
  API.run(`/run/${id}`).then(data => {
    if (data.error) {
      document.getElementById('errorLog').textContent = data.error;
    } else {
      // Parse execution terminal logs
      document.getElementById('terminalLogs').innerHTML = `
        <div class="terminal-header">
          <span>bash - debug_agent@meshclean-node:~</span>
          <span>tty1</span>
        </div>
        ${formatLogs(data.logs)}
      `;
      
      // Scroll to bottom of terminal
      const term = document.getElementById('terminalLogs');
      term.scrollTop = term.scrollHeight;
      
      // Update metrics
      const isCorrect = data.grade === 1.0;
      const healthEl = document.getElementById('healthVal');
      if (isCorrect) {
        healthEl.textContent = 'RESOLVED';
        healthEl.className = 'metric-value text-success';
      } else {
        healthEl.textContent = 'FAILED';
        healthEl.className = 'metric-value text-danger';
      }
      
      document.getElementById('stepsVal').textContent = `${data.steps} / 15`;
      document.getElementById('rewardVal').textContent = parseFloat(data.total_reward).toFixed(2);
      document.getElementById('causeVal').textContent = data.predicted || 'UNKNOWN';
      
      // Redraw graph with traversed highlights
      drawGraph(CURRENT_NODES_DATA);
      
      // Inspect the predicted cause
      if (data.predicted && CURRENT_NODES_DATA[data.predicted]) {
        inspectNode(data.predicted);
      }
    }
  }).catch(err => {
    document.getElementById('errorLog').textContent = 'Execution failed: ' + err.message;
  }).finally(() => {
    btn.disabled = false;
    document.getElementById('loadingArea').style.display = 'none';
  });
}

window.onload = updateTask;
</script>
</body>
</html>
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
        
        # Extract nodes details for JS SVG builder
        nodes_data = {}
        for node_id, node in env.state.current_task.nodes.items():
            nodes_data[node_id] = {
                'node_id': node.node_id,
                'node_type': node.node_type,
                'description': node.description,
                'schema_info': node.schema_info,
                'parents': node.parents,
                'children': node.children
            }
            
        return jsonify({
            'name': env.state.current_task.task_name,
            'difficulty': env.state.current_task.difficulty,
            'error_log': env.state.current_task.error_log,
            'num_nodes': len(env.state.current_task.nodes),
            'nodes': nodes_data,
            'error': None
        })
    except Exception as e:
        print(f"Task error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e), 
            'name': '', 
            'difficulty': '', 
            'error_log': '', 
            'num_nodes': 0,
            'nodes': {}
        }), 500

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
            'error': None,
            'predicted': predicted,
            'actual': actual,
            'grade': grade,
            'steps': result.get('steps', 0),
            'total_reward': result.get('total_reward', 0.0)
        })
    except Exception as e:
        print(f"Run error: {e}")
        traceback.print_exc()
        return jsonify({
            'logs': '',
            'analysis': '',
            'summary': '',
            'error': str(e),
            'predicted': 'Unknown',
            'actual': 'Unknown',
            'grade': 0.0,
            'steps': 0,
            'total_reward': 0.0
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[*] MeshClean Pipeline Debugging Environment")
    print("="*60)
    print("\nStarting Flask UI...")
    print("Open browser: http://localhost:7860")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)
