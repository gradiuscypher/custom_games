import requests
import random
import string
import traceback
from sqlalchemy import Column, Boolean, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///gdmembers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

association_table = Table('association', Base.metadata,
    Column('membergroups', Integer, ForeignKey('membergroups.id')),
    Column('gdmembers', Integer, ForeignKey('gdmembers.id'))
)


class MembersManager:
    def build_db(self):
        Base.metadata.create_all(engine)

    def create_group(self, group_name):
        try:
            new_group = MemberGroup(group_name=group_name)
            session.add(new_group)
            session.commit()
            return True
        except:
            print(traceback.format_exc())
            return False

    def create_member(self, summoner_name=None, discord_name=None, discord_id=None):
        try:
            validation_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            new_member = GdMember(summoner_name=summoner_name, discord_name=discord_name, discord_id=discord_id,
                                  validation_string=validation_string, validated=False)
            session.add(new_member)
            session.commit()
            return new_member
        except:
            print(traceback.format_exc())
            return None

    def list_all_groups(self):
        return [x for x in session.query(MemberGroup).all()]

    def list_all_members(self):
        return [x for x in session.query(GdMember).all()]


class MemberGroup(Base):
    __tablename__ = "membergroups"
    id = Column(Integer, primary_key=True)
    group_name = Column(String)
    members = relationship('GdMember', secondary=association_table, back_populates='groups')

    def add_member(self, member):
        self.members.append(member)
        session.commit()

    def __repr__(self):
        return "<MemberGroup(group_name={})>".format(self.group_name)


class GdMember(Base):
    __tablename__ = "gdmembers"
    id = Column(Integer, primary_key=True)
    discord_name = Column(String)
    discord_id = Column(String)
    summoner_name = Column(String)
    validation_string = Column(String)
    validated = Column(Boolean)
    groups = relationship('MemberGroup', secondary=association_table, back_populates='members')

    def __repr__(self):
        return "<GdMember(summoner_name={}, discord_name={})>".format(self.summoner_name, self.discord_name)


def start_validation(discord_id, discord_name):
    """
    Start the validation process for a new discord ID. If ID already exists, do not create
    :param discord_id:
    :param discord_name:
    :return: return validation tuple, first is a boolean indicating if validation was started, second is validation string
    """
    manager = MembersManager()
    # query = session.query(Tournament).filter(Tournament.completed==False)
    query = session.query(GdMember).filter(GdMember.discord_id==discord_id)

    if query.count() == 0:
        # If Discord ID hasn't been seen, do this
        member = manager.create_member(discord_name=discord_name, discord_id=discord_id)
        return True, member.validation_string
    else:
        # If Discord ID already is tied to a member, do this
        member = query.one()
        return False, member.validation_string


def check_for_validation(validation_url, validation_string):
    """
    Check the Boards forum post for validation string
    :param validation_url:
    :param validation_string:
    :return:
    """
    pass
