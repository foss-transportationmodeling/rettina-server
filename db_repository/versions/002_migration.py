from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
route = Table('route', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('route_id', String(length=32)),
    Column('trip_id', String(length=32)),
    Column('route_short_name', String(length=256)),
    Column('route_long_name', String(length=512)),
    Column('route_desc', Text),
    Column('route_type', Integer),
    Column('route_url', String(length=256)),
    Column('route_color', String(length=6), default=ColumnDefault('FFFFFF')),
    Column('route_text_color', String(length=6), default=ColumnDefault('000000')),
    Column('agency_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['route'].columns['agency_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['route'].columns['agency_id'].drop()
