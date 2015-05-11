from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
shape = Table('shape', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('shape_id', String(length=32)),
    Column('shape_pt_lat', Float),
    Column('shape_pt_lon', Float),
    Column('shape_pt_sequence', Integer),
    Column('shape_dist_traveled', Float),
)

route = Table('route', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('route_id', String(length=32)),
    Column('agency_id', String(length=64)),
    Column('trip_id', String(length=32)),
    Column('route_short_name', String(length=256)),
    Column('route_long_name', String(length=512)),
    Column('route_desc', Text),
    Column('route_type', Integer),
    Column('route_url', String(length=256)),
    Column('route_color', String(length=6), default=ColumnDefault('FFFFFF')),
    Column('route_text_color', String(length=6), default=ColumnDefault('000000')),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['shape'].create()
    post_meta.tables['route'].columns['trip_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['shape'].drop()
    post_meta.tables['route'].columns['trip_id'].drop()
