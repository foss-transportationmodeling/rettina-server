from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
shape = Table('shape', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('shape_id', INTEGER),
    Column('shape_pt_lat', FLOAT),
    Column('shape_pt_lon', FLOAT),
    Column('shape_pt_sequence', INTEGER),
    Column('shape_dist_traveled', FLOAT),
    Column('trip_id', INTEGER),
)

trip = Table('trip', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('service_id', String(length=32)),
    Column('trip_id', String(length=32)),
    Column('shape_id', Integer),
    Column('trip_headsign', String(length=32)),
    Column('trip_short_name', String(length=64)),
    Column('direction_id', Integer),
    Column('block_id', Integer),
    Column('wheelchair_accessible', Integer),
    Column('bikes_allowed', Integer),
    Column('route_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['shape'].columns['trip_id'].drop()
    post_meta.tables['trip'].columns['shape_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['shape'].columns['trip_id'].create()
    post_meta.tables['trip'].columns['shape_id'].drop()
