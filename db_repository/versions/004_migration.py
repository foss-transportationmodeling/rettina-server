from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
stop_time = Table('stop_time', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('trip_id', String(length=32)),
    Column('arrival_time', String(length=16)),
    Column('departure_time', String(length=16)),
    Column('stop_id', String(length=32)),
    Column('stop_sequence', Integer),
    Column('stop_headsign', String(length=64)),
    Column('pickup_type', Integer),
    Column('drop_off_type', Integer),
    Column('shape_dist_traveled', String(length=32)),
    Column('timepoint', Integer),
    Column('stop_lat', Float),
    Column('stop_lon', Float),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['stop_time'].columns['stop_lat'].create()
    post_meta.tables['stop_time'].columns['stop_lon'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['stop_time'].columns['stop_lat'].drop()
    post_meta.tables['stop_time'].columns['stop_lon'].drop()
