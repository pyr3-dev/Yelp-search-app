"""add_pg_trgm_indexes

Revision ID: 8c7e8c81b668
Revises: ff2141bac104
Create Date: 2026-04-08 16:19:00.079471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c7e8c81b668'
down_revision: Union[str, Sequence[str], None] = 'ff2141bac104'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX business_city_trgm_idx ON business USING gin (city gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX business_name_trgm_idx ON business USING gin (name gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS business_name_trgm_idx")
    op.execute("DROP INDEX IF EXISTS business_city_trgm_idx")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
