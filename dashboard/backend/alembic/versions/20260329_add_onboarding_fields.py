"""add onboarding fields to users

Revision ID: 20260329_onboarding
Revises: 20260309_performance
Create Date: 2026-03-29 05:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '20260329_onboarding'
down_revision = '20260309_performance'
branch_labels = None
depends_on = None


def upgrade():
    """Add onboarding tracking fields to users table"""
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('onboarding_state', JSONB(), nullable=True, server_default='{}'))
    op.add_column('users', sa.Column('onboarding_completed_at', sa.DateTime(), nullable=True))


def downgrade():
    """Remove onboarding fields from users table"""
    op.drop_column('users', 'onboarding_completed_at')
    op.drop_column('users', 'onboarding_state')
    op.drop_column('users', 'onboarding_completed')
