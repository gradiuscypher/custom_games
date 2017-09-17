from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///tournament.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class TournamentManager:
    def build_db(self):
        Base.metadata.create_all(engine)

    def get_active_tournaments(self):
        """
        Return a list of active Tournaments
        :return: list of Tournament
        """
        tournament_list = []
        query = session.query(Tournament).filter(Tournament.completed==False)

        for result in query:
            tournament_list.append(result)

        return tournament_list

    def start_tournament(self, name, provider_id, tournament_id, map, extra=""):
        """
        Starts a new Tournament. Will not start if an active tournament (completed==False) already exists.
        :param name: The tournament name. User-friendly value.
        :param provider_id: The Tournament API Provider ID
        :param tournament_id: The Tournament API Tournament ID
        :param extra: Any extra data about the tournament. Can be empty.
        :return: boolean if creation succeeds or fails
        """
        query = session.query(Tournament).filter(Tournament.completed==False, Tournament.map==map)

        if query.count() == 0:
            new_tournament = Tournament(tournament_id=tournament_id, extra=extra, name=name, completed=False,
                                        provider_id=provider_id, map=map)
            session.add(new_tournament)
            session.commit()
            return True
        else:
            print("There is already an active tournament.")
            return False


class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True)
    tournament_id = Column(String)
    extra = Column(String)
    map = Column(String)
    name = Column(String)
    completed = Column(Boolean)
    provider_id = Column(Integer)
    participants = relationship('Participant')
    game_instances = relationship('GameInstance')

    def complete_tournament(self):
        """
        Marks the Tournament as complete.
        :return:
        """
        self.completed = True
        session.commit()

    def clean_stale_games(self):
        """
        Cleans up games that are starting but don't have enough players. Compares create_date vs a timeout period.
        :return:
        """
        pass

    def create_game(self, creator_discord_id, map_name):
        """
        When a user requests a new game is created. Creates an GameInstance. Will only start if map type isn't
        already starting
        :param creator_discord_id:
        :param map_name:
        :return:
        """
        query = session.query(GameInstance).filter(GameInstance.finish_date==None, GameInstance.map_name==map_name)

        if query.count() == 0:
            now = datetime.now()
            new_game = GameInstance(tournament_id=self.id, creator_discord_id=creator_discord_id, map_name=map_name,
                                    create_date=now)
            session.add(new_game)
            session.commit()
            return True
        else:
            return False

    def get_active_games(self):
        """
        Return a list of active Games
        :return: list of GameInstance
        """
        game_list = []
        query = session.query(GameInstance).filter(GameInstance.finish_date==None)

        for result in query:
            game_list.append(result)

        return game_list

    def join_game(self):
        pass

    def join_season(self, discord_id):
        new_participant = Participant(discord_id=discord_id, tournament_id=self.id)
        session.add(new_participant)
        session.commit()

    def __repr__(self):
        return "<Tournament(id={}, tournament_id={}, extra={}, name={}, completed={}, map={}, provider_id={})>"\
            .format(self.id, self.tournament_id, self.extra, self.name, self.completed, self.map, self.provider_id)


class GameInstance(Base):
    __tablename__ = "gameinstances"
    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime)
    start_date = Column(DateTime)
    finish_date = Column(DateTime)
    creator_discord_id = Column(String)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    map_name = Column(String)
    eog_json = Column(String)

    def __repr__(self):
        return f'<GameInstance(id={self.id}, create_date={self.create_date}, start_date={self.start_date}, ' \
               f'finish_date={self.finish_date}, creator_discord_id={self.creator_discord_id}, ' \
               f'tournament_id={self.tournament_id}, map_name={self.map_name}, eog_json={self.eog_json}'

    def finish_game(self):
        """
        Sets a game into finished mode
        :return:
        """
        self.finish_date = datetime.now()
        session.commit()
        return True

    def start_game(self):
        """
        Sets a game into start mode
        :return:
        """
        self.start_date = datetime.now()
        session.commit()
        return True


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    discord_id = Column(String)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))

    def __repr__(self):
        return "<Participant(id={} discord_id={} tournament_id={})>"\
            .format(self.id, self.discord_id, self.tournament_id)
