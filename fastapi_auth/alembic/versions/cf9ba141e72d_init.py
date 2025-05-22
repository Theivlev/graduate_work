"""init

Revision ID: cf9ba141e72d
Revises: 
Create Date: 2025-05-09 20:02:05.766587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cf9ba141e72d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.create_table(
        "role",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "permissions", sa.ARRAY(sa.Enum("read", "write", "delete", "update", name="permissions", schema="auth")), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("surname", sa.String(), nullable=True),
        sa.Column("patronymic", sa.String(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    with op.batch_alter_table("user", schema="auth") as batch_op:
        batch_op.create_index(batch_op.f("ix_user_email"), ["email"], unique=True)

    op.create_table(
        "auth_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("user_agent", sa.String(), nullable=False),
        sa.Column("user_device_type", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["auth.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", "user_device_type"),
        sa.UniqueConstraint("id", "user_device_type"),
        postgresql_partition_by="LIST (user_device_type)",
        schema="auth",
    )
    op.create_table(
        "user_role",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["auth.role.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", "user_id", "role_id"),
        schema="auth",
    )

def downgrade():
    op.drop_table("user_role", schema="auth")
    op.drop_table("auth_history", schema="auth")
    with op.batch_alter_table("user", schema="auth") as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_email"))
    op.drop_table("user", schema="auth")
    op.drop_table("role", schema="auth")
