from sqlite3 import IntegrityError
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from api.models import RollTable, RollTableRow, RollTableRowExtra
from api.schemas import (
    RollTableCreate,
    RollTableRowCreate,
    RollTableRowCreateInTable,
    RollTableRowUpdate,
    RollTableUpdate,
)

from .base import BaseService


class RollTableService(BaseService[RollTable, RollTableCreate, RollTableUpdate]):
    def __init__(self, db_session: DBSession):
        super(RollTableService, self).__init__(RollTable, db_session)

    def create(self, rolltable: RollTableCreate) -> RollTable:
        rolltable_obj = RollTable(name=rolltable.name)
        rows = rolltable.rows
        if rows is not None:
            rolltable_obj.rows.extend(self.create_row(r, False) for r in rows)
        try:
            self.db_session.add(rolltable_obj)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate_key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict error")
        return rolltable_obj

    def create_row(self, rolltablerow: RollTableRowCreateInTable, push_to_db=True) -> RollTableRow:
        rolltable_row_obj = RollTableRow(
            name=rolltablerow.name,
            display_name=rolltablerow.display_name
            if rolltablerow.display_name is not None
            else rolltablerow.name,
        )
        extra_data = rolltablerow.extra_data
        if extra_data is not None:
            rolltable_row_obj.extra_data.extend(
                RollTableRowExtra(**d.model_dump()) for d in extra_data
            )
        if push_to_db:
            self.db_session.add(rolltable_row_obj)
            try:
                self.db_session.commit()
            except IntegrityError as e:
                self.db_session.rollback()
                if "duplicate key" in str(e):
                    raise HTTPException(status_code=409, detail="Conflict Error")
                else:
                    raise e
        return rolltable_row_obj

    def update(self, id: Any, obj: RollTableUpdate) -> RollTable:
        db_obj = self.get(id)
        model_dump = obj.model_dump(exclude_unset=True)
        for column, value in model_dump.items():
            if column == "rows":
                try:
                    for row in model_dump[column]:  # loop over rolltablerow elements
                        if "id" in row:  # If the row already exists
                            row_obj = self.db_session.scalar(
                                select(RollTableRow).where(RollTableRow.id == row["id"])
                            )
                            for col, val in row.items():
                                if col != "id":
                                    setattr(row_obj, col, val)
                        else:  # If the row does not exist
                            row_obj = self.create_row(row, push_to_db=False)
                            db_obj.rows.append(row_obj)
                except Exception as e:
                    raise e
            else:
                setattr(db_obj, column, value)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise HTTPException(status_code=409, detail="Conflict Error")
            else:
                raise e
        return db_obj


class RollTableRowService(BaseService[RollTableRow, RollTableRowCreate, RollTableRowUpdate]):
    def __init__(self, db_session: DBSession):
        super(RollTableRowService, self).__init__(RollTableRow, db_session)
