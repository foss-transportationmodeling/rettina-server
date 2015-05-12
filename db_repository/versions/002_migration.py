from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
stops = Table('stops', post_meta,
    Column('stop_id', Integer),
    Column('trip_id', Integer),
)

stop = Table('stop', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('stop_id', VARCHAR(length=32)),
    Column('stop_code', VARCHAR(length=16)),
    Column('stop_name', VARCHAR(length=128)),
    Column('stop_desc', TEXT),
    Column('stop_lat', FLOAT),
    Column('stop_lon', FLOAT),
    Column('zone_id', VARCHAR(length=32)),
    Column('stop_url', VARCHAR(length=256)),
    Column('location_type', INTEGER),
    Column('parent_station', VARCHAR(length=32)),
    Column('stop_timezone', VARCHAR(length=2)),
    Column('wheelchair_boarding', INTEGER),
    Column('trip_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['stops'].create()
    pre_meta.tables['stop'].columns['trip_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['stops'].drop()
    pre_meta.tables['stop'].columns['trip_id'].create()
