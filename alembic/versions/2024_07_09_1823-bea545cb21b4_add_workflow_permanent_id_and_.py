"""Add workflow_permanent_id and organization_id to workflow_runs table

Revision ID: bea545cb21b4
Revises: 485667adef01
Create Date: 2024-07-09 18:23:03.641136+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bea545cb21b4"
down_revision: Union[str, None] = "485667adef01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workflow_runs", sa.Column("workflow_permanent_id", sa.String(), nullable=True))
    op.add_column("workflow_runs", sa.Column("organization_id", sa.String(), nullable=True))

    # Backfill the new columns with data from the workflows table
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE workflow_runs wr
            SET workflow_permanent_id = (
                SELECT workflow_permanent_id
                FROM workflows w
                WHERE w.workflow_id = wr.workflow_id
            ),
            organization_id = (
                SELECT organization_id
                FROM workflows w
                WHERE w.workflow_id = wr.workflow_id
            )
        """)
    )

    # Now set the columns to be non-nullable
    op.alter_column("workflow_runs", "workflow_permanent_id", nullable=False)
    op.alter_column("workflow_runs", "organization_id", nullable=False)

    # Create foreign keys and indices after backfilling
    op.create_foreign_key(
        "fk_workflow_runs_organization_id", "workflow_runs", "organizations", ["organization_id"], ["organization_id"]
    )
    op.create_index("ix_workflow_runs_organization_id", "workflow_runs", ["organization_id"], unique=False)
    op.create_index("ix_workflow_runs_workflow_permanent_id", "workflow_runs", ["workflow_permanent_id"], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_workflow_runs_organization_id", "workflow_runs", type_="foreignkey")
    op.drop_column("workflow_runs", "organization_id")
    op.drop_column("workflow_runs", "workflow_permanent_id")
    # ### end Alembic commands ###
