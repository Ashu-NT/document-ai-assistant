from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = PROJECT_ROOT / "src" / "config" / "research" / "research_constants.yaml"
_config = load_yaml_config(_CONFIG_PATH, description="Research constants")

DEFAULT_MAX_RESEARCH_TASKS = int(_config["max_research_tasks"])
DEFAULT_MAX_RESEARCH_ITERATIONS = int(_config["max_research_iterations"])
DEFAULT_MAX_RESEARCH_EVIDENCE_PER_TASK = int(_config["max_research_evidence_per_task"])
DEFAULT_MAX_TOTAL_RESEARCH_EVIDENCE = int(_config["max_total_research_evidence"])

RESEARCH_ROUTE_TRIGGER_TERMS: tuple[str, ...] = tuple(_config["route_trigger_terms"])
