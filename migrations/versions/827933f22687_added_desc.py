"""Added desc

Revision ID: 827933f22687
Revises: 4d3e7c147844
Create Date: 2019-08-02 00:09:35.875130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '827933f22687'
down_revision = '4d3e7c147844'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('links', sa.Column('description', sa.String(length=20), nullable=True))
    op.add_column('links', sa.Column('expiration', sa.Boolean(), nullable=True))
    op.add_column('links', sa.Column('expiration_date', sa.DateTime(), nullable=True))
    op.add_column('links', sa.Column('password_hash', sa.String(length=250), nullable=True))
    op.add_column('links', sa.Column('password_protect', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('links', 'password_protect')
    op.drop_column('links', 'password_hash')
    op.drop_column('links', 'expiration_date')
    op.drop_column('links', 'expiration')
    op.drop_column('links', 'description')
    # ### end Alembic commands ###