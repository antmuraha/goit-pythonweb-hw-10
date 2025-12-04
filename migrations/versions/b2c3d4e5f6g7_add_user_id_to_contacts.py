"""Add user_id to contacts

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-04 18:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add user_id column to contacts table
    op.add_column("contacts", sa.Column("user_id", sa.Integer(), nullable=True))
    
    # Create index on user_id
    op.create_index(op.f("ix_contacts_user_id"), "contacts", ["user_id"], unique=False)
    
    # Create foreign key constraint
    op.create_foreign_key(
        "fk_contacts_user_id_users",
        "contacts",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Note: In a real migration with existing data, you would:
    # 1. First add the column as nullable
    # 2. Populate it with a default user or migrate existing data
    # 3. Then alter the column to be NOT NULL
    # For a fresh database, we can make it NOT NULL after adding it
    op.alter_column("contacts", "user_id", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_contacts_user_id_users", "contacts", type_="foreignkey")
    op.drop_index(op.f("ix_contacts_user_id"), table_name="contacts")
    op.drop_column("contacts", "user_id")
