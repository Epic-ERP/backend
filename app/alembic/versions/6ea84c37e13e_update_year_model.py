"""update year model

Revision ID: 6ea84c37e13e
Revises: 7b2f235b8ffe
Create Date: 2021-03-07 18:28:06.956510

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ea84c37e13e'
down_revision = '7b2f235b8ffe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('year', sa.Column('name', sa.String(length=100), nullable=False))
    op.alter_column('year', 'end_year',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('year', 'school_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('year', 'start_year',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.create_index(op.f('ix_year_name'), 'year', ['name'], unique=False)
    op.create_unique_constraint(None, 'year', ['name', 'school_id', 'start_year', 'end_year'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'year', type_='unique')
    op.drop_index(op.f('ix_year_name'), table_name='year')
    op.alter_column('year', 'start_year',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('year', 'school_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('year', 'end_year',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.drop_column('year', 'name')
    # ### end Alembic commands ###
