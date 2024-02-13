"""CR to float

Revision ID: 2a5af4b00ce8
Revises: 4491524593f7
Create Date: 2024-02-13 10:35:05.581229

https://www.julo.ch/blog/migrating-content-with-alembic/
http://ominian.com/2019/07/11/data-migration-with-sqlalchemy-and-alembic/

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from core.utils import decodeCR, encodeCR

# revision identifiers, used by Alembic.
revision: str = "2a5af4b00ce8"
down_revision: Union[str, None] = "4491524593f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


cr_helper = sa.Table(
    "entities",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("cr", sa.String(10)),
    sa.Column("_cr", sa.Float),
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    # session = orm.Session(bind=connection)
    op.add_column("entities", sa.Column("_cr", sa.Float, nullable=True))

    for entity in connection.execute(cr_helper.select()):
        cr: str | None = entity.cr
        connection.execute(
            cr_helper.update().where(cr_helper.c.id == entity.id).values(_cr=encodeCR(cr))
        )
    with op.batch_alter_table("entities", schema=None) as batch_op:
        # temp = "cr_old"
        batch_op.alter_column("cr", new_column_name="_cr")
        batch_op.alter_column("_cr", new_column_name="cr")
        batch_op.drop_column("cr")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    # session = orm.Session(bind=connection)
    op.add_column("entities", sa.Column("_cr", sa.VARCHAR(length=10), nullable=True))

    for entity in connection.execute(cr_helper.select()):
        cr: float | None = entity.cr
        connection.execute(
            cr_helper.update().where(cr_helper.c.id == entity.id).values(_cr=decodeCR(cr))
        )

    with op.batch_alter_table("entities", schema=None) as batch_op:
        # temp = "cr_old"
        batch_op.alter_column("cr", new_column_name="_cr")
        batch_op.alter_column("_cr", new_column_name="cr")
        batch_op.drop_column("cr")
        # batch_op.alter_column(
        #     "cr", existing_type=sa.Float(), type_=sa.VARCHAR(length=10), nullable=False
        # )

    # ### end Alembic commands ###
