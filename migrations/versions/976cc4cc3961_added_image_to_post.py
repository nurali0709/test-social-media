"""added image to post

Revision ID: 976cc4cc3961
Revises: cfe350a4d53d
Create Date: 2023-08-19 15:31:53.945362

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '976cc4cc3961'
down_revision = 'cfe350a4d53d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'image')
    # ### end Alembic commands ###
