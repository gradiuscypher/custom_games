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

    def create_member(self, summoner_name=None, discord_name=None, discord_id=None, realm=None):
        try:
            validation_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            new_member = GdMember(summoner_name=summoner_name, discord_name=discord_name, discord_id=discord_id,
                                  validation_string=validation_string, validated=False, realm=realm)
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
    realm = Column(String)
    validation_string = Column(String)
    validated = Column(Boolean)
    groups = relationship('MemberGroup', secondary=association_table, back_populates='members')

    def __repr__(self):
        return "<GdMember(summoner_name={}, realm={}, discord_name={})>".format(
            self.summoner_name, self.realm, self.discord_name
        )


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


def check_for_validation(url_location, url_discussion, forum_location="na"):
    """
    Check the Boards forum post for validation string and validate those users
    :param url_location:
    :param url_discussion:
    :param forum_location:
    :return:
    """
    api_url = "https://boards.{}.leagueoflegends.com/api/{}/discussions/{}/comments?num_loaded={}"
    loaded_count = 0
    remaining = 1
    post_data = []

    try:
        # Pull all data from validation posts and format into useful object
        while remaining > 0:
            result = requests.get(api_url.format(forum_location, url_location, url_discussion, loaded_count)).json()
            remaining = result['moreCount']
            loaded_count += 20

            for comment in result['comments']:
                if len(comment['message']) <= 16:
                    post_data.append([comment['user'], comment['message']])
    except:
        print(traceback.format_exc())

    # Find all users that aren't validated
    unvalidated = [x for x in session.query(GdMember).filter(GdMember.validated==False).all()]

    # For every message found that matches length, see if it matches any unvalidated user's message
    for message in post_data:
        for user in unvalidated:
            # TODO: Remove this print, it's spammy
            print("Checking ", user.discord_name, " to post value ", user.validation_string)
            if message[1] == user.validation_string:
                user.summoner_name = message[0]['name']
                user.realm = message[0]['realm']
                user.validated = True
                session.commit()
                print(user.summoner_name + " has been validated")
                break


def generate_discord_nickname(discord_id):
    """
    Returns a nickname generated by combining summoner name and region.
    :param discord_id:
    :return: String
    """
    try:
        member_query = session.query(GdMember).filter(GdMember.discord_id==discord_id)

        if member_query.count() > 0:
            member = session.query(GdMember).filter(GdMember.discord_id==discord_id).one()
            return member.summoner_name + " (" + member.realm + ")"
        else:
            return None
    except:
        print(traceback.format_exc())


def is_user_validated(discord_id):
    """
    Returns a boolean of if the discord_id has been validated via the forums
    :param discord_id:
    :return: boolean
    """
    try:
        member_query = session.query(GdMember).filter(GdMember.discord_id==discord_id)

        if member_query.count() > 0:
            member = session.query(GdMember).filter(GdMember.discord_id==discord_id).one()
            return member.validated
        else:
            return False
    except:
        print(traceback.format_exc())
