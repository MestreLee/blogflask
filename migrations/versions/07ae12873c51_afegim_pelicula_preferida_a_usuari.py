"""afegim pelicula preferida a usuari

Revision ID: 07ae12873c51
Revises: 
Create Date: 2022-02-24 13:13:59.897471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07ae12873c51'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('pelicula_preferida', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'pelicula_preferida')
    # ### end Alembic commands ###