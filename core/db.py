import sqlalchemy.types as types
from sqlalchemy import VARCHAR, MetaData, String
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
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
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
        return cls.__name__.lower() + "s"

    # def __init__(self, **kwargs):
    #     """A simple constructor that allows initialization from kwargs.

    #     Sets attributes on the constructed instance using the names and
    #     values in ``kwargs``.

    #     Only keys that are present as
    #     attributes of the instance's class are allowed. These could be,
    #     for example, any mapped columns or relationships.

    #     EDITED by Samuel to auto_instantiate nested lists's elements as child classes
    #     """
    #     cls_ = type(self)
    #     relationships = self.__mapper__.relationships
    #     for k in kwargs:
    #         if not hasattr(cls_, k):
    #             raise TypeError(
    #                 "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
    #             )
    #         if k in relationships.keys():
    #             if relationships[k].direction.name == 'ONETOMANY':
    #                 childclass = getattr(sys.modules['models'], relationships[k].argument)
    #                 nestedattribute = getattr(self, k)
    #                 for elem in kwargs[k]:
    #                     new_elem = childclass(**elem)
    #                     nestedattribute.append(new_elem)
    #         else:
    #             setattr(self, k, kwargs[k])


class CSV(types.TypeDecorator):
    """Outside of the database is a list of strings, inside is a comma delimited string"""

    impl = VARCHAR

    cache_ok = True

    def process_bind_param(self, value: list[str], dialect) -> str:
        return ",".join(value)

    def process_result_value(self, value: str, dialect) -> list[str]:
        return value.split(",")

    def copy(self, **kw):
        return CSV(self.impl.length)  # type: ignore
