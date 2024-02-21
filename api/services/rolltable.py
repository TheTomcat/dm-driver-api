from sqlite3 import IntegrityError
from typing import Any

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DBSession

from api.models import RollTable, RollTableRow, RollTableRowExtra
from api.schemas import (
    RollTableCreate,
    RollTableRowCreateInTable,
    RollTableRowCreateStandalone,
    RollTableRowUpdate,
    RollTableUpdate,
)
from core.utils import make_sortable_name

from .base import BaseService


class RollTableService(BaseService[RollTable, RollTableCreate, RollTableUpdate]):
    def __init__(self, db_session: DBSession):
        super(RollTableService, self).__init__(RollTable, db_session)

    def create(self, rolltable: RollTableCreate) -> RollTable:
        rolltable_obj = RollTable(name=rolltable.name)
        rows = rolltable.rows
        if rows is not None:
            rolltable_obj.rows.extend(self.create_row(r.model_dump(), False) for r in rows)
        try:
            self.db_session.add(rolltable_obj)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if "duplicate_key" in str(e):
                raise HTTPException(status_code=409, detail="Conflict error")
        return rolltable_obj

    def add_row_to_table(self, rolltable_id: int, rolltable_row: RollTableRowCreateInTable):
        rolltable = self.get(rolltable_id)
        if not rolltable:
            raise HTTPException(status_code=404, detail=f"<Rolltable id={rolltable_id}> not found.")
        try:
            rolltable.rows.append(self.create_row(rolltable_row.model_dump()))
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail="Bad request")
        return rolltable

    def delete_row_from_table(self, rolltable_row_id: int):
        query = delete(RollTableRow).where(RollTableRow.id == rolltable_row_id)
        try:
            self.db_session.execute(query)
            self.db_session.commit()
        except IntegrityError:
            self.db_session.rollback()

    def create_row(self, rolltablerow: dict[str, Any], push_to_db=True) -> RollTableRow:
        # print(rolltablerow)
        rolltable_row_obj = RollTableRow(
            name=rolltablerow["name"],
            display_name=make_sortable_name(rolltablerow["name"]),
        )
        extra_data = rolltablerow.get("extra_data", None)
        if extra_data is not None:
            rolltable_row_obj.extra_data.extend(RollTableRowExtra(**d) for d in extra_data)
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
                # print(model_dump[column])
                try:
                    rows = []
                    for row in model_dump[column]:  # loop over rolltablerow elements
                        if "rolltable_row_id" in row:  # If the row already exists
                            row_obj = self.db_session.scalar(
                                select(RollTableRow).where(
                                    RollTableRow.id == row["rolltable_row_id"]
                                )
                            )
                            if row_obj is None:
                                raise HTTPException(status_code=400, detail="Bad request")
                            for column_name, val in row.items():
                                if column_name != "rolltable_row_id":
                                    print(column_name)

                                    setattr(row_obj, column_name, val)
                        else:  # If the row does not exist
                            row_obj = self.create_row(row, push_to_db=False)
                        rows.append(row_obj)
                    db_obj.rows = rows
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


class RollTableRowService(
    BaseService[RollTableRow, RollTableRowCreateStandalone, RollTableRowUpdate]
):
    def __init__(self, db_session: DBSession):
        super(RollTableRowService, self).__init__(RollTableRow, db_session)
