from src.config.settings.app_settings import AppSettings
from src.config.settings.db_settings import DatabaseSettings
from src.config.settings.docling_settings import DoclingSettings
from src.config.settings.embedding_settings import EmbeddingSettings
from src.config.settings.guardrail_settings import GuardrailSettings
from src.config.settings.ingestion_settings import IngestionSettings
from src.config.settings.llm_settings import LLMSettings
from src.config.settings.ocr_settings import OCRSettings
from src.config.settings.qdrant_settings import QdrantSettings
from src.config.settings.retrieval_settings import RetrievalSettings
from src.config.settings.classification_settings import ClassificationSettings
from src.config.settings.chunking_settings import ChunkingSettings
from src.config.settings.logging_settings import LoggingSettings
from src.config.settings.agent_settings import AgentSettings
from src.config.settings.langgraph_setting import LangGraphSettings
from src.config.settings.memory_settings import MemorySettings
from src.config.settings.extraction_settings import ExtractionSettings
from src.config.settings.duplicate_detection_settings import DuplicateDetectionSettings
from src.config.settings.prompt_context_settings import PromptContextSettings
from src.config.settings.storage_settings import StorageSettings


app_settings = AppSettings()                        # type: ignore[call-arg]
database_settings = DatabaseSettings()              # type: ignore[call-arg]
qdrant_settings = QdrantSettings()                  # type: ignore[call-arg]
llm_settings = LLMSettings()                        # type: ignore[call-arg]
embedding_settings = EmbeddingSettings()            # type: ignore[call-arg]
ingestion_settings = IngestionSettings()            # type: ignore[call-arg]
docling_settings = DoclingSettings()                # type: ignore[call-arg]
retrieval_settings = RetrievalSettings()            # type: ignore[call-arg]
guardrail_settings = GuardrailSettings()            # type: ignore[call-arg]
classification_settings = ClassificationSettings()  # type: ignore[call-arg]
chunking_settings = ChunkingSettings()              # type: ignore[call-arg]
logging_settings = LoggingSettings()                # type: ignore[call-arg]
agent_settings = AgentSettings()                    # type: ignore[call-arg]
langgraph_settings = LangGraphSettings()            # type: ignore[call-arg]
memory_settings = MemorySettings()                  # type: ignore[call-arg]
ocr_settings = OCRSettings()                        # type: ignore[call-arg]
extraction_settings = ExtractionSettings()                      # type: ignore[call-arg]
duplicate_detection_settings = DuplicateDetectionSettings()     # type: ignore[call-arg]
storage_settings = StorageSettings()                            # type: ignore[call-arg]
prompt_context_settings = PromptContextSettings()                # type: ignore[call-arg]
