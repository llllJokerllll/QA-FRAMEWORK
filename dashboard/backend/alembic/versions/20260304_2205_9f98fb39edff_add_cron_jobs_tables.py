"""add_cron_jobs_tables

Revision ID: 9f98fb39edff
Revises: 20260227_add_feedback_beta
Create Date: 2026-03-04 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f98fb39edff'
down_revision = '20260227_add_feedback_beta'
branch_labels = None
depends_on = None


def upgrade():
    # Create cron_jobs table
    op.create_table(
        'cron_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('schedule', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('script_path', sa.String(), nullable=False),
        sa.Column('last_run', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('next_run', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cron_executions table
    op.create_table(
        'cron_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['cron_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_cron_jobs_id'), 'cron_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_cron_jobs_name'), 'cron_jobs', ['name'], unique=True)
    op.create_index(op.f('ix_cron_executions_id'), 'cron_executions', ['id'], unique=False)
    op.create_index(op.f('ix_cron_executions_job_id'), 'cron_executions', ['job_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_cron_executions_job_id'), table_name='cron_executions')
    op.drop_index(op.f('ix_cron_executions_id'), table_name='cron_executions')
    op.drop_index(op.f('ix_cron_jobs_name'), table_name='cron_jobs')
    op.drop_index(op.f('ix_cron_jobs_id'), table_name='cron_jobs')

    # Drop tables
    op.drop_table('cron_executions')
    op.drop_table('cron_jobs')
