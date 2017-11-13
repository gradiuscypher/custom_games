import configparser
import traceback
import json
from lol_customs import riot_tournament_api
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///tournament.db')
Base.metadata.bind = engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

# Setup Config
config = configparser.RawConfigParser()
config.read('config.conf')
provider_id = config.getint("Tournament", 'provider_id')
developer = config.getboolean("Tournament", 'developer')


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

    def start_tournament(self, name, extra=""):
        """
        Starts a new Tournament. Will not start if an active tournament (completed==False) already exists.
        :param name: The tournament name. User-friendly value.
        :param extra: Any extra data about the tournament. Can be empty.
        :return: boolean if creation succeeds or fails
        """
        query = session.query(Tournament).filter(Tournament.completed==False)

        if query.count() == 0:
            new_tournament = Tournament(extra=extra, name=name, completed=False, provider_id=provider_id)
            session.add(new_tournament)

            if developer:
                new_tournament.tournament_id = riot_tournament_api.stub_create_tournament(name, provider_id)
            else:
                new_tournament.tournament_id = riot_tournament_api.create_tournament(name, provider_id)

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
    name = Column(String)
    completed = Column(Boolean)
    provider_id = Column(Integer)
    game_instances = relationship('GameInstance')

    def complete_tournament(self):
        """
        Marks the Tournament as complete and closes all currently active games
        :return:
        """
        for game in self.get_active_games():
            game.finish_game()

        self.completed = True
        session.commit()
        return True

    def create_game(self, creator_discord_id, map_name, team_size=5):
        """
        When a user requests a new game is created. Creates an GameInstance. Will only start if map type isn't
        already starting
        :param creator_discord_id:
        :param map_name:
        :param team_size: The amount of players on each team
        :return:
        """
        # :param map_type: The map type of the game. (Legal values: SUMMONERS_RIFT, TWISTED_TREELINE, HOWLING_ABYSS)
        game_type_list = ["SUMMONERS_RIFT", "HOWLING_ABYSS"]

        query = session.query(GameInstance).filter(GameInstance.start_date==None, GameInstance.finish_date==None,
                                                   GameInstance.map_name==map_name)

        if query.count() == 0 and map_name in game_type_list:
            now = datetime.now()
            new_game = GameInstance(tournament_id=self.id, creator_discord_id=creator_discord_id, map_name=map_name,
                                    create_date=now)
            session.add(new_game)

            if developer:
                new_game_id = riot_tournament_api.stub_create_tournament_code(self.tournament_id, map_type=map_name)
                new_game.tournament_code = new_game_id.json()[0]
            else:
                new_game_id = riot_tournament_api.create_tournament_code(self.tournament_id, map_type=map_name, team_size=team_size)
                new_game.tournament_code = new_game_id.json()[0]

            session.commit()
            return True
        else:
            return False

    def get_open_games(self):
        """
        Return a list of open Games
        :return: list of GameInstance
        """
        game_list = []
        query = session.query(GameInstance).filter(GameInstance.start_date==None)

        for result in query:
            game_list.append(result)

        return game_list

    def get_active_games(self):
        """
        Return a list of active Games
        :return: list of GameInstance
        """
        game_list = []
        query = session.query(GameInstance).filter(GameInstance.finish_date==None, GameInstance.start_date!=None)

        for result in query:
            game_list.append(result)

        return game_list

    def get_complete_games(self):
        """
        Return a list of completed Games
        :return: list of GameInstance
        """
        game_list = []
        query = session.query(GameInstance).filter(GameInstance.finish_date!=None)

        for result in query:
            game_list.append(result)

        return game_list

    def __repr__(self):
        return "<Tournament(id={}, tournament_id={}, extra={}, name={}, completed={}, provider_id={})>" \
            .format(self.id, self.tournament_id, self.extra, self.name, self.completed, self.provider_id)


class GameInstance(Base):
    __tablename__ = "gameinstances"
    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime)
    start_date = Column(DateTime)
    finish_date = Column(DateTime)
    creator_discord_id = Column(String)
    tournament_code = Column(String)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    participants = relationship('Participant')
    map_name = Column(String)
    eog_json = Column(String)

    def __repr__(self):
        return '<GameInstance(id={}, create_date={}, start_date={}, finish_date={}, creator_discord_id={}, ' \
               'tournament_id={}, map_name={}, eog_json={}, tournament_code={}'\
            .format(self.id, self.create_date, self.start_date, self.finish_date, self.creator_discord_id,
                    self.tournament_id, self.map_name, self.eog_json, self.tournament_code)

    def get_players_in_lobby(self):
        player_actions = {}
        player_list = []

        lobby_events = riot_tournament_api.get_lobby_events(self.tournament_code)

        for event in lobby_events['eventList']:
            if event['eventType'] == "PracticeGameCreatedEvent" or event['eventType'] == "PlayerJoinedGameEvent" or event['eventType'] == "PlayerQuitGameEvent":
                if event['summonerId'] not in player_actions.keys():
                    player_actions[event['summonerId']] = [event['timestamp'], event['eventType']]
                else:
                    if player_actions[event['summonerId']][0] < event['timestamp']:
                        player_actions[event['summonerId']] = [event['timestamp'], event['eventType']]

        for key in player_actions.keys():
            if player_actions[key][1] == "PlayerJoinedGameEvent" or player_actions[key][1] == "PracticeGameCreatedEvent":
                player_list.append(riot_tournament_api.get_summoner_name(key))
        return player_list

    def get_lobby_status(self):
        """
        Get the JSON events of the game Lobby
        :return: a dict with the following information :
        {
            game_started: boolean
        }
        """
        if developer:
            lobby_events = riot_tournament_api.stub_get_lobby_events(self.tournament_code)
            for event in lobby_events:
                if event['eventType'] == 'GameAllocationStartedEvent':
                    self.start_game()
        else:
            lobby_events = riot_tournament_api.get_lobby_events(self.tournament_code)
            for event in lobby_events:
                if event['eventType'] == 'GameAllocationStartedEvent':
                    self.start_game()

    def check_game_status(self):
        match_id_list = riot_tournament_api.get_match_id_list(self.tournament_code)

        if len(match_id_list) > 0:
            try:
                # Set the game as finished
                self.finish_game()

                # Update the eog_json
                json_results = riot_tournament_api.get_match(match_id_list[0], self.tournament_code)

                if json_results:
                    self.eog_json = json.dumps(json_results)

                # Update the session
                session.commit()

                return True

            except:
                print("Failed to update the game status")
                print(traceback.format_exc())

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
    gameinstance_id = Column(Integer, ForeignKey('gameinstances.id'))

    def __repr__(self):
        return "<Participant(id={} discord_id={} tournament_id={})>"\
            .format(self.id, self.discord_id, self.tournament_id)
