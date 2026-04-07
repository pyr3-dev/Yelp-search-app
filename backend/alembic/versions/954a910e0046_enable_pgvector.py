"""enable_pgvector

Revision ID: 954a910e0046
Revises: f167e13c491b
Create Date: 2026-04-06 08:50:43.753338

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "954a910e0046"
down_revision: Union[str, Sequence[str], None] = "f167e13c491b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.drop_table("idea")
    op.drop_table("query_paper")
    op.drop_table("paper")
    op.drop_table("search_query")
    op.drop_table("search_session")
    # Leave the vector extension installed
