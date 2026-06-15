"""
Pipeline Debugging Environment Package
"""

from pipeline_debug_env.environment import PipelineDebugEnv, make_env, available_tasks
from pipeline_debug_env.models import Observation, Action, StepResult
from pipeline_debug_env.tasks import get_task, list_tasks
from pipeline_debug_env.error_engine import ErrorInjector, ErrorLogGenerator, create_pipeline_with_error

__version__ = "1.0.0"
__all__ = [
    "PipelineDebugEnv",
    "make_env",
    "available_tasks",
    "get_task",
    "list_tasks",
    "Observation",
    "Action",
    "StepResult",
    "ErrorInjector",
    "ErrorLogGenerator",
    "create_pipeline_with_error",
]
