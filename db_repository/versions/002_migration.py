from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
agency = Table('agency', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('agency_id', String(length=64)),
    Column('agency_name', String(length=128)),
    Column('agency_url', String(length=256)),
    Column('agency_timezone', String(length=64)),
    Column('agency_phone', String(length=32)),
    Column('agency_lang', String(length=2)),
    Column('agency_fare_url', String(length=256)),
)

calendar = Table('calendar', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('service_id', String(length=32)),
    Column('monday', Integer),
    Column('tuesday', Integer),
    Column('wednesday', Integer),
    Column('thursday', Integer),
    Column('friday', Integer),
    Column('saturday', Integer),
    Column('sunday', Integer),
    Column('start_date', String(length=16)),
    Column('end_date', String(length=16)),
)

calendar_date = Table('calendar_date', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('service_id', String(length=32)),
    Column('date', String(length=16)),
    Column('exception_type', Integer),
)

route = Table('route', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('route_id', String(length=32)),
    Column('agency_id', String(length=64)),
    Column('route_short_name', String(length=256)),
    Column('route_long_name', String(length=512)),
    Column('route_desc', Text),
    Column('route_type', Integer),
    Column('route_url', String(length=256)),
    Column('route_color', String(length=6), default=ColumnDefault('FFFFFF')),
    Column('route_text_color', String(length=6), default=ColumnDefault('000000')),
)

stop = Table('stop', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('stop_id', String(length=32)),
    Column('stop_code', String(length=16)),
    Column('stop_name', String(length=128)),
    Column('stop_desc', Text),
    Column('stop_lat', Float),
    Column('stop_lon', Float),
    Column('zone_id', String(length=32)),
    Column('stop_url', String(length=256)),
    Column('location_type', Integer),
    Column('parent_station', String(length=32)),
    Column('stop_timezone', String(length=2)),
    Column('wheelchair_boarding', Integer),
)

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
    Column('shape_dist_traveled', Float),
    Column('timepoint', Integer),
)

trip = Table('trip', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('route_id', String(length=32)),
    Column('service_id', String(length=32)),
    Column('trip_id', String(length=32)),
    Column('trip_headsign', String(length=32)),
    Column('trip_short_name', String(length=64)),
    Column('direction_id', Integer),
    Column('block_id', Integer),
    Column('shape_id', Integer),
    Column('wheelchair_accessible', Integer),
    Column('bikes_allowed', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['agency'].create()
    post_meta.tables['calendar'].create()
    post_meta.tables['calendar_date'].create()
    post_meta.tables['route'].create()
    post_meta.tables['stop'].create()
    post_meta.tables['stop_time'].create()
    post_meta.tables['trip'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['agency'].drop()
    post_meta.tables['calendar'].drop()
    post_meta.tables['calendar_date'].drop()
    post_meta.tables['route'].drop()
    post_meta.tables['stop'].drop()
    post_meta.tables['stop_time'].drop()
    post_meta.tables['trip'].drop()
