"""create_yelp_tables

Revision ID: ff2141bac104
Revises: 954a910e0046
Create Date: 2026-04-08 05:48:31.516584

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ff2141bac104"
down_revision: Union[str, Sequence[str], None] = "954a910e0046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "yelp_user",
        sa.Column("user_id", sa.String(22), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("yelping_since", sa.DateTime(), nullable=True),
        sa.Column("average_stars", sa.Float(), nullable=True),
        sa.Column("fans", sa.Integer(), nullable=True),
    )

    op.create_table(
        "business",
        sa.Column("business_id", sa.String(22), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True, index=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("stars", sa.Float(), nullable=True, index=True),
        sa.Column("review_count", sa.Integer(), nullable=True, index=True),
        sa.Column("is_open", sa.Boolean(), nullable=True),
        sa.Column("attributes", JSONB(), nullable=True),
        sa.Column("categories", ARRAY(sa.String()), nullable=True),
        sa.Column("hours", JSONB(), nullable=True),
    )
    op.create_index(
        "ix_business_categories_gin",
        "business",
        ["categories"],
        postgresql_using="gin",
    )

    op.create_table(
        "review",
        sa.Column("review_id", sa.String(22), primary_key=True),
        sa.Column("user_id", sa.String(22), nullable=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("stars", sa.SmallInteger(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("useful", sa.Integer(), nullable=True),
        sa.Column("funny", sa.Integer(), nullable=True),
        sa.Column("cool", sa.Integer(), nullable=True),
    )

    op.create_table(
        "tip",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("compliment_count", sa.Integer(), nullable=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("user_id", sa.String(22), nullable=True),
    )

    op.create_table(
        "checkin",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            unique=True,
        ),
        sa.Column("dates", sa.Text(), nullable=True),
    )

    op.create_table(
        "photo",
        sa.Column("photo_id", sa.String(22), primary_key=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("label", sa.String(10), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("photo")
    op.drop_table("checkin")
    op.drop_table("tip")
    op.drop_table("review")
    op.drop_index("ix_business_categories_gin", table_name="business")
    op.drop_table("business")
    op.drop_table("yelp_user")
