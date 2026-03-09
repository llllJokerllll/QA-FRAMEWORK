"""add performance indexes

Revision ID: 20260309_performance
Revises: 20260227_add_feedback_beta
Create Date: 2026-03-09 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260309_performance'
down_revision = '20260227_add_feedback_beta'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for frequently queried columns"""
    
    # Test executions - created_at for time-series queries
    op.create_index(
        'idx_test_executions_created_at',
        'test_executions',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Test executions - status for filtering
    op.create_index(
        'idx_test_executions_status',
        'test_executions',
        ['status'],
        postgresql_using='btree'
    )
    
    # Test executions - composite index for dashboard queries
    op.create_index(
        'idx_test_executions_suite_status_created',
        'test_executions',
        ['suite_id', 'status', 'created_at'],
        postgresql_using='btree'
    )
    
    # Test cases - suite_id for filtering
    op.create_index(
        'idx_test_cases_suite_id',
        'test_cases',
        ['suite_id'],
        postgresql_using='btree'
    )
    
    # Test cases - is_active for soft delete queries
    op.create_index(
        'idx_test_cases_is_active',
        'test_cases',
        ['is_active'],
        postgresql_using='btree'
    )
    
    # Users - email for login queries
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        postgresql_using='btree',
        postgresql_unique=True
    )
    
    # Users - username for login queries
    op.create_index(
        'idx_users_username',
        'users',
        ['username'],
        postgresql_using='btree',
        postgresql_unique=True
    )
    
    # Users - stripe_customer_id for billing queries
    op.create_index(
        'idx_users_stripe_customer_id',
        'users',
        ['stripe_customer_id'],
        postgresql_using='btree'
    )
    
    # Test suites - is_active for soft delete queries
    op.create_index(
        'idx_test_suites_is_active',
        'test_suites',
        ['is_active'],
        postgresql_using='btree'
    )
    
    # Test suites - created_by for user filtering
    op.create_index(
        'idx_test_suites_created_by',
        'test_suites',
        ['created_by'],
        postgresql_using='btree'
    )
    
    # API keys - user_id for authentication
    op.create_index(
        'idx_api_keys_user_id',
        'api_keys',
        ['user_id'],
        postgresql_using='btree'
    )
    
    # API keys - key for authentication
    op.create_index(
        'idx_api_keys_key',
        'api_keys',
        ['key'],
        postgresql_using='btree',
        postgresql_unique=True
    )
    
    # Feedback - created_at for time-series queries
    op.create_index(
        'idx_feedback_created_at',
        'feedback',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Feedback - status for filtering
    op.create_index(
        'idx_feedback_status',
        'feedback',
        ['status'],
        postgresql_using='btree'
    )
    
    # Beta signups - email for duplicate check
    op.create_index(
        'idx_beta_signups_email',
        'beta_signups',
        ['email'],
        postgresql_using='btree',
        postgresql_unique=True
    )
    
    # Beta signups - status for filtering
    op.create_index(
        'idx_beta_signups_status',
        'beta_signups',
        ['status'],
        postgresql_using='btree'
    )


def downgrade():
    """Remove performance indexes"""
    
    # Drop all indexes created in upgrade
    op.drop_index('idx_test_executions_created_at', 'test_executions')
    op.drop_index('idx_test_executions_status', 'test_executions')
    op.drop_index('idx_test_executions_suite_status_created', 'test_executions')
    op.drop_index('idx_test_cases_suite_id', 'test_cases')
    op.drop_index('idx_test_cases_is_active', 'test_cases')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_stripe_customer_id', 'users')
    op.drop_index('idx_test_suites_is_active', 'test_suites')
    op.drop_index('idx_test_suites_created_by', 'test_suites')
    op.drop_index('idx_api_keys_user_id', 'api_keys')
    op.drop_index('idx_api_keys_key', 'api_keys')
    op.drop_index('idx_feedback_created_at', 'feedback')
    op.drop_index('idx_feedback_status', 'feedback')
    op.drop_index('idx_beta_signups_email', 'beta_signups')
    op.drop_index('idx_beta_signups_status', 'beta_signups')
