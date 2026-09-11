"""Fix geometry_geojson column type from VARCHAR to TEXT

Revision ID: fix_geometry_geojson
Revises: create_route_table
Create Date: 2026-09-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_geometry_geojson'
down_revision = 'create_route_table'
branch_labels = None
depends_on = None


def upgrade():
    # Change geometry_geojson column type from VARCHAR to TEXT
    op.alter_column(
        'route',
        'geometry_geojson',
        existing_type=sa.String(length=65535),
        type_=sa.Text(),
        existing_nullable=True,
        nullable=True
    )


def downgrade():
    # Revert back to VARCHAR for downgrade
    op.alter_column(
        'route',
        'geometry_geojson',
        existing_type=sa.Text(),
        type_=sa.String(length=65535),
        existing_nullable=True,
        nullable=True
    )

