from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session


def bulk_merge(
    session: Session,
    orm_class: Any,
    orm_objects: Sequence[Any],
) -> None:
    """Upserts a batch of ORM objects with one existence-check query instead
    of letting session.merge() issue a `SELECT ... WHERE id = ?` per object.

    session.merge() is correct but costs a round trip per call for objects
    it isn't already tracking: it always checks for an existing row before
    deciding whether to insert or update. Looping merge() over a collection
    turns an O(1)-round-trip batch write into O(n) round trips. This does
    the same existence check once, in bulk, then routes each object to
    session.add() (new) or session.merge() (existing) accordingly.
    """
    if not orm_objects:
        return

    ids = [obj.id for obj in orm_objects]
    existing_ids = set(
        session.execute(
            select(orm_class.id).where(orm_class.id.in_(ids))
        ).scalars()
    )

    new_objects = [obj for obj in orm_objects if obj.id not in existing_ids]
    if new_objects:
        session.add_all(new_objects)

    for obj in orm_objects:
        if obj.id in existing_ids:
            session.merge(obj)
