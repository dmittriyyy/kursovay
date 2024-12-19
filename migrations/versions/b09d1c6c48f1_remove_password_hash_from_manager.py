"""remove password_hash from Manager

Revision ID: b09d1c6c48f1
Revises: 64319b1f9e8f
Create Date: 2024-11-24 20:27:59.505542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b09d1c6c48f1'
down_revision = '64319b1f9e8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manager', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['phone'])
        batch_op.create_unique_constraint(None, ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manager', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###