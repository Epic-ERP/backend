"""Increase size of profile_picture field

Revision ID: bacefdad7004
Revises: 7b2f235b8ffe
Create Date: 2021-03-04 17:11:30.528539

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bacefdad7004'
down_revision = '7b2f235b8ffe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'profile_picture',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=36),
               type_=sa.String(length=41),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'profile_picture',
               existing_type=sa.String(length=41),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=36),
               existing_nullable=True)
    # ### end Alembic commands ###