"""add feedback and beta signup tables

Revision ID: 20260227_add_feedback_beta
Revises: 20260224_add_oauth_api_keys_and_subscription_fields
Create Date: 2026-02-27 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260227_add_feedback_beta'
down_revision = '20260224_add_oauth_api_keys_and_subscription_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=True),
        sa.Column('feedback_type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True, default='medium'),
        sa.Column('page_url', sa.String(500), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('browser_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default='new'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True, default=[]),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True, default=[]),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    op.create_index(op.f('ix_feedback_id'), 'feedback', ['id'], unique=False)
    op.create_index(op.f('ix_feedback_user_id'), 'feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_feedback_status'), 'feedback', ['status'], unique=False)
    op.create_index(op.f('ix_feedback_type'), 'feedback', ['feedback_type'], unique=False)
    op.create_index(op.f('ix_feedback_created_at'), 'feedback', ['created_at'], unique=False)

    # Create beta_signups table
    op.create_table(
        'beta_signups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company', sa.String(200), nullable=True),
        sa.Column('use_case', sa.Text(), nullable=True),
        sa.Column('team_size', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default='pending'),
        sa.Column('invite_sent_at', sa.DateTime(), nullable=True),
        sa.Column('onboarded_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('utm_campaign', sa.String(), nullable=True),
        sa.Column('utm_source', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_beta_signups_id'), 'beta_signups', ['id'], unique=False)
    op.create_index(op.f('ix_beta_signups_email'), 'beta_signups', ['email'], unique=True)
    op.create_index(op.f('ix_beta_signups_status'), 'beta_signups', ['status'], unique=False)
    op.create_index(op.f('ix_beta_signups_source'), 'beta_signups', ['source'], unique=False)
    op.create_index(op.f('ix_beta_signups_created_at'), 'beta_signups', ['created_at'], unique=False)


def downgrade():
    # Drop feedback table
    op.drop_index(op.f('ix_feedback_created_at'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_type'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_status'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_user_id'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_id'), table_name='feedback')
    op.drop_table('feedback')

    # Drop beta_signups table
    op.drop_index(op.f('ix_beta_signups_created_at'), table_name='beta_signups')
    op.drop_index(op.f('ix_beta_signups_source'), table_name='beta_signups')
    op.drop_index(op.f('ix_beta_signups_status'), table_name='beta_signups')
    op.drop_index(op.f('ix_beta_signups_email'), table_name='beta_signups')
    op.drop_index(op.f('ix_beta_signups_id'), table_name='beta_signups')
    op.drop_table('beta_signups')
