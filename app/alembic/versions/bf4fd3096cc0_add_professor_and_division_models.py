"""add Professor and Division models

Revision ID: bf4fd3096cc0
Revises: 47da74065fe7
Create Date: 2021-04-04 00:08:44.179500

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bf4fd3096cc0'
down_revision = '47da74065fe7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('professor',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_professor_user_id'), 'professor', ['user_id'], unique=False)
    op.create_table('division',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('division_code', sa.Integer(), nullable=False),
    sa.Column('professor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['professor_id'], ['professor.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'division_code', name='_unique_by_course_division')
    )
    op.create_index(op.f('ix_division_course_id'), 'division', ['course_id'], unique=False)
    op.create_index(op.f('ix_division_division_code'), 'division', ['division_code'], unique=False)
    op.create_index(op.f('ix_division_id'), 'division', ['id'], unique=False)
    op.create_index(op.f('ix_division_professor_id'), 'division', ['professor_id'], unique=False)
    op.drop_index('ix_course_panel_code', table_name='course')
    op.drop_constraint('_unique_by_name_code_term', 'course', type_='unique')
    op.create_unique_constraint('_unique_by_name_code_term', 'course', ['name', 'course_code', 'term_id'])
    op.drop_column('course', 'panel_code')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('panel_code', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint('_unique_by_name_code_term', 'course', type_='unique')
    op.create_unique_constraint('_unique_by_name_code_term', 'course', ['name', 'course_code', 'panel_code', 'term_id'])
    op.create_index('ix_course_panel_code', 'course', ['panel_code'], unique=False)
    op.drop_index(op.f('ix_division_professor_id'), table_name='division')
    op.drop_index(op.f('ix_division_id'), table_name='division')
    op.drop_index(op.f('ix_division_division_code'), table_name='division')
    op.drop_index(op.f('ix_division_course_id'), table_name='division')
    op.drop_table('division')
    op.drop_index(op.f('ix_professor_user_id'), table_name='professor')
    op.drop_table('professor')
    # ### end Alembic commands ###