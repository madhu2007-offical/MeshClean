"""
Predefined Debugging Tasks - Base Pipelines
Three realistic data pipeline debugging scenarios with DAG structure.
Errors are injected DYNAMICALLY at runtime, not hardcoded here.
"""

from pipeline_debug_env.models import TaskDefinition, NodeInfo
from typing import Dict


def create_task_1_easy() -> TaskDefinition:
    """
    TASK 1 (EASY): Simple Linear Pipeline
    
    DAG Graph:
    A → B → Output
    
    Base structure to which error will be dynamically injected.
    No predefined errors - will be generated at reset time.
    """
    nodes = {
        "A_source": NodeInfo(
            node_id="A_source",
            node_type="data_source",
            description="Original data source with baseline schema.",
            schema_info={"id": "int", "name": "str", "value": "float"},
            parents=[],
            children=["B_processor"]
        ),
        "B_processor": NodeInfo(
            node_id="B_processor",
            node_type="processor",
            description="Processing stage that transforms data from source.",
            schema_info={"id": "int", "name": "str", "value": "float"},
            parents=["A_source"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Final output of the pipeline.",
            schema_info={"id": "int", "name": "str", "value": "float"},
            parents=["B_processor"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_1",
        task_name="Easy: Simple Linear Pipeline",
        difficulty="easy",
        description="Simple 2-node pipeline. Error injected dynamically at one random node.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="",  # Will be set dynamically
        error_log="",  # Will be generated dynamically
        ground_truth_explanation="Error location and type determined at runtime."
    )


def create_task_2_medium() -> TaskDefinition:
    """
    TASK 2 (MEDIUM): Branching Pipeline with Merge
    
    DAG Graph:
        A
       / \
      B   C
      |   |
      D   E
       \ /
        F
        |
      Output
    
    Base structure with no predefined errors.
    Errors will be injected dynamically.
    """
    nodes = {
        "A_source": NodeInfo(
            node_id="A_source",
            node_type="data_source",
            description="Original data source with baseline schema.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=[],
            children=["B_branch1", "C_branch2"]
        ),
        "B_branch1": NodeInfo(
            node_id="B_branch1",
            node_type="processor",
            description="First processing branch from source.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["A_source"],
            children=["D_transform1"]
        ),
        "C_branch2": NodeInfo(
            node_id="C_branch2",
            node_type="processor",
            description="Second processing branch from source.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["A_source"],
            children=["E_transform2"]
        ),
        "D_transform1": NodeInfo(
            node_id="D_transform1",
            node_type="processor",
            description="Transformation applied to branch 1 data.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["B_branch1"],
            children=["F_merge"]
        ),
        "E_transform2": NodeInfo(
            node_id="E_transform2",
            node_type="processor",
            description="Transformation applied to branch 2 data.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["C_branch2"],
            children=["F_merge"]
        ),
        "F_merge": NodeInfo(
            node_id="F_merge",
            node_type="processor",
            description="Merge point combining both branches.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["D_transform1", "E_transform2"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Final merged output of the pipeline.",
            schema_info={"id": "int", "name": "str", "email": "str", "amount": "float"},
            parents=["F_merge"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_2",
        task_name="Medium: Branching Pipeline with Merge",
        difficulty="medium",
        description="Complex pipeline with branching and merging. Error injected at random node and propagates.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="",  # Will be set dynamically
        error_log="",  # Will be generated dynamically
        ground_truth_explanation="Error location and type determined at runtime."
    )


def create_task_3_hard() -> TaskDefinition:
    """
    TASK 3 (HARD): Complex Multi-Path DAG with Merge Issues
    
    DAG Graph:
        A ──────┐
       / \      │
      B   C    │
      |   |    │
      D   E    │
       \ /     │
        F      │
        |      │
        G──────┘
        |
      Output
    
    Complex structure with multiple convergence points.
    Includes decoy error on independent node (hard difficulty).
    Errors injected dynamically.
    """
    nodes = {
        "A_source": NodeInfo(
            node_id="A_source",
            node_type="data_source",
            description="Original data source with baseline schema.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=[],
            children=["B_path1", "C_path2", "G_independent"]
        ),
        "B_path1": NodeInfo(
            node_id="B_path1",
            node_type="processor",
            description="First processing path from source.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["A_source"],
            children=["D_depth1"]
        ),
        "C_path2": NodeInfo(
            node_id="C_path2",
            node_type="processor",
            description="Second processing path from source.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["A_source"],
            children=["E_depth1"]
        ),
        "D_depth1": NodeInfo(
            node_id="D_depth1",
            node_type="processor",
            description="Deeper processing in path 1.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["B_path1"],
            children=["F_merge"]
        ),
        "E_depth1": NodeInfo(
            node_id="E_depth1",
            node_type="processor",
            description="Deeper processing in path 2.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["C_path2"],
            children=["F_merge"]
        ),
        "F_merge": NodeInfo(
            node_id="F_merge",
            node_type="processor",
            description="First merge point combining paths 1 and 2.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["D_depth1", "E_depth1"],
            children=["G_independent"]
        ),
        "G_independent": NodeInfo(
            node_id="G_independent",
            node_type="processor",
            description="Final processing combining all sources.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["A_source", "F_merge"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Final output of the complex pipeline.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "status": "str", "date": "str"},
            parents=["G_independent"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_3",
        task_name="Hard: Complex Multi-Path DAG",
        difficulty="hard",
        description="Complex pipeline with multiple paths and convergence points. Root error + independent decoy error injected.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="",  # Will be set dynamically
        error_log="",  # Will be generated dynamically
        ground_truth_explanation="Error location and type determined at runtime. Contains decoy error on independent node."
    )


# Task registry
TASKS = {
    "task_1": create_task_1_easy,
    "task_2": create_task_2_medium,
    "task_3": create_task_3_hard
}


def get_task(task_id: str) -> TaskDefinition:
    """
    Get a task by ID with dynamically injected error.
    
    Args:
        task_id: "task_1", "task_2", or "task_3"
    
    Returns:
        TaskDefinition with error injected
    """
    if task_id not in TASKS:
        raise ValueError(f"Unknown task: {task_id}. Valid tasks: {list(TASKS.keys())}")
    
    return TASKS[task_id]()


def list_tasks() -> Dict[str, str]:
    """
    List all available tasks.
    
    Returns:
        Dict mapping task_id to task_name
    """
    return {
        "task_1": "Easy: Simple Linear Pipeline",
        "task_2": "Medium: Branching Pipeline with Merge",
        "task_3": "Hard: Complex Multi-Path DAG"
    }
    """
    TASK 1 (EASY): Multi-Stage Pipeline with Branching
    
    DAG Graph:
    A (original_data) → B (missing_columns), C (unchanged)
    B → D (type_change)
    C → E (col_rename)
    D, E → F (merge) → output
    
    Error: Missing columns in B branch propagates
    Root Cause: A has 2 missing columns initially
    """
    nodes = {
        "A_original_data": NodeInfo(
            node_id="A_original_data",
            node_type="data_source",
            description="Original customer dataset with 1000 records. Missing 2 columns (email, status).",
            schema_info={"customer_id": "int", "name": "str", "amount": "float"},
            parents=[],
            children=["B_missing_cols", "C_unchanged"]
        ),
        "B_missing_cols": NodeInfo(
            node_id="B_missing_cols",
            node_type="processor",
            description="Copy of A with columns: customer_id, name, amount. Missing email & status columns.",
            schema_info={"customer_id": "int", "name": "str", "amount": "float"},
            parents=["A_original_data"],
            children=["D_type_change"]
        ),
        "C_unchanged": NodeInfo(
            node_id="C_unchanged",
            node_type="processor",
            description="Exact copy of A with all original columns: customer_id, name, amount.",
            schema_info={"customer_id": "int", "name": "str", "amount": "float"},
            parents=["A_original_data"],
            children=["E_col_rename"]
        ),
        "D_type_change": NodeInfo(
            node_id="D_type_change",
            node_type="processor",
            description="Converts amount from float to int (lossy conversion). Derived from B.",
            schema_info={"customer_id": "int", "name": "str", "amount": "int"},
            parents=["B_missing_cols"],
            children=["F_merge"]
        ),
        "E_col_rename": NodeInfo(
            node_id="E_col_rename",
            node_type="processor",
            description="Renames columns: customer_id→cust_id, name→full_name. Derived from C.",
            schema_info={"cust_id": "int", "full_name": "str", "amount": "float"},
            parents=["C_unchanged"],
            children=["F_merge"]
        ),
        "F_merge": NodeInfo(
            node_id="F_merge",
            node_type="processor",
            description="Merges D and E. Schema mismatch: D has customer_id/int amounts, E has cust_id/float amounts.",
            schema_info={"customer_id": "int", "name": "str", "cust_id": "int", "full_name": "str", "amount": "float"},
            parents=["D_type_change", "E_col_rename"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Merged output: 1000 records with schema conflicts. Missing email/status columns.",
            schema_info={"customer_id": "int", "name": "str", "cust_id": "int", "full_name": "str", "amount": "float"},
            parents=["F_merge"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_1",
        task_name="Data Pipeline - Missing Columns at Source",
        difficulty="easy",
        description="Multi-stage pipeline with column drops. Track missing columns back to source.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="A_original_data",
        error_log="ERROR: Output missing email and status columns. Schema incomplete. 1000 records with 5 fields instead of 7.",
        ground_truth_explanation=(
            "Root cause is in 'A_original_data': Original dataset was loaded with only 3 columns "
            "(customer_id, name, amount) instead of 5. Columns 'email' and 'status' were never loaded. "
            "Node B inherited this problem, which propagated through D→merge→output. "
            "Node C also has the same issue but renamed columns. "
            "The missing columns never existed in the raw data."
        )
    )


def create_task_2_medium() -> TaskDefinition:
    """
    TASK 2 (MEDIUM): DAG with Data Type Issues
    
    DAG Graph:
    A (transactions) → B (subset), C (full)
    B → D (int_conversion)
    C → E (rename_cols)
    D, E → F (merge) → output
    
    Error: Precision loss in amounts (500 vs 50000)
    Root Cause: D node converts float to int, losing decimal precision
    """
    nodes = {
        "A_transactions": NodeInfo(
            node_id="A_transactions",
            node_type="data_source",
            description="Transaction data from API: 10,000 records with amount as float (1.25, 99.99, etc.).",
            schema_info={"transaction_id": "str", "amount": "float", "user_id": "int"},
            parents=[],
            children=["B_subset", "C_full"]
        ),
        "B_subset": NodeInfo(
            node_id="B_subset",
            node_type="processor",
            description="Subset of A with transactions amount > 100. 5000 records with decimal amounts.",
            schema_info={"transaction_id": "str", "amount": "float", "user_id": "int"},
            parents=["A_transactions"],
            children=["D_int_conversion"]
        ),
        "C_full": NodeInfo(
            node_id="C_full",
            node_type="processor",
            description="Full set of A transactions, maintains original schema and float precision.",
            schema_info={"transaction_id": "str", "amount": "float", "user_id": "int"},
            parents=["A_transactions"],
            children=["E_rename_cols"]
        ),
        "D_int_conversion": NodeInfo(
            node_id="D_int_conversion",
            node_type="processor",
            description=(
                "BUG: Converts amount from float to int (lossy). "
                "Example: 123.99 becomes 123. Loses 0.99 precision. "
                "5000 records affected by precision loss."
            ),
            schema_info={"transaction_id": "str", "amount": "int", "user_id": "int"},
            parents=["B_subset"],
            children=["F_merge"]
        ),
        "E_rename_cols": NodeInfo(
            node_id="E_rename_cols",
            node_type="processor",
            description="Renames columns: transaction_id→txn_id, amount→total. Maintains precision.",
            schema_info={"txn_id": "str", "total": "float", "user_id": "int"},
            parents=["C_full"],
            children=["F_merge"]
        ),
        "F_merge": NodeInfo(
            node_id="F_merge",
            node_type="processor",
            description="Merges D (int amounts) and E (float amounts). Schema mismatch on amount data type.",
            schema_info={"transaction_id": "str", "amount": "int", "txn_id": "str", "total": "float", "user_id": "int"},
            parents=["D_int_conversion", "E_rename_cols"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Merged output: 10,000 records with precision loss in 5000 transactions from D branch.",
            schema_info={"transaction_id": "str", "amount": "int", "txn_id": "str", "total": "float", "user_id": "int"},
            parents=["F_merge"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_2",
        task_name="Data Pipeline - Data Type Precision Loss",
        difficulty="medium",
        description="Pipeline has precision loss in financial amounts. Track back to conversion stage.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="D_int_conversion",
        error_log="ERROR: 5000 transactions show precision loss. Amounts like 149.99 became 149. Decimals missing.",
        ground_truth_explanation=(
            "Root cause is in 'D_int_conversion' node: Converting float amounts to int loses decimal precision. "
            "5000 transactions from B branch converted 149.99 → 149 (losing 0.99). "
            "E branch maintains precision but isn't merged correctly. "
            "The D branch was designed for int conversion but financial data needs float precision. "
            "This is a schema/type design error at D node."
        )
    )


def create_task_3_hard() -> TaskDefinition:
    """
    TASK 3 (HARD): Complex DAG with Merge Issues
    
    DAG Graph:
    A (customers) → B (duplicates), C (clean)
    B → D (type_change)
    C → E (col_rename)
    D, E → F (merge) → output
    
    Error: Duplicate records and schema conflicts at merge
    Root Cause: A contains duplicate customer records, propagates through both branches
    """
    nodes = {
        "A_customers": NodeInfo(
            node_id="A_customers",
            node_type="data_source",
            description=(
                "Raw customer data: 50,000 records. "
                "CORRUPTION: 200 duplicate customer_ids with conflicting data (cust_id 1001 appears 2x with different emails)."
            ),
            schema_info={"customer_id": "int", "name": "str", "email": "str", "registration_date": "str"},
            parents=[],
            children=["B_duplicates", "C_clean"]
        ),
        "B_duplicates": NodeInfo(
            node_id="B_duplicates",
            node_type="processor",
            description="Inherits all 50,200 records from A (including 200 duplicates). No deduplication.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "registration_date": "str"},
            parents=["A_customers"],
            children=["D_type_change"]
        ),
        "C_clean": NodeInfo(
            node_id="C_clean",
            node_type="processor",
            description="Also inherits 50,200 records from A. No deduplication applied.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "registration_date": "str"},
            parents=["A_customers"],
            children=["E_col_rename"]
        ),
        "D_type_change": NodeInfo(
            node_id="D_type_change",
            node_type="processor",
            description="Converts registration_date from str to datetime. Maintains 50,200 records with duplicates.",
            schema_info={"customer_id": "int", "name": "str", "email": "str", "registration_date": "datetime"},
            parents=["B_duplicates"],
            children=["F_merge"]
        ),
        "E_col_rename": NodeInfo(
            node_id="E_col_rename",
            node_type="processor",
            description="Renames: customer_id→cust_id, name→full_name. Maintains 50,200 records with duplicates.",
            schema_info={"cust_id": "int", "full_name": "str", "email": "str", "registration_date": "str"},
            parents=["C_clean"],
            children=["F_merge"]
        ),
        "F_merge": NodeInfo(
            node_id="F_merge",
            node_type="processor",
            description=(
                "Merges D and E on customer_id. Both carry duplicates. "
                "Schema conflict: D has customer_id/datetime, E has cust_id/str dates. "
                "Result: 50,200 records with conflicting data for 200 customer pairs."
            ),
            schema_info={"customer_id": "int", "cust_id": "int", "name": "str", "full_name": "str", "email": "str", "registration_date": "datetime"},
            parents=["D_type_change", "E_col_rename"],
            children=["output"]
        ),
        "output": NodeInfo(
            node_id="output",
            node_type="output",
            description="Merged output: 50,200 records with duplicate customer_ids showing conflicting metadata.",
            schema_info={"customer_id": "int", "cust_id": "int", "name": "str", "full_name": "str", "email": "str", "registration_date": "datetime"},
            parents=["F_merge"],
            children=[]
        )
    }
    
    return TaskDefinition(
        task_id="task_3",
        task_name="Complex DAG - Duplicate Records at Source",
        difficulty="hard",
        description="Multi-path pipeline with duplicate propagation through merge. Complex DAG structure.",
        nodes=nodes,
        start_node="output",
        correct_root_cause="A_customers",
        error_log=(
            "ERROR: Output has 50,200 records but only 50,000 customers should exist. "
            "200 customer_ids appear twice with conflicting emails and registration dates. "
            "Merge shows duplicate keys. Schema conflicts between branches."
        ),
        ground_truth_explanation=(
            "Root cause is in 'A_customers' node: Raw data was corrupted during load. "
            "200 customer records were duplicated with divergent data (same cust_id, different email/date). "
            "Both B and C branches inherited these 50,200 records including duplicates. "
            "D branch converts dates correctly but maintains duplicates. "
            "E branch renames columns but maintains duplicates. "
            "F merge combines both, showing 200 duplicate customer_ids with conflicting metadata. "
            "The issue originates at the source data load in A_customers, not in branch logic or merge."
        )
    )


# Task registry
TASKS: Dict[str, TaskDefinition] = {
    "task_1": create_task_1_easy(),
    "task_2": create_task_2_medium(),
    "task_3": create_task_3_hard(),
}


def get_task(task_id: str) -> TaskDefinition:
    """Retrieve a task by ID"""
    if task_id not in TASKS:
        raise ValueError(f"Task {task_id} not found. Available tasks: {list(TASKS.keys())}")
    return TASKS[task_id]


def list_tasks() -> Dict[str, str]:
    """List all available tasks"""
    return {
        task_id: f"{task.task_name} ({task.difficulty})"
        for task_id, task in TASKS.items()
    }
