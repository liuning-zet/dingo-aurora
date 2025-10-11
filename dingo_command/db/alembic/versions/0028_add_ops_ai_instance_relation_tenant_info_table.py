"""0026

Revision ID: 0028
Revises: 0027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0028'
down_revision: Union[str, None] = '0027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ops_ai_instance_relation_tenant_info',
        sa.Column("id", sa.String(length=128), nullable=False, index=True, comment='主键UUID'),
        sa.Column('k8s_id', sa.String(length=128), nullable=True, comment='k8s的id'),
        sa.Column('tenant_id', sa.String(length=128), nullable=True, comment='租户的id'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='容器实例租户关联表'
    )

def downgrade() -> None:
    op.drop_table('ops_ai_instance_relation_tenant_info')