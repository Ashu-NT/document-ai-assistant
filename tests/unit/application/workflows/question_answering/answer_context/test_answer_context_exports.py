from src.application.workflows.question_answering import answer_context as package_root
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerRelationship,
    AnswerSectionGroup,
    AnswerSource,
    AnswerSourceGroup,
    AnswerStructuredEntity,
    MaintenanceEntryMerger,
    StructuredAnswerContext,
    StructuredEvidenceViewBuilder,
    StructuredFactKeyValueBuilder,
)
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer as OrganizerImpl,
)
from src.application.workflows.question_answering.answer_context.maintenance_entry_merger import (
    MaintenanceEntryMerger as MergerImpl,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue as ModelAnswerKeyValue,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerMaintenanceEntry as ModelAnswerMaintenanceEntry,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerMaintenanceReference as ModelAnswerMaintenanceReference,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerRelationship as ModelAnswerRelationship,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSectionGroup as ModelAnswerSectionGroup,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource as ModelAnswerSource,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSourceGroup as ModelAnswerSourceGroup,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerStructuredEntity as ModelAnswerStructuredEntity,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext as ModelStructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.structured_evidence_view_builder import (
    StructuredEvidenceViewBuilder as StructuredEvidenceViewBuilderImpl,
)
from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
    StructuredFactKeyValueBuilder as KeyValueBuilderImpl,
)


def test_package_root_re_exports_answer_context_types_stably() -> None:
    assert AnswerKeyValue is ModelAnswerKeyValue
    assert AnswerMaintenanceEntry is ModelAnswerMaintenanceEntry
    assert AnswerMaintenanceReference is ModelAnswerMaintenanceReference
    assert AnswerRelationship is ModelAnswerRelationship
    assert AnswerSectionGroup is ModelAnswerSectionGroup
    assert AnswerSource is ModelAnswerSource
    assert AnswerSourceGroup is ModelAnswerSourceGroup
    assert AnswerStructuredEntity is ModelAnswerStructuredEntity
    assert StructuredAnswerContext is ModelStructuredAnswerContext


def test_package_root_lazy_re_exports_support_service_classes() -> None:
    assert package_root.AnswerContextOrganizer is OrganizerImpl
    assert package_root.MaintenanceEntryMerger is MergerImpl
    assert package_root.StructuredEvidenceViewBuilder is StructuredEvidenceViewBuilderImpl
    assert package_root.StructuredFactKeyValueBuilder is KeyValueBuilderImpl
    assert AnswerContextOrganizer is OrganizerImpl
    assert MaintenanceEntryMerger is MergerImpl
    assert StructuredEvidenceViewBuilder is StructuredEvidenceViewBuilderImpl
    assert StructuredFactKeyValueBuilder is KeyValueBuilderImpl
