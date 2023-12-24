"""image_entities

Revision ID: 3a5d7ae4cb22
Revises: 40c61f0c926b
Create Date: 2023-12-20 22:40:05.190062

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3a5d7ae4cb22"
down_revision: Union[str, None] = "40c61f0c926b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "image_entities",
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["entities.id"], name=op.f("fk_image_entities_entity_id_entities")
        ),
        sa.ForeignKeyConstraint(
            ["image_id"], ["images.id"], name=op.f("fk_image_entities_image_id_images")
        ),
        sa.PrimaryKeyConstraint("image_id", "entity_id", name=op.f("pk_image_entities")),
    )
    # ### end Alembic commands ###

    # insert into image_entities
    # select image_id, id as entity_id from entities
    # where image_id is NOT NULL


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("image_entities")
    # ### end Alembic commands ###
