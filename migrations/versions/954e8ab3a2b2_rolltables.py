"""rolltables

Revision ID: 954e8ab3a2b2
Revises: 52e67fa60461
Create Date: 2024-02-17 08:35:34.347689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '954e8ab3a2b2'
down_revision: Union[str, None] = '52e67fa60461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rolltables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_rolltables'))
    )
    with op.batch_alter_table('rolltables', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rolltables_name'), ['name'], unique=False)

    op.create_table('rolltable_rows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('display_name', sa.String(length=64), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('rolltable_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['rolltable_id'], ['rolltables.id'], name=op.f('fk_rolltable_rows_rolltable_id_rolltables')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_rolltable_rows'))
    )
    with op.batch_alter_table('rolltable_rows', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rolltable_rows_name'), ['name'], unique=False)

    op.create_table('rolltable_row_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.String(length=500), nullable=False),
    sa.Column('rolltable_row_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['rolltable_row_id'], ['rolltable_rows.id'], name=op.f('fk_rolltable_row_data_rolltable_row_id_rolltable_rows')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_rolltable_row_data'))
    )
    op.drop_table('sessions')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('backdrop_id', sa.INTEGER(), nullable=True),
    sa.Column('overlay_image_id', sa.INTEGER(), nullable=True),
    sa.Column('message_id', sa.INTEGER(), nullable=True),
    sa.Column('combat_id', sa.INTEGER(), nullable=True),
    sa.Column('mode', sa.VARCHAR(length=8), nullable=False),
    sa.ForeignKeyConstraint(['backdrop_id'], ['images.id'], name='fk_sessions_backdrop_id_images'),
    sa.ForeignKeyConstraint(['combat_id'], ['combat.id'], name='fk_sessions_combat_id_combat'),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], name='fk_sessions_message_id_messages'),
    sa.ForeignKeyConstraint(['overlay_image_id'], ['images.id'], name='fk_sessions_overlay_image_id_images'),
    sa.PrimaryKeyConstraint('id', name='pk_sessions')
    )
    op.drop_table('rolltable_row_data')
    with op.batch_alter_table('rolltable_rows', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rolltable_rows_name'))

    op.drop_table('rolltable_rows')
    with op.batch_alter_table('rolltables', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rolltables_name'))

    op.drop_table('rolltables')
    # ### end Alembic commands ###