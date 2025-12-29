"""
Core game entities: World, Fleet, Player, Artifact.
"""


class Artifact:
    def __init__(self, artifact_id, name):
        self.id = artifact_id
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class World:
    def __init__(self, world_id):
        self.id = world_id
        self.connections = []
        self.owner = None
        self.industry = 0
        self.metal = 0
        self.mines = 0
        self.population = 0
        self.limit = 0
        self.iships = 0
        self.pships = 0
        self.fleets = []
        self.artifacts = []
        self.key = False  # True if this is a player's homeworld
        self.population_type = "human"  # "human", "robot", "apostle"
        self.plundered = False  # True if world has been plundered this turn
        self.planet_buster = False  # True if planet buster bomb has been dropped

    def to_dict(self, viewer=None, turn_last_seen=None):
        data = {
            "id": self.id,
            "connections": self.connections,
            "turn_last_seen": turn_last_seen
        }

        data["owner"] = self.owner.name if self.owner else None

        is_visible_now = False
        if viewer:
            if self.owner == viewer:
                is_visible_now = True
            else:
                for f in self.fleets:
                    if f.owner == viewer:
                        is_visible_now = True
                        break

        if is_visible_now:
            data.update({
                "industry": self.industry,
                "metal": self.metal,
                "mines": self.mines,
                "population": self.population,
                "limit": self.limit,
                "iships": self.iships,
                "pships": self.pships,
                "key": self.key,  # Homeworld marker
                "population_type": self.population_type,  # "human", "robot", "apostle"
                "plundered": self.plundered,  # Plundered status
                "planet_buster": self.planet_buster,  # Planet buster bomb status
                "fleets": [f.id for f in self.fleets],
                "artifacts": [a.to_dict() for a in self.artifacts]
            })
        else:
            data.update({
                "industry": "?", "metal": "?", "mines": "?",
                "population": "?", "limit": "?", "iships": "?", "pships": "?",
                "fleets": [],
                "artifacts": []
            })

        return data


class Fleet:
    def __init__(self, fleet_id, owner, world):
        self.id = fleet_id
        self.owner = owner
        self.world = world
        self.ships = 0
        self.cargo = 0
        self.moved = False
        self.is_ambushing = False
        self.has_pbb = False  # Planet Buster Bomb
        self.artifacts = []
        world.fleets.append(self)

    def to_dict(self, viewer=None):
        data = {
            "id": self.id,
            "owner": self.owner.name if self.owner else "[Neutral]",
            "world": self.world.id,
            "moved": self.moved,
            "is_ambushing": self.is_ambushing,
            "artifacts": [a.to_dict() for a in self.artifacts]
        }

        if viewer == self.owner:
            data["ships"] = self.ships
            data["cargo"] = self.cargo
            data["has_pbb"] = self.has_pbb
        else:
            data["ships"] = self.ships
            data["cargo"] = "?"

        return data


class Player:
    def __init__(self, player_id, name, websocket):
        self.id = player_id
        self.name = name
        self.websocket = websocket
        self.score = 0
        self.character_type = "Empire Builder"
        self.fleets = []
        self.worlds = []
        self.known_worlds = {}
        self.orders = []
        self.last_state_snapshot = None
        self.turn_timer_minutes = 60  # Player's preferred minimum turn time in minutes (default 60)
