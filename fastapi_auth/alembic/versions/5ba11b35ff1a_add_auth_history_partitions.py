"""add_auth_history_partitions

Revision ID: 5ba11b35ff1a
Revises: cf9ba141e72d
Create Date: 2025-05-10 07:01:03.057228

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError



# revision identifiers, used by Alembic.
revision = "5ba11b35ff1a"
down_revision = "cf9ba141e72d"
branch_labels = None
depends_on = None

def create_partition(target, connection, device_types: list = None, **kw) -> None:
    """Создание партиций по типу устройства"""
    device_types = device_types or ["smart", "mobile", "web"]

    try:
        for device_type in device_types:
            partition_table_name = f"auth.auth_history_{device_type}"
            sql = text(
                f"""
                CREATE TABLE IF NOT EXISTS "{partition_table_name}"
                PARTITION OF auth."auth_history"
                FOR VALUES IN ('{device_type}')
                """
            )
            connection.execute(sql)
    except SQLAlchemyError as e: 
        raise SQLAlchemyError("Ошибка create_partition для auth_history") from e


def upgrade():
    connection = op.get_bind()
    create_partition(None, connection)


def downgrade():
    onnection = op.get_bind()
    device_types = ["smart", "mobile", "web"]
    for device_type in device_types:
        partition_table_name = f"auth.auth_history_{device_type}"
        op.drop_table(partition_table_name)
