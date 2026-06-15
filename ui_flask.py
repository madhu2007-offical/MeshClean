#!/usr/bin/env python
"""
Simple Flask-based UI alternative
This replaces Gradio with Flask for better Windows compatibility
"""

from flask import Flask, render_template_string, request, jsonify
import json
import threading
import time
import sys

# Force UTF-8 encoding on Windows standard output to avoid UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)

# Cache task data
TASK_CACHE = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MeshClean Debugger</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { padding: 20px 0; border-bottom: 1px solid #333; margin-bottom: 20px; }
        h1 { font-size: 24px; margin-bottom: 5px; }
        p { color: #999; font-size: 14px; }
        .layout { display: grid; grid-template-columns: 30% 70%; gap: 20px; }
        .panel { background: #222; border: 1px solid #333; border-radius: 8px; padding: 20px; }
        .panel h2 { font-size: 14px; text-transform: uppercase; color: #4a9eff; margin-bottom: 12px; letter-spacing: 1px; }
        select, button, textarea { background: #333; border: 1px solid #444; color: #e0e0e0; padding: 8px 12px; border-radius: 4px; font-family: monospace; }
        button { background: #4a9eff; color: white; cursor: pointer; border: none; padding: 10px 20px; }
        button:hover { background: #357abd; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        textarea { width: 100%; resize: vertical; }
        .output { margin-top: 15px; padding: 12px; background: #1a1a1a; border-left: 3px solid #4a9eff; font-size: 12px; line-height: 1.6; }
        .loading { display: none; color: #999; font-size: 13px; margin-top: 10px; }
        .error { color: #ff6b6b; }
        .success { color: #51cf66; }
        .right-sections { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .panel textarea { min-height: 150px; }
        @media (max-width: 1024px) { .right-sections { grid-template-columns: 1fr; } .layout { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 MeshClean Debugger</h1>
            <p>AI-Powered Data Pipeline Debugging Environment</p>
        </header>
        
        <div class="layout">
            <!-- LEFT PANEL -->
            <div>
                <div class="panel">
                    <h2>Task Configuration</h2>
                    <select id="taskSelect" onchange="updateTask()">
                        <option value="task_1">Task 1 - Easy</option>
                        <option value="task_2">Task 2 - Medium</option>
                        <option value="task_3">Task 3 - Hard</option>
                    </select>
                </div>
                
                <div class="panel" style="margin-top:15px;">
                    <h2>Error Log</h2>
                    <textarea id="errorLog" rows="6" readonly></textarea>
                </div>
                
                <div class="panel" style="margin-top:15px;">
                    <h2>Execution</h2>
                    <button id="runBtn" onclick="runDebugger()">Run Debugger</button>
                    <div id="loading" class="loading">🔄 Running...</div>
                    <div id="error" style="display:none; margin-top:10px; color:#ff6b6b;"></div>
                </div>
                
                <div class="panel" style="margin-top:15px;">
                    <h2>Task Information</h2>
                    <textarea id="taskInfo" rows="3" readonly></textarea>
                </div>
            </div>
            
            <!-- RIGHT PANEL -->
            <div>
                <div class="panel">
                    <h2>Debugging Process</h2>
                    <textarea id="logs" rows="12" readonly></textarea>
                </div>
                
                <div class="right-sections">
                    <div class="panel">
                        <h2>Agent Analysis</h2>
                        <textarea id="analysis" rows="10" readonly></textarea>
                    </div>
                    
                    <div class="panel">
                        <h2>Result Summary</h2>
                        <textarea id="summary" rows="10" readonly></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showError(msg) {
            document.getElementById('error').textContent = '❌ Error: ' + msg;
            document.getElementById('error').style.display = 'block';
        }
        
        function clearError() {
            document.getElementById('error').style.display = 'none';
        }
        
        function updateTask() {
            const taskId = document.getElementById('taskSelect').value;
            clearError();
            
            fetch(`/api/task/${taskId}`)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .then(data => {
                    document.getElementById('errorLog').value = data.error_log || 'No error log';
                    document.getElementById('taskInfo').value = `Task: ${data.name}\\nDifficulty: ${data.difficulty.toUpperCase()}`;
                })
                .catch(err => showError('Failed to load task: ' + err.message));
        }
        
        function runDebugger() {
            const taskId = document.getElementById('taskSelect').value;
            const btn = document.getElementById('runBtn');
            
            btn.disabled = true;
            document.getElementById('loading').style.display = 'block';
            clearError();
            
            fetch(`/api/run/${taskId}`)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}: ${r.statusText}`);
                    return r.json();
                })
                .then(data => {
                    if (data.error) {
                        showError(data.error);
                    } else {
                        document.getElementById('logs').value = data.logs || '';
                        document.getElementById('analysis').value = data.analysis || '';
                        document.getElementById('summary').value = data.summary || '';
                    }
                })
                .catch(err => showError('Execution failed: ' + err.message))
                .finally(() => {
                    btn.disabled = false;
                    document.getElementById('loading').style.display = 'none';
                });
        }
        
        // Load task on startup
        window.onload = updateTask;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/task/<task_id>')
def get_task(task_id):
    """Get task information"""
    try:
        # Check cache first
        if task_id in TASK_CACHE:
            return jsonify(TASK_CACHE[task_id])
        
        from pipeline_debug_env import PipelineDebugEnv
        
        env = PipelineDebugEnv(task_id)
        obs = env.reset()
        
        task_data = {
            'name': env.state.current_task.task_name,
            'difficulty': env.state.current_task.difficulty,
            'error_log': env.state.current_task.error_log
        }
        
        # Cache it
        TASK_CACHE[task_id] = task_data
        
        return jsonify(task_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run/<task_id>')
def run(task_id):
    """Run debugging session"""
    try:
        from inference import DebugAgent
        
        # Create and run agent
        agent = DebugAgent(task_id)
        result = agent.run()
        
        # Format outputs
        actions = result.get('actions', [])
        logs = "=== EXECUTION STEPS ===\n" + "\n".join(actions) if actions else "No steps recorded"
        
        predicted = result.get('predicted_root_cause', 'Unknown')
        actual = result.get('correct_root_cause', 'Unknown')
        grade = result.get('grade', 0.0)
        
        analysis = f"""Predicted: {predicted}
Actual: {actual}
Match: {'✓ YES' if grade == 1.0 else '✗ NO'}
Grade Score: {grade:.1%}"""
        
        summary = f"""Total Reward: {result.get('total_reward', 0):.2f}
Steps: {result.get('steps', 0)}
Grade: {grade:.1%}
Status: {'CORRECT' if grade == 1.0 else 'INCORRECT'}"""
        
        return jsonify({
            'logs': logs,
            'analysis': analysis,
            'summary': summary,
            'error': None
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"ERROR in /api/run: {error_msg}")
        print(traceback_str)
        return jsonify({
            'logs': '',
            'analysis': '',
            'summary': '',
            'error': error_msg
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[*] MeshClean Pipeline Debugging Environment")
    print("="*60)
    print("\nStarting Flask UI...")
    print("Open in browser: http://localhost:7860")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

