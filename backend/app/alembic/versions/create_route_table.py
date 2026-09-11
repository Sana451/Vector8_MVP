"""Create route table with PostGIS support (optional)

Revision ID: create_route_table
Revises: fe56fa70289e
Create Date: 2026-09-10 00:00:00.000000

Notes:
  - PostGIS extension is optional. If not available, geometry is stored as TEXT.
  - For production, ensure PostgreSQL has PostGIS extension installed.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_route_table'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def check_postgis_available(connection):
    """Check if PostGIS extension is available in PostgreSQL."""
    try:
        result = connection.execute(
            sa.text("SELECT 1 FROM pg_available_extensions WHERE name='postgis'")
        )
        return result.fetchone() is not None
    except Exception:
        return False


def upgrade():
    # Get connection to check PostGIS availability
    connection = op.get_context().bind
    use_postgis = check_postgis_available(connection)

    # Try to enable PostGIS extension if available
    if use_postgis:
        try:
            op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS postgis'))
        except Exception:
            # PostGIS not available despite being listed, continue without it
            use_postgis = False

    # Create route table
    columns = [
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('start_lat', sa.Float(), nullable=False),
        sa.Column('start_lon', sa.Float(), nullable=False),
        sa.Column('end_lat', sa.Float(), nullable=False),
        sa.Column('end_lon', sa.Float(), nullable=False),
        sa.Column('distance_meters', sa.Float(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('route_geometry', sa.Text(), nullable=True),
        sa.Column('geometry_geojson', sa.String(length=65535), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    ]

    op.create_table('route', *columns)

    # Create index on created_at
    op.create_index('ix_route_created_at', 'route', ['created_at'])

    # Create spatial index on geometry if PostGIS is available
    if use_postgis:
        try:
            op.create_index(
                'ix_route_geometry',
                'route',
                ['route_geometry'],
                postgresql_using='gist'
            )
        except Exception:
            # Spatial index failed, continue without it
            pass


def downgrade():
    # Drop indexes
    try:
        op.drop_index('ix_route_geometry', table_name='route')
    except Exception:
        pass

    try:
        op.drop_index('ix_route_created_at', table_name='route')
    except Exception:
        pass

    # Drop table
    try:
        op.drop_table('route')
    except Exception:
        pass


