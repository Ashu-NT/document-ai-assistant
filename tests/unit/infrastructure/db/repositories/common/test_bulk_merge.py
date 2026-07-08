from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.infrastructure.db.orm_models import SectionORM
from src.infrastructure.db.repositories.common import bulk_merge
from src.infrastructure.db.schema_management import ensure_database_schema


def _make_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    ensure_database_schema(engine)
    return engine


def _make_section(section_id: str, *, title: str) -> SectionORM:
    return SectionORM(
        id=section_id,
        document_id="doc_001",
        title=title,
        level=1,
        created_at=datetime.now(timezone.utc),
    )


def test_bulk_merge_inserts_new_rows_with_no_prior_existence_query_match() -> None:
    engine = _make_engine()
    with Session(engine) as session:
        bulk_merge(
            session,
            SectionORM,
            [_make_section("sec_1", title="Intro"), _make_section("sec_2", title="Body")],
        )
        session.commit()

        rows = session.execute(select(SectionORM.id, SectionORM.title)).all()
        assert sorted(rows) == [("sec_1", "Intro"), ("sec_2", "Body")]


def test_bulk_merge_updates_existing_rows() -> None:
    engine = _make_engine()
    with Session(engine) as session:
        bulk_merge(session, SectionORM, [_make_section("sec_1", title="Intro")])
        session.commit()

    with Session(engine) as session:
        bulk_merge(session, SectionORM, [_make_section("sec_1", title="Updated Intro")])
        session.commit()

        row = session.execute(
            select(SectionORM.title).where(SectionORM.id == "sec_1")
        ).scalar_one()
        assert row == "Updated Intro"


def test_bulk_merge_handles_mixed_new_and_existing_rows_in_one_call() -> None:
    engine = _make_engine()
    with Session(engine) as session:
        bulk_merge(session, SectionORM, [_make_section("sec_1", title="Intro")])
        session.commit()

    with Session(engine) as session:
        bulk_merge(
            session,
            SectionORM,
            [
                _make_section("sec_1", title="Updated Intro"),
                _make_section("sec_2", title="New Section"),
            ],
        )
        session.commit()

        rows = dict(session.execute(select(SectionORM.id, SectionORM.title)).all())
        assert rows == {"sec_1": "Updated Intro", "sec_2": "New Section"}


def test_bulk_merge_does_nothing_for_empty_input() -> None:
    engine = _make_engine()
    with Session(engine) as session:
        bulk_merge(session, SectionORM, [])
        session.commit()

        rows = session.execute(select(SectionORM.id)).all()
        assert rows == []
