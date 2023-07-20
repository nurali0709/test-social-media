"""added verification field to user table

Revision ID: 4b8d9d3c6dfd
Revises: 9d3b02cfe449
Create Date: 2023-07-20 17:09:48.820663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b8d9d3c6dfd'
down_revision = '9d3b02cfe449'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('verification_code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'verification_code')
    # ### end Alembic commands ###
