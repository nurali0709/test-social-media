"""added image field to user table

Revision ID: 181a54280fae
Revises: c8a78befe351
Create Date: 2023-07-21 22:23:32.039911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '181a54280fae'
down_revision = 'c8a78befe351'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'image')
    # ### end Alembic commands ###
