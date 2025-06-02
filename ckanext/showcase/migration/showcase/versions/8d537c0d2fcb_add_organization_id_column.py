"""Add organization_id column

Revision ID: 8d537c0d2fcb
Revises: 02b006cb222c
Create Date: 2025-06-03 08:46:13.157749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d537c0d2fcb'
down_revision = '02b006cb222c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'showcase_package_association',
        sa.Column('organization_id',
                  sa.types.UnicodeText,
                  sa.ForeignKey('group.id', ondelete='CASCADE', onupdate='CASCADE'),
                  primary_key=True,
                  nullable=True,
        )
    )


def downgrade():
    op.drop_column('showcase_package_association', 'organization_id')
