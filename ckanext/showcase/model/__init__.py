from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import types
from sqlalchemy.engine.reflection import Inspector

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper, Session
from ckan import model

import logging
log = logging.getLogger(__name__)


showcase_package_assocation_table = None
showcase_admin_table = None
showcase_position_table = None


def setup():
    # setup showcase_package_assocation_table
    if showcase_package_assocation_table is None:
        define_showcase_package_association_table()
        log.debug('ShowcasePackageAssociation table defined in memory')

    # setup showcase_position_table
    if showcase_position_table is None:
        define_showcase_position_table()
        log.debug('ShowcasePosition table defined in memory')

    if model.package_table.exists():
        if not showcase_package_assocation_table.exists():
            showcase_package_assocation_table.create()
            log.debug('ShowcasePackageAssociation table create')
        else:
            log.debug('ShowcasePackageAssociation table already exists')
            # Check if existing tables need to be updated
            from ckan.model.meta import engine
            inspector = Inspector.from_engine(engine)
            columns = inspector.get_columns('showcase_package_association')
            column_names = [column['name'] for column in columns]
            if 'organization_id' not in column_names:
                log.debug('ShowcasePackageAssociation table needs to be updated')
                migrate_v2()

        showcases_postions = []
        if not showcase_position_table.exists():
            showcase_position_table.create()
            log.debug('ShowcasePosition table create')
        else:
            log.debug('ShowcasePosition table already exists')
            showcases_postions = ShowcasePosition.get_showcase_postions()

        if len(showcases_postions) == 0:
            log.debug('Inserting default showcase position values.')
            conn = Session.connection()
            statement = """
            SELECT id from package where type='showcase';
            """
            showcases = conn.execute(statement).fetchall()
            showcases = [i for (i, ) in showcases]
            position = 0
            for showcase_id in showcases:
                statement = """
                INSERT INTO showcase_position (showcase_id,position)
                VALUES (%s,%s);
                """
                data = (showcase_id,position)
                conn.execute(statement,data)
                position = position + 1

            Session.commit()
            log.info('Default showcase position values inserted')

    else:
        log.debug('ShowcasePackageAssociation table creation deferred')

    # setup showcase_admin_table
    if showcase_admin_table is None:
        define_showcase_admin_table()
        log.debug('ShowcaseAdmin table defined in memory')

    if model.user_table.exists():
        if not showcase_admin_table.exists():
            showcase_admin_table.create()
            log.debug('ShowcaseAdmin table create')
        else:
            log.debug('ShowcaseAdmin table already exists')
    else:
        log.debug('ShowcaseAdmin table creation deferred')


class ShowcaseBaseModel(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()


class ShowcasePackageAssociation(ShowcaseBaseModel):

    @classmethod
    def get_package_ids_for_showcase(cls, showcase_id):
        '''
        Return a list of package ids associated with the passed showcase_id.
        '''
        showcase_package_association_list = \
            Session.query(cls.package_id).filter_by(
                showcase_id=showcase_id).all()
        return showcase_package_association_list

    @classmethod
    def get_showcase_ids_for_package(cls, package_id):
        '''
        Return a list of showcase ids associated with the passed package_id.
        '''
        showcase_package_association_list = \
            Session.query(cls.showcase_id).filter_by(
                package_id=package_id).all()
        return showcase_package_association_list

    @classmethod
    def get_showcase_ids_for_organization(cls, organization_id):
        '''
        Return a list of showcase ids associated with the passed organization_id.
        '''
        showcase_organization_association_list = \
            Session.query(cls.showcase_id).filter_by(
                organization_id=organization_id).distinct()
        return showcase_organization_association_list


def define_showcase_package_association_table():
    global showcase_package_assocation_table

    showcase_package_assocation_table = Table(
        'showcase_package_association', metadata,
        Column('package_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('showcase_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('organization_id', types.UnicodeText,
               ForeignKey('group.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=True)
    )

    mapper(ShowcasePackageAssociation, showcase_package_assocation_table)


class ShowcaseAdmin(ShowcaseBaseModel):

    @classmethod
    def get_showcase_admin_ids(cls):
        '''
        Return a list of showcase admin user ids.
        '''
        id_list = [i for (i, ) in Session.query(cls.user_id).all()]
        return id_list

    @classmethod
    def is_user_showcase_admin(cls, user):
        '''
        Determine whether passed user is in the showcase admin list.
        '''
        return (user.id in cls.get_showcase_admin_ids())


def define_showcase_admin_table():
    global showcase_admin_table

    showcase_admin_table = Table('showcase_admin', metadata,
                                 Column('user_id', types.UnicodeText,
                                        ForeignKey('user.id',
                                                   ondelete='CASCADE',
                                                   onupdate='CASCADE'),
                                        primary_key=True, nullable=False))

    mapper(ShowcaseAdmin, showcase_admin_table)


def migrate_v2():
    log.debug('Migrating ShowcasePackageAssociation table to v2.')
    conn = Session.connection()

    statements = """
    ALTER TABLE showcase_package_association
    ADD COLUMN organization_id text;

    UPDATE showcase_package_association spa
    SET organization_id = p.owner_org
    FROM package p
    WHERE spa.package_id = p.id;
    """
    conn.execute(statements)
    Session.commit()
    log.info('ShowcasePackageAssociation table migrated to v2')


class ShowcasePosition(ShowcaseBaseModel):
    @classmethod
    def get_showcase_postions(cls):
        showcase_positions = [i for (i, ) in Session.query(cls.showcase_id).order_by(cls.position).all()]
        return showcase_positions


def define_showcase_position_table():
    global showcase_position_table

    showcase_position_table = Table(
        'showcase_position', metadata,
        Column('showcase_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('position', types.Integer,
               primary_key=False, nullable=False))

    mapper(ShowcasePosition, showcase_position_table)
