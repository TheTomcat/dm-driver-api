from sqlalchemy import VARCHAR, String
import sqlalchemy.types as types
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import Annotated

Intpk = Annotated[int, mapped_column(primary_key=True)]
foreign_key = int
str256 = Annotated[str, mapped_column(String(256))]
str128 = Annotated[str, mapped_column(String(128))]
str100 = Annotated[str, mapped_column(String(100))]
str64_i = Annotated[str, mapped_column(String(64), index=True)]
str64 = Annotated[str, mapped_column(String(64))]


class Base(DeclarativeBase):
    id: Mapped[Intpk]
    __name__: str

    type_annotation_map = {
        str256: String(256),
        str128: String(128),
        str100: String(100),
        str64_i: String(64),
        str64: String(64),
    }

    def __eq__(self, other: "Base"):
        return self.id == other.id

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

    def __hash__(self):
        return sum(
            hash(self.__getattribute__(column))
            for column in (c[0] for c in self.__table__.columns.items())
        )

    # Generate __tablename__ automatically
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()+'s'
    

class CSV(types.TypeDecorator):
    '''Outside of the database is a list of strings, inside is a comma delimited string
    '''

    impl = VARCHAR

    cache_ok = True

    def process_bind_param(self, value: list[str], dialect) -> str:
        return ','.join(value)

    def process_result_value(self, value: str, dialect) -> list[str]:
        return value.split(',')

    def copy(self, **kw):
        return CSV(self.impl.length)