"""empty message

Revision ID: f0acdaba6da2
Revises: 1af82b0327ea
Create Date: 2024-08-07 08:07:32.855676

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0acdaba6da2"
down_revision: Union[str, None] = "1af82b0327ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("messages", sa.Column("image_path", sa.String(length=400), nullable=True))
    op.drop_table("message_images")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("messages", "image_path")
    op.create_table(
        "message_images",
        sa.Column("message_image_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=300), nullable=False),
        sa.PrimaryKeyConstraint("message_image_id"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.message_id"], ondelete="CASCADE"),
    )
    # ### end Alembic commands ###
