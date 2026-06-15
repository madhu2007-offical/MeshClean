# 🔍 MeshClean: A Dynamic Data Pipeline Debugging Environment

[![Gradio App](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face%20Spaces-blue)](https://huggingface.co/spaces/Madhu007official/MeshClean-Debugger)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

MeshClean is a high-fidelity simulation environment built to model failures that software and data engineers encounter daily in production pipelines. A minor upstream change—such as a schema mismatch—can silently propagate downstream, leading to cascading failures at terminal stages. Identifying the true root cause manually requires tracing DAG dependencies, comparing schema histories, and filtering out the noise of downstream side effects.

This environment presents a **structured API and UI** to let AI agents systematically traverse pipeline DAGs, inspect data quality states, and diagnose root causes.

---

## 🚀 Key Features

*   **DAG-Based Pipeline Modeling:** Represents workflows as Directed Acyclic Graphs (DAGs), mimicking modern orchestrators like Apache Airflow, Prefect, and Dagster.
*   **Dynamic Error Injection:** Simulates realistic failure modes, including schema conflicts, type mismatches, and renamed columns.
*   **Structured Action Space:** Equip agents to perform operations like `inspect_node`, `check_schema`, `move_to_parent`, and `submit_root_cause`.
*   **Guided Reward System:** Includes a dense reward signal to incentivize efficient exploration while penalizing redundant or invalid actions.
*   **Dual Interfaces:**
    *   **Gradio Web UI:** High-fidelity interface featuring interactive flowcharts and live debugging.
    *   **Flask Web UI (Minimal):** Pure HTML/JS lightweight UI for maximum compatibility.

---

## 🛠️ System Architecture

```text
MeshClean-main/
├── pipeline_debug_env/      # Core environment package
│   ├── __init__.py          # Exposed classes and helpers
│   ├── environment.py       # Core PipelineDebugEnv (OpenEnv)
│   ├── models.py            # Pydantic schemas and typed definitions
│   ├── tasks.py             # Predefined debugging scenarios
│   └── grader.py            # Graph distance evaluation logic
├── inference.py             # Reference baseline heuristic agent
├── ui.py                    # Gradio web interface
├── ui_minimal.py            # Pure Flask web interface
├── start_ui.py              # Launcher script for Flask UI
├── test_system.py           # Verification and validation suite
├── Dockerfile               # Deployment container build script
└── requirements.txt         # Package dependencies
```

---

## ⚡ Quickstart Setup

Get the environment and interface up and running on your local machine in three steps:

### 1. Clone & Navigate
```bash
git clone https://github.com/madhu2007-offical/MeshClean.git
cd MeshClean
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Interface
To start the default web interface:
```bash
python start_ui.py
```
Open your browser and navigate to **`http://localhost:7860`**.

> [!NOTE]
> If you prefer the Gradio-based layout, run:
> ```bash
> python ui.py
> ```

---

## 🧩 Debugging Tasks

MeshClean ships with three predefined scenarios representing different difficulty tiers:

| Task ID | Name / Scenario | Difficulty | Injected Error & propagation |
| :--- | :--- | :---: | :--- |
| **`task_1`** | **Simple Linear Pipeline** (Data Cleaning)<br>Traces missing value propagation in an Employee database. | **Easy** | Root cause is at `data_source` which contains null values. Cleaner drops them, causing a count discrepancy downstream. |
| **`task_2`** | **Data Type Precision Loss** (ETL Pipeline)<br>Models locale-specific numeric parsing issues. | **Medium** | Decimal separator parsing bugs in `transform` stage propagate to invalid calculations at output. |
| **`task_3`** | **Duplicate Records at Source** (Complex DAG)<br>A complex dual-path merge flow. | **Hard** | Comprises a true root cause at `data_source` accompanied by a decoy error downstream to test agent differentiation capabilities. |

---

## 🗺️ Pipeline DAG Visualization

Pipelines are structured as dependency trees where errors flow downstream:

```text
         [A_source]         <- Data entry point (possible root cause)
           /    \
     [B_clean] [C_filter]   <- Intermediate processing stages
        |         |
     [D_trans] [E_enrich]   <- Schema alignment and conversions
           \    /
         [F_merge]          <- Merging datasets
            |
        [output]            <- Terminal node (where failures surface)
```

---

## 💾 Environment API

AI agents interact with the debugging pipeline through a standardized programmatic interface.

### Initializing the Environment
```python
from pipeline_debug_env import PipelineDebugEnv

# Create the environment for a specific task
env = PipelineDebugEnv(task_id="task_1")
obs = env.reset()

print(f"Initial Error Surface: {obs.error_log}")
print(f"Available Upstream Node connections: {obs.parents}")
```

### Executing an Action
```python
action = {
    "action_type": "inspect_node",  # Options: inspect_node, move_to_parent, check_schema, submit_root_cause
    "node": "B_clean"
}

step_result = env.step(action)
print(f"Action Reward: {step_result.reward}")
print(f"Updated Observation Current Node: {step_result.observation.current_node}")
print(f"Is Episode Finished: {step_result.done}")
```

---

## 🏆 Reward and Grading System

To guide autonomous learning, the environment provides immediate step feedback and evaluates the final prediction using graph-distance heuristics:

### Step-Level Rewards
| Action Executed | Reward | Condition / Rationale |
| :--- | :---: | :--- |
| **Correct prediction** | **`+1.0`** | `submit_root_cause` matches the true injected failure node. |
| **Adjacent prediction** | **`+0.5`** | Predicted node is 1 hop away from the true cause. |
| **Near-miss prediction** | **`+0.25`** | Predicted node is 2 hops away from the true cause. |
| **Valid Exploration** | **`+0.2`** | Inspecting/checking a new, unvisited node. |
| **Redundant Action** | **`-0.1`** | Inspecting or moving to an already visited node. |
| **Incorrect Prediction** | **`-0.5`** | Submitting a prediction node that is far from the true cause. |

### Prediction Grading Formula
Performance is mathematically evaluated by structural distance in the DAG:
$$\text{Grade} = \max\left(0, 1 - 0.5 \times \text{distance}(\text{prediction}, \text{truth})\right)$$

---

## 🤖 Reference Baseline Agent

A standard heuristic agent is provided in `inference.py` to establish a performance baseline. The agent begins exploration at the failing terminal output node and steps upstream, comparing parent schema states to locate the primary failure point.

Run the baseline agent from your terminal:
```bash
python inference.py task_1
```

**Example Output:**
```text
[START]
[INFO] Task: Easy: Simple Linear Pipeline (easy)
[INFO] Error: ERROR: Data loss detected in pipeline. Fewer records than expected in output.
[INFO] Exploration plan: output -> B_processor -> A_source
[STEP 1] action=inspect_node(output) reward=-0.1 total_reward=-0.1
[STEP 2] action=inspect_node(B_processor) reward=0.2 total_reward=0.2
[STEP 3] action=inspect_node(A_source) reward=0.2 total_reward=0.4
[STEP 4] action=check_schema(A_source) reward=0.1 total_reward=0.5
[STEP 5] action=submit_root_cause(A_source) reward=1.0 total_reward=1.5 result=CORRECT
[INFO] Episode complete in 5 steps
[INFO] Predicted root cause: A_source
[INFO] Correct root cause: A_source
[INFO] Grade: 1.00
[END]
```

---

## 🐳 Docker Deployment

To package and run the debugger as a container:

### Build the Image
```bash
docker build -t meshclean-debugger .
```

### Run the Container
```bash
docker run -p 7860:7860 meshclean-debugger
```
Access the application on `http://localhost:7860`.

---

## 🔗 Hugging Face Spaces Deployment

The repository is pre-configured for deployment to **Hugging Face Spaces** using the Docker SDK:

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Choose **Docker** as the SDK.
3. Link your GitHub repository or push the codebase directly to the Space's Git remote.
4. The Space will automatically build the `Dockerfile` and run the Gradio server on port `7860`.

Live demonstration template: [MeshClean Debugger on HF Spaces](https://huggingface.co/spaces/Madhu007official/MeshClean-Debugger)

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
