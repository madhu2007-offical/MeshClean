                             MeshClean - A Dynamic Data Pipeline Debugging Environment

MeshClean is a simulation environment built to model the failures that engineers encounter daily in production data pipelines. A small upstream change—such as a schema mismatch—can propagate downstream and cause widespread failures. Identifying that root cause manually requires tracing dependencies, comparing schemas, and filtering out the noise of downstream symptoms that are really just side effects. 
MeshClean is a dynamic, real-world simulation environment designed to model failures in modern data pipelines. It enables an AI agent to explore a Directed Acyclic Graph (DAG), identify hidden upstream issues, and determine the true root cause of failures without prior knowledge. 

Features Of  MeshClean:
1) Pipeline Representation: The pipeline is modeled as a DAG where nodes represent individual data processing stages and directed edges represent data dependencies. This structure mirrors how modern orchestration tools like Apache Airflow or Prefect organize their workflows. For example,
           
         A           <- Source node (possible root cause)
        / \
       B   C         <- Intermediate processing stages
       |   |
       D   E         <- Transformation nodes
        \ /
         F           <- Merge node
         |
       Output        <- Terminal node (where failures surface)
   
2)Errors: the errors are injected dynamically. The three supported error types are:

       |  Root Cause    | Downstream Effects             |
       | -------------- | ------------------------------ |
       | Missing column | Merge failure, schema mismatch |
       | Type mismatch  | Transformation errors          |
       | Rename         | Column not found               |

4) Tasks: The 3 tasks are of three diffculty levels.
i)  Easy: single visisble error with minimal propogation.
ii) Medium: one root cause with multiple downstream symptoms.
iii) Hard : includes a decoy error, requires the agent to distinguish structural failures from isolated anomalies.

5) Reward System: The agent receives rewards and penalties based on the quality and efficiency of its reasoning.

         | Action               | Reward |
         | -------------------- | ------ |
         | Correct root cause   | +1.0   |
         | Close (1 hop)        | +0.5   |
         | Partial (2 hops)     | +0.25  |
         | Exploration          | +0.2   |
         | Redundant action     | -0.1   |
         | Incorrect submission | -0.5   |
   Grading: Performance is evaluated using graph distance:
         Exact match → 1.0
         Adjacent node → 0.5
         Two hops away → 0.25
         Otherwise → 0.0

6) Agent (Baseline Heuristic Agent): A reference heuristic agent is included to establish a performance baseline. It starts at the terminal output node and traverses upstream step by step, comparing each node's schema against its parent's expected output and scoring nodes by inconsistency severity — ultimately submitting the highest-scoring node as the predicted root cause. It performs reliably on Easy and Medium configurations, but the Hard mode's decoy error can inflate the score of an unrelated node, throwing it off. This gap is precisely where more intelligent agent designs have room to outperform.

7) User interface: The system includes UI (Gradio) to visualize DAG, traversal, score node and predict root cause.

MeshClean is a dynamic OpenEnv environment where AI agents debug data pipelines by reasoning over DAG structures and identifying hidden upstream failures. 

Hugging Face Spaces

Just visit 👉 [MeshClean Link](https://huggingface.co/spaces/Madhu007official/MeshClean-Debugger)


