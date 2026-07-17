from src.config.paths import PROJECT_ROOT
from src.config.yaml_config_loader import load_yaml_config

_CONFIG_PATH = (
    PROJECT_ROOT / "src" / "config" / "retrieval_keyword" / "sql_keyword_scorer.yaml"
)
_config = load_yaml_config(_CONFIG_PATH, description="SQL keyword scorer tables")

STRUCTURED_TYPES = set(_config["structured_types"])
NOISE_SECTION_TOKENS = set(_config["noise_section_tokens"])
TABLE_QUERY_MARKERS = tuple(_config["table_query_markers"])
FIGURE_QUERY_MARKERS = tuple(_config["figure_query_markers"])
OVERVIEW_QUERY_MARKERS = tuple(_config["overview_query_markers"])
OVERVIEW_SECTION_MARKERS = tuple(_config["overview_section_markers"])
