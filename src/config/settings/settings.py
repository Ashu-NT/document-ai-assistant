from src.config.settings.app_settings import AppSettings
from src.config.settings.db_settings import DatabaseSettings
from src.config.settings.embedding_settings import EmbeddingSettings
from src.config.settings.guardrail_settings import GuardrailSettings
from src.config.settings.ingestion_settings import IngestionSettings
from src.config.settings.llm_settings import LLMSettings
from src.config.settings.qdrant_settings import QdrantSettings
from src.config.settings.retrieval_settings import RetrievalSettings
from src.config.settings.classification_settings import ClassificationSettings
from src.config.settings.logging_settings import LoggingSettings
from src.config.settings.agent_settings import AgentSettings
from src.config.settings.langgraph_setting import LangGraphSettings
from src.config.settings.memory_settings import MemorySettings
from src.config.settings.extraction_settings import ExtractionSettings
from src.config.settings.duplicate_detection_settings import DuplicateDetectionSettings
from src.config.settings.storage_settings import StorageSettings


app_settings = AppSettings()
database_settings = DatabaseSettings()
qdrant_settings = QdrantSettings()
llm_settings = LLMSettings()
embedding_settings = EmbeddingSettings()
ingestion_settings = IngestionSettings()
retrieval_settings = RetrievalSettings()
guardrail_settings = GuardrailSettings()
classification_settings = ClassificationSettings()
logging_settings = LoggingSettings()
agent_settings = AgentSettings()
langgraph_settings = LangGraphSettings()
memory_settings = MemorySettings()
extraction_settings = ExtractionSettings()
duplicate_detection_settings = DuplicateDetectionSettings()
storage_settings = StorageSettings()

def ensure_application_directories() -> None:
    storage_settings.ensure_directories()
    database_settings.ensure_database_directory()
    qdrant_settings.ensure_storage_directory()
