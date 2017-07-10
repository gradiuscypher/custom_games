import requests
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


class MemberGroup(Base):
    __tablename__ = "membergroups"
    id = Column(Integer, primary_key=True)
    group_name = Column(String)
    gdmembers = relationship('GdMember', secondary=association_table, back_populates='membergroups')

    def create_group(self, group_name):
        try:
            new_group = MemberGroup(group_name=group_name)
            session.add(new_group)
            session.commit()
            return True
        except:
            print(traceback.format_exc())
            return False

    def add_member_to_group(self, member):
        self.gdmembers.append(member)
        session.commit()


class GdMember(Base):
    __tablename__ = "gdmembers"
    id = Column(Integer, primary_key=True)
    discord_name = Column(String)
    discord_id = Column(String)
    summoner_name = Column(String)
    validation_string = Column(String)
    membergroups = relationship('MemberGroup', secondary=association_table, back_populates='gdmembers')

    def create_member(self, summoner_name, discord_name="", discord_id="", validation_string=""):
        try:
            new_member = GdMember(summoner_name=summoner_name, discord_name=discord_name, discord_id=discord_id,
                                  validation_string=validation_string)
            session.add(new_member)
            session.commit()
            return True
        except:
            print(traceback.format_exc())
            return False


def check_for_validation(validation_url, validation_string):
    pass
