"""updated db

Revision ID: 39cd30eddd42
Revises: d0ed2339a177
Create Date: 2024-05-10 09:44:12.480889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39cd30eddd42'
down_revision = 'd0ed2339a177'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Unit', schema=None) as batch_op:
        batch_op.drop_column('reserved')
        batch_op.drop_column('unit_image')
        batch_op.drop_column('air_conditioning')
        batch_op.drop_column('amenities')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Unit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amenities', sa.VARCHAR(length=3, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('air_conditioning', sa.VARCHAR(length=3, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('unit_image', sa.VARCHAR(length=50, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('reserved', sa.VARCHAR(length=5, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
