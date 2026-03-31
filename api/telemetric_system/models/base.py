"""Base ORM model declarations and shared mixins.

This module defines the project's SQLAlchemy declarative base and a reusable
`BaseModel` mixin providing:
- Common fields: id, created_at, updated_at, is_deleted
- Soft delete functionality
- Automatic timestamp management
- JSON serialization via `to_dict()`
- Simple query helper class methods that expect a Session
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Sequence

from sqlalchemy import BigInteger, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base."""


class BaseModel(Base):
    """Abstract base model with common fields and helpers."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0", index=True)

    # ----------------------------
    # Instance helpers
    # ----------------------------
    def soft_delete(self, *, commit: bool = False, session: Optional[Session] = None) -> None:
        """Mark the row as softly deleted.

        If `commit` is True, a flush/commit is attempted using the provided
        `session`. When `commit` is False, caller is responsible for persisting.
        """
        self.is_deleted = True
        # updated_at will be set by onupdate on next flush; ensure flush to apply
        if commit and session is not None:
            session.add(self)
            session.commit()

    def hard_delete(self, *, commit: bool = False, session: Optional[Session] = None) -> None:
        """Permanently remove the row from the database."""
        if session is None:
            raise ValueError("session is required for hard_delete")
        session.delete(self)
        if commit:
            session.commit()

    def to_dict(
        self,
        *,
        include: Optional[Iterable[str]] = None,
        exclude: Optional[Iterable[str]] = None,
        include_relationships: bool = False,
    ) -> Dict[str, Any]:
        """Serialize model to a plain dict.

        - `include`: explicit allow-list of fields to include
        - `exclude`: fields to omit (applied after include)
        - `include_relationships`: if True, includes simple relationship-loaded
          attributes where possible (best-effort, may trigger lazy loads)
        """
        include_set = set(include or [])
        exclude_set = set(exclude or [])

        result: Dict[str, Any] = {}
        mapper = self.__class__.__mapper__

        # Column attributes
        for attr in mapper.column_attrs:
            key = attr.key
            if include_set and key not in include_set:
                continue
            if key in exclude_set:
                continue
            result[key] = getattr(self, key)

        if include_relationships:
            for rel in mapper.relationships:
                key = rel.key
                if include_set and key not in include_set:
                    continue
                if key in exclude_set:
                    continue
                val = getattr(self, key)
                # Avoid deep recursion; provide primary keys or simple dicts
                if isinstance(val, list) or isinstance(val, tuple):
                    result[key] = [getattr(item, "id", None) for item in val]
                else:
                    result[key] = getattr(val, "id", None) if val is not None else None

        return result

    # ----------------------------
    # Query helpers (class methods)
    # ----------------------------
    @classmethod
    def get_by_id(
        cls,
        session: Session,
        object_id: int,
        *,
        include_deleted: bool = False,
    ) -> Optional["BaseModel"]:
        """Fetch a single row by id, optionally including soft-deleted rows."""
        stmt = session.query(cls).filter(cls.id == object_id)
        if not include_deleted:
            stmt = stmt.filter(cls.is_deleted.is_(False))
        return stmt.one_or_none()

    @classmethod
    def all(
        cls,
        session: Session,
        *,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Sequence[Any]] = None,
    ) -> list["BaseModel"]:
        """Return a list of rows with basic pagination and ordering."""
        stmt = session.query(cls)
        if not include_deleted:
            stmt = stmt.filter(cls.is_deleted.is_(False))
        if order_by:
            stmt = stmt.order_by(*order_by)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(stmt.all())

    @classmethod
    def filter_by_fields(
        cls,
        session: Session,
        *,
        include_deleted: bool = False,
        order_by: Optional[Sequence[Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any,
    ) -> list["BaseModel"]:
        """Filter rows by simple equality on provided fields.

        Example: `User.filter_by_fields(session, email="a@b.com")`
        """
        stmt = session.query(cls).filter_by(**filters)
        if not include_deleted:
            stmt = stmt.filter(cls.is_deleted.is_(False))
        if order_by:
            stmt = stmt.order_by(*order_by)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(stmt.all())
