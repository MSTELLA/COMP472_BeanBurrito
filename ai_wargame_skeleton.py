from __future__ import annotations
import argparse
import copy
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from time import sleep
from typing import Tuple, TypeVar, Type, Iterable, ClassVar
import random
import requests
from MoveHandler import MoveHandler
from OutputHandler import OutputHandler

# maximum and minimum values for our heuristic scores (usually represents an end of game condition)
MAX_HEURISTIC_SCORE = 2000000000
MIN_HEURISTIC_SCORE = -2000000000

class UnitType(Enum):
    """Every unit type."""
    AI = 0
    Tech = 1
    Virus = 2
    Program = 3
    Firewall = 4

class Player(Enum):
    """The 2 players."""
    Attacker = 0
    Defender = 1

    def next(self) -> Player:
        """The next (other) player."""
        if self is Player.Attacker:
            return Player.Defender
        else:
            return Player.Attacker

class GameType(Enum):
    AttackerVsDefender = 0
    AttackerVsComp = 1
    CompVsDefender = 2
    CompVsComp = 3

##############################################################################################################

@dataclass(slots=True)
class Unit:
    player: Player = Player.Attacker
    type: UnitType = UnitType.Program
    health : int = 9
    # class variable: damage table for units (based on the unit type constants in order)
    damage_table : ClassVar[list[list[int]]] = [
        # S depicts the row and then T depicts the column, S attacks T
        # S attacks T, S damages T but T also damages S
        # AI, Tech, Virus, Program, Firewall
        [3,3,3,3,1], # AI
        [1,1,6,1,1], # Tech
        [9,6,1,6,1], # Virus
        [3,3,3,3,1], # Program
        [1,1,1,1,1], # Firewall
    ]
    # class variable: repair table for units (based on the unit type constants in order)
    repair_table : ClassVar[list[list[int]]] = [
        [0,1,1,0,0], # AI
        [3,0,0,3,3], # Tech
        [0,0,0,0,0], # Virus
        [0,0,0,0,0], # Program
        [0,0,0,0,0], # Firewall
    ]

    # class variable: valid move directionality for ATTACKER's units (based on the unit type constants in order)
    valid_move_attacker : ClassVar[list[list[int]]] = [
        # UP DOWN LEFT RIGHT
        [1,0,1,0], # AI UP LEFT
        [1,1,1,1], # Tech UP DOWN LEFT RIGHT
        [1,1,1,1], # Virus UP DOWN LEFT RIGHT
        [1,0,1,0], # Program UP LEFT
        [1,0,1,0], # Firewall UP LEFT
    ]

    # class variable: valid move directionality for DEFENDER's units (based on the unit type constants in order)
    valid_move_defender : ClassVar[list[list[int]]] = [
        # UP DOWN LEFT RIGHT
        [0,1,0,1], # AI DOWN RIGHT
        [1,1,1,1], # Tech UP DOWN LEFT RIGHT
        [1,1,1,1], # Virus UP DOWN LEFT RIGHT
        [0,1,0,1], # Program DOWN RIGHT
        [0,1,0,1], # Firewall DOWN RIGHT
    ]

    def is_alive(self) -> bool:
        """Are we alive ?"""
        return self.health > 0

    def mod_health(self, health_delta : int):
        """Modify this unit's health by delta amount."""
        self.health += health_delta
        if self.health < 0:
            self.health = 0
        elif self.health > 9:
            self.health = 9

    def to_string(self) -> str:
        """Text representation of this unit."""
        p = self.player.name.lower()[0]
        t = self.type.name.upper()[0]
        return f"{p}{t}{self.health}"
    
    def __str__(self) -> str:
        """Text representation of this unit."""
        return self.to_string()
    
    def damage_amount(self, target: Unit) -> int:
        """How much can this unit damage another unit."""
        amount = self.damage_table[self.type.value][target.type.value]
        if target.health - amount < 0:
            return target.health
        return amount

    def repair_amount(self, target: Unit) -> int:
        """How much can this unit repair another unit."""
        amount = self.repair_table[self.type.value][target.type.value]
        if target.health + amount > 9:
            return 9 - target.health
        return amount

    def validate_move_direction(self,coords:CoordPair) -> boolean:
        """Validate specific allowed moves for the player type and unit type (must receive already validated coordinates)"""
        directionality = coords.directionality #sets directionality of CoordPair and returns it
        if directionality==4: # If the source and destination are the same (self-destruct)
            return True
        if self.type.value==1 or self.type.value==2: # 1:Tech and 2: Virus can move in any direction no matter the Player type
            return True
        elif self.player.value == 0: # Attacker = 0
                if self.valid_move_attacker[self.type.value][coords.directionality] ==1:
                    return True
        else: # player is Defender
                if self.valid_move_defender[self.type.value][coords.directionality] ==1:
                    return True
        return False # if all of above fails...

    def is_not_healer(self) -> bool:
        # enum to find row index value
        rowIndex = self.type.value
        row = self.repair_table[rowIndex]  # Replace repair table with appropriate table
        return all(value == 0 for value in row)

    def unit_name(self) ->str:
        return self.type.name


##############################################################################################################

@dataclass(slots=True)
class Coord:
    """Representation of a game cell coordinate (row, col)."""
    row : int = 0
    col : int = 0
    

    def col_string(self) -> str:
        """Text representation of this Coord's column."""
        coord_char = '?'
        if self.col < 16:
                coord_char = "0123456789abcdef"[self.col]
        return str(coord_char)

    def row_string(self) -> str:
        """Text representation of this Coord's row."""
        coord_char = '?'
        if self.row < 26:
                coord_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[self.row]
        return str(coord_char)

    def to_string(self) -> str:
        """Text representation of this Coord."""
        return self.row_string()+self.col_string()
    
    def __str__(self) -> str:
        """Text representation of this Coord."""
        return self.to_string()
    
    def clone(self) -> Coord:
        """Clone a Coord."""
        return copy.copy(self)

    def iter_range(self, dist: int) -> Iterable[Coord]:
        """Iterates over Coords inside a rectangle centered on our Coord."""
        for row in range(self.row-dist,self.row+1+dist):
            for col in range(self.col-dist,self.col+1+dist):
                yield Coord(row,col)

    def iter_adjacent(self) -> Iterable[Coord]:
        """Iterates over adjacent Coords."""
        yield Coord(self.row-1,self.col)
        yield Coord(self.row,self.col-1)
        yield Coord(self.row+1,self.col)
        yield Coord(self.row,self.col+1)

    @classmethod
    def from_string(cls, s : str) -> Coord | None:
        """Create a Coord from a string. ex: D2."""
        s = s.strip()
        for sep in " ,.:;-_":
                s = s.replace(sep, "")
        if (len(s) == 2):
            coord = Coord()
            coord.row = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(s[0:1].upper())
            coord.col = "0123456789abcdef".find(s[1:2].lower())
            return coord
        else:
            return None

##############################################################################################################

@dataclass(slots=True)
class CoordPair:
    """Representation of a game move or a rectangular area via 2 Coords."""
    src : Coord = field(default_factory=Coord)
    dst : Coord = field(default_factory=Coord)
    directionality : int= -1

    def to_string(self) -> str:
        """Text representation of a CoordPair."""
        return self.src.to_string()+" "+self.dst.to_string()
    
    def __str__(self) -> str:
        """Text representation of a CoordPair."""
        return self.to_string()

    def clone(self) -> CoordPair:
        """Clones a CoordPair."""
        return copy.copy(self)

    def iter_rectangle(self) -> Iterable[Coord]:
        """Iterates over cells of a rectangular area."""
        for row in range(self.src.row,self.dst.row+1):
            for col in range(self.src.col,self.dst.col+1):
                yield Coord(row,col)

    def move_directionality(self):
        """ Return the directionality of the movement 0:UP 1:DOWN 2:LEFT 3:RIGHT 4:SAME SPOT"""
        x_diff = self.src.row - self.dst.row
        y_diff = self.src.col - self.dst.col
        if x_diff > 0 and y_diff==0: 
            self.directionality=0 
            # print("STEPS: directionality registered as UP")
        elif x_diff < 0 and y_diff==0: 
            self.directionality=1
            # print("STEPS: directionality registered as DOWN")
        elif y_diff > 0 and x_diff==0: 
            self.directionality=2
            # print("STEPS: directionality registered as LEFT")
        elif y_diff < 0 and x_diff==0: 
            self.directionality=3
            # print("STEPS: directionality registered as RIGHT")
        elif y_diff==0 and x_diff==0: 
            self.directionality=4
            # print("STEPS: directionality registered as in place")
        else:
            # print("STEPS: Not allowed to move in that direction")
            self.directionality=-1
        return self.directionality



    @classmethod
    def from_quad(cls, row0: int, col0: int, row1: int, col1: int) -> CoordPair:
        """Create a CoordPair from 4 integers."""
        return CoordPair(Coord(row0,col0),Coord(row1,col1))
    
    @classmethod
    def from_dim(cls, dim: int) -> CoordPair:
        """Create a CoordPair based on a dim-sized rectangle."""
        return CoordPair(Coord(0,0),Coord(dim-1,dim-1))
    
    @classmethod
    def from_string(cls, s : str) -> CoordPair | None:
        """Create a CoordPair from a string. ex: A3 B2"""
        s = s.strip()
        for sep in " ,.:;-_":
                s = s.replace(sep, "")
        if (len(s) == 4):
            coords = CoordPair()
            coords.src.row = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(s[0:1].upper())
            coords.src.col = "0123456789abcdef".find(s[1:2].lower())
            coords.dst.row = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(s[2:3].upper())
            coords.dst.col = "0123456789abcdef".find(s[3:4].lower())
            return coords
        else:
            return None
    

##############################################################################################################

@dataclass(slots=True)
class Options:
    """Representation of the game options."""
    dim: int = 5
    max_depth : int | None = 4
    min_depth : int | None = 2
    max_time : float | None = 5.0
    game_type : GameType = GameType.AttackerVsDefender
    alpha_beta : bool = True
    max_turns : int | None = 100
    randomize_moves : bool = True
    broker : str | None = None # What is this for?

##############################################################################################################

@dataclass(slots=True)
class Stats:
    """Representation of the global game statistics."""
    evaluations_per_depth : dict[int,int] = field(default_factory=dict)
    total_seconds: float = 0.0

##############################################################################################################

@dataclass(slots=True)
class Game:
    """Representation of the game state."""
    board: list[list[Unit | None]] = field(default_factory=list)
    next_player: Player = Player.Attacker
    turns_played : int = 0
    options: Options = field(default_factory=Options)
    stats: Stats = field(default_factory=Stats)
    _attacker_has_ai : bool = True
    _defender_has_ai : bool = True
    move_handler=MoveHandler()
    output_handler=OutputHandler()

    def __post_init__(self):
        """Automatically called after class init to set up the default board state."""
        dim = self.options.dim
        self.board = [[None for _ in range(dim)] for _ in range(dim)]
        md = dim-1
        self.set(Coord(0,0),Unit(player=Player.Defender,type=UnitType.AI))
        self.set(Coord(1,0),Unit(player=Player.Defender,type=UnitType.Tech))
        self.set(Coord(0,1),Unit(player=Player.Defender,type=UnitType.Tech))
        self.set(Coord(2,0),Unit(player=Player.Defender,type=UnitType.Firewall))
        self.set(Coord(0,2),Unit(player=Player.Defender,type=UnitType.Firewall))
        self.set(Coord(1,1),Unit(player=Player.Defender,type=UnitType.Program))
        self.set(Coord(md,md),Unit(player=Player.Attacker,type=UnitType.AI))
        self.set(Coord(md-1,md),Unit(player=Player.Attacker,type=UnitType.Virus))
        self.set(Coord(md,md-1),Unit(player=Player.Attacker,type=UnitType.Virus))
        self.set(Coord(md-2,md),Unit(player=Player.Attacker,type=UnitType.Program))
        self.set(Coord(md,md-2),Unit(player=Player.Attacker,type=UnitType.Program))
        self.set(Coord(md-1,md-1),Unit(player=Player.Attacker,type=UnitType.Firewall))

    def clone(self) -> Game:
        """Make a new copy of a game for minimax recursion.

        Shallow copy of everything except the board (options and stats are shared).
        """
        new = copy.copy(self)
        new.board = copy.deepcopy(self.board)
        return new

    def is_empty(self, coord : Coord) -> bool:
        """Check if contents of a board cell of the game at Coord is empty (must be valid coord)."""
        return self.board[coord.row][coord.col] is None

    def get(self, coord : Coord) -> Unit | None:
        """Get contents of a board cell of the game at Coord."""
        # if self.is_valid_coord(coord): 
        #     return self.board[coord.row][coord.col]
        # else:
        #     return None
        return self.board[coord.row][coord.col]


    def set(self, coord : Coord, unit : Unit | None):
        """Set contents of a board cell of the game at Coord."""
        # if self.is_valid_coord(coord):
        self.board[coord.row][coord.col] = unit

    def clean_up_board(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                self.remove_dead(Coord(i,j))

    def remove_dead(self, coord: Coord):
        """Remove unit at Coord if dead."""
        unit = self.get(coord)
        if unit is not None and not unit.is_alive():
            self.set(coord,None)
            if unit.type == UnitType.AI:
                if unit.player == Player.Attacker:
                    self._attacker_has_ai = False
                else:
                    self._defender_has_ai = False

    def mod_health(self, coord : Coord, health_delta : int):
        """Modify health of unit at Coord (positive or negative delta)."""
        target = self.get(coord)
        if target is not None:
            target.mod_health(health_delta)
            self.remove_dead(coord)

    def is_adjacent(self, src_coord, dst_coord: Coord) -> bool:
        """Boolean function that returns T/F based on if target code is
        in the adjacent list (using iter_adjacent() method )"""
        return dst_coord in list(src_coord.iter_adjacent())

    def is_valid_move(self, coords : CoordPair)-> bool: # TODO: IF AI MAKES AN INVALID MOVE => OTHER PLAYER WINS
        """Validate a move expressed as a CoordPair."""
        # ALREADY CHECKED DURING INPUT: If either source or Target are not valid coordinates
        #if not self.is_valid_coord(coords.src) or not self.is_valid_coord(coords.dst): 
        # print("The source or destination coordinates are not on the board.")
        # return False

        src_unit = self.get(coords.src) # Get Source unit
        dst_unit = self.get(coords.dst) # Get Destination unit

        if src_unit is None:
            print("The Source coordinates contain no unit.")
            return False
        elif src_unit.player != self.next_player: # Source coordinate is empty or not the player's unit
            print("The Source coordinates contain an unit that belongs to the adversary.")
            return False

        # set Directionality of CoordPair
        coords.directionality=coords.move_directionality()

        # DETERMINE TYPE OF ACTION
        self.move_handler.action_type(src_unit,dst_unit,coords) # sets action type
        action_type= self.move_handler.ACTION.value # 0: Movement 1: Attack 2: Repair 3: Self-Destruct
        # print("STEPS: Action determined to be #",action_type)

        # VALIDATE SELFDESTRUCT
        if action_type==3:
            #coordinates and unit belonging to player already validated
            self.move_handler.validate_selfdestruct(src_unit, coords)
            return True
        
        # VALIDATE ATTACK
        elif action_type==1:
            return self.move_handler.validate_attack(src_unit, dst_unit, coords)

        # VALIDATE MOVEMENT
        elif action_type==0:
            return self.move_handler.validate_movement(src_unit, coords, self.board)

        # VALIDATE REPAIR
        elif action_type==2:
            return self.move_handler.validate_repair(src_unit, dst_unit, coords)
        
        else:
            return False

    def perform_move(self, coords : CoordPair) -> Tuple[bool,str]: #returns (success,result)
        """Validate and perform a move expressed as a CoordPair."""
        if self.is_valid_move(coords): # validates coordinates source and target, sets action type and validates it

            # print("STEPS: Will now perform move")
            action_type= self.move_handler.ACTION.value # 0: Movement 1: Attack 2: Repair 3: Self-Destruct
            
            # PERFORM ATTACK
            if action_type==1:
                # print("Attack STEPS: Will now perform an Attack")
                self.move_handler.attack(self.get(coords.src), self.get(coords.dst), coords)
                # print("Attack STEPS: Will now clean up board")
                self.clean_up_board()
                return(True,self.move_handler.action_consequence)
                
            # PERFORM MOVEMENT
            elif action_type==0:
                self.board=self.move_handler.movement(self.board,self.get(coords.src),coords)
                return(True,self.move_handler.action_consequence)
            
            # PERFORM REPAIR
            elif action_type==2:
                # print("REPAIR STEPS: Will now perform Repair")
                self.board = self.move_handler.repair(self.board, self.get(coords.src),coords.src,coords.dst)
                return(True,self.move_handler.action_consequence)
            
            # PERFORM SELF-DESTRUCT
            elif action_type==3:
                # print("SD STEPS: Will now perform SD")
                self.board=self.move_handler.self_Destruct(self.board,self.get(coords.src),coords.src)
                # print("SD STEPS: Will now clean up board")
                self.clean_up_board()
                return(True,self.move_handler.action_consequence)

        return (False,"invalid move")

    def next_turn(self):
        """Transitions game to the next turn."""
        self.next_player = self.next_player.next()
        self.turns_played += 1

    def to_string(self) -> str:
        """Pretty text representation of the game."""
        dim = self.options.dim
        output = ""
        output += f"Next player: {self.next_player.name}\n"
        output += f"Turns played: {self.turns_played}\n"
        # TODO : ADD AI STATS
        coord = Coord()
        output += "\n   "
        for col in range(dim):
            coord.col = col
            label = coord.col_string()
            output += f"{label:^3} "
        output += "\n"
        for row in range(dim):
            coord.row = row
            label = coord.row_string()
            output += f"{label}: "
            for col in range(dim):
                coord.col = col
                unit = self.get(coord)
                if unit is None:
                    output += " .  "
                else:
                    output += f"{str(unit):^3} "
            output += "\n"
        return output
    
    def board_print(self) -> str:
        """Board Print"""
        dim = self.options.dim
        output = ""
        coord = Coord()
        output += "\n   "
        for col in range(dim):
            coord.col = col
            label = coord.col_string()
            output += f"{label:^3} "
        output += "\n"
        for row in range(dim):
            coord.row = row
            label = coord.row_string()
            output += f"{label}: "
            for col in range(dim):
                coord.col = col
                unit = self.get(coord)
                if unit is None:
                    output += " .  "
                else:
                    output += f"{str(unit):^3} "
            output += "\n"
        return output

    def __str__(self) -> str:
        """Default string representation of a game."""
        return self.to_string()
    
    def is_valid_coord(self, coord: Coord) -> bool:
        """Check if a Coord is valid within out board dimensions."""
        dim = self.options.dim
        if coord.row < 0 or coord.row >= dim or coord.col < 0 or coord.col >= dim:
            return False
        return True

    def read_move(self) -> CoordPair:
        """Read a move from keyboard and return as a CoordPair."""
        while True:
            s = input(F'Player {self.next_player.name}, enter your move: ')
            coords = CoordPair.from_string(s)
            if coords is not None and self.is_valid_coord(coords.src) and self.is_valid_coord(coords.dst): # Check for validate coordinates
                return coords
            else:
                print('Invalid coordinates! Try again.')
    
    def human_turn(self):
        """Human player plays a move (or get via broker)."""
        if self.options.broker is not None:
            print("Getting next move with auto-retry from game broker...")
            while True:
                mv = self.get_move_from_broker()
                if mv is not None:
                    (success,result) = self.perform_move(mv)
                    print(f"Broker {self.next_player.name}: ",end='')
                    print(result)
                    if success:
                        self.next_turn()
                        break
                sleep(0.1)
        else:
            while True:
                mv = self.read_move()
                (success,result) = self.perform_move(mv)
                if success:
                    print(f"Player {self.next_player.name}: ",end='')
                    print(result)
                    self.next_turn()
                    break
                else:
                    print("The move is not valid! Try again.")

    def computer_turn(self) -> CoordPair | None: # TODO TO INSPECT
        """Computer plays a move."""
        mv = self.suggest_move()
        if mv is not None:
            (success,result) = self.perform_move(mv) # validates and performs
            if success:
                print(f"Computer {self.next_player.name}: ",end='')
                print(result)
                self.next_turn()
        return mv

    def player_units(self, player: Player) -> Iterable[Tuple[Coord,Unit]]:
        """Iterates over all units belonging to a player."""
        for coord in CoordPair.from_dim(self.options.dim).iter_rectangle():
            unit = self.get(coord)
            if unit is not None and unit.player == player:
                yield (coord,unit)

    def is_finished(self) -> bool:
        """Check if the game is over."""
        return self.has_winner() is not None

    def has_winner(self) -> Player | None:
        """Check if the game is over and returns winner"""
        if self.options.max_turns is not None and self.turns_played >= self.options.max_turns:
            print(f"Game has reached the max number of turns with no winner. \n")
            return Player.Defender
        elif self._attacker_has_ai:
            if self._defender_has_ai:
                return None
            else:
                return Player.Attacker    
        elif self._defender_has_ai:
            return Player.Defender

    def move_candidates(self) -> Iterable[CoordPair]: # GENERATES MOVE CANDIDATES OF ONE LEVEL! 
        """Generate valid move candidates for the next player."""
        move = CoordPair()
        for (src,_) in self.player_units(self.next_player):
            move.src = src
            for dst in src.iter_adjacent():
                move.dst = dst
                if self.is_valid_move(move):
                    yield move.clone()
            move.dst = src
            yield move.clone()

    def random_move(self) -> Tuple[int, CoordPair | None, float]:
        """Returns a random move."""
        move_candidates = list(self.move_candidates()) # The list size will help with branching factor?
        random.shuffle(move_candidates)
        if len(move_candidates) > 0:
            return (0, move_candidates[0], 1)
        else:
            return (0, None, 0)

    def suggest_move(self) -> CoordPair | None: 
        """Suggest the next move using minimax alpha beta. TODO: REPLACE RANDOM_MOVE WITH PROPER GAME LOGIC!!!"""
        start_time = datetime.now() # Start time
        (score, move, avg_depth) = self.random_move() # TODO CHANGE
        elapsed_seconds = (datetime.now() - start_time).total_seconds() # End time

        # Below is generating statistics and printing them
        self.stats.total_seconds += elapsed_seconds
        print(f"Heuristic score: {score}")
        print(f"Average recursive depth: {avg_depth:0.1f}")
        print(f"Evals per depth: ",end='')
        for k in sorted(self.stats.evaluations_per_depth.keys()):
            print(f"{k}:{self.stats.evaluations_per_depth[k]} ",end='')
        print()
        total_evals = sum(self.stats.evaluations_per_depth.values())
        if self.stats.total_seconds > 0:
            print(f"Eval perf.: {total_evals/self.stats.total_seconds/1000:0.1f}k/s")
        print(f"Elapsed time: {elapsed_seconds:0.1f}s")
        return move

    def post_move_to_broker(self, move: CoordPair):
        """Send a move to the game broker."""
        if self.options.broker is None:
            return
        data = {
            "from": {"row": move.src.row, "col": move.src.col},
            "to": {"row": move.dst.row, "col": move.dst.col},
            "turn": self.turns_played
        }
        try:
            r = requests.post(self.options.broker, json=data)
            if r.status_code == 200 and r.json()['success'] and r.json()['data'] == data:
                # print(f"Sent move to broker: {move}")
                pass
            else:
                print(f"Broker error: status code: {r.status_code}, response: {r.json()}")
        except Exception as error:
            print(f"Broker error: {error}")

    def get_move_from_broker(self) -> CoordPair | None: # TODO
        """Get a move from the game broker."""
        if self.options.broker is None:
            return None
        headers = {'Accept': 'application/json'}
        try:
            r = requests.get(self.options.broker, headers=headers)
            if r.status_code == 200 and r.json()['success']:
                data = r.json()['data']
                if data is not None:
                    if data['turn'] == self.turns_played+1:
                        move = CoordPair(
                            Coord(data['from']['row'],data['from']['col']),
                            Coord(data['to']['row'],data['to']['col'])
                        )
                        print(f"Got move from broker: {move}")
                        return move
                    else:
                        # print("Got broker data for wrong turn.")
                        # print(f"Wanted {self.turns_played+1}, got {data['turn']}")
                        pass
                else:
                    # print("Got no data from broker")
                    pass
            else:
                print(f"Broker error: status code: {r.status_code}, response: {r.json()}")
        except Exception as error:
            print(f"Broker error: {error}")
        return None
     
    def player_ai_health(self, player: Player) -> int:
        """Returns health of players AI unit."""
        for coord in CoordPair.from_dim(self.options.dim).iter_rectangle():
            unit = self.get(coord)
            if unit is not None and unit.player == player and unit.type == UnitType.AI:
                return unit.health
    
    '''
    def move_damage_potential(self, coords : CoordPair) -> int:
        if self.is_valid_move(coords):
            action_type = self.move_handler.ACTION.value
            if (action_type == 1 or  action_type == 3):
                # only attack and self_destruct results in damage

            else: return 0
    '''

##############################################################################################################

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog='ai_wargame',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--max_depth', type=int, help='maximum search depth')
    parser.add_argument('--max_time', type=float, help='maximum search time')
    parser.add_argument('--game_type', type=str, default="manual", help='game type: auto|attacker|defender|manual')
    parser.add_argument('--broker', type=str, help='play via a game broker')
    args = parser.parse_args()

    # parse the game type
    if args.game_type == "attacker":
        game_type = GameType.AttackerVsComp
    elif args.game_type == "defender":
        game_type = GameType.CompVsDefender
    elif args.game_type == "manual":
        game_type = GameType.AttackerVsDefender
    else:
        game_type = GameType.CompVsComp

    # set up game options
    options = Options(game_type=game_type)

    # override class defaults via command line options
    if args.max_depth is not None:
        options.max_depth = args.max_depth
    if args.max_time is not None:
        options.max_time = args.max_time
    if args.broker is not None:
        options.broker = args.broker

    # ask user for game parameters
    print("Please input your game parameters.\n")
    options.max_turns = int(input("Enter the maximum number of turns: "))
    options.max_time = int(input("Enter the value of the timeout in seconds: "))

    play_mode = input("Enter the play mode attacker-defender (auto|attacker|defender|manual): ")
    if play_mode == "attacker":
        options.game_type = GameType.AttackerVsComp
    elif play_mode == "defender":
        options.game_type = GameType.CompVsDefender
    elif play_mode == "manual":
        options.game_type = GameType.AttackerVsDefender
    else:
        options.game_type = GameType.CompVsComp

    if (game_type != GameType.AttackerVsDefender):
        alpha_beta = input("Enter whether alpha-beta is on or off (on|off): ")
        if alpha_beta == 'on': options.alpha_beta = True
        else: options.alpha_beta = False

    # heuristic = input("Enter the name of your heuristic (e0|e1|e2): ")

    # create a new game
    game = Game(options=options)

    #  OutputHandler creates the game file and writes the game parameters
    game.output_handler.setupfile(game.options)

    # print title
    title = [
    "",
    " .-. .-.  .--.  .---.  .----.  .--.   .-. .-..---.",
    "| {  } | / {} \\ | {} } |  __/ / {} \\ {  \\/  }| --}",
    "{  /\\  }/  /\\  \\| |\\ \\ | '- }/  /\\  \\| }  { || --}",
    "`-'  `-'`-'  `-'`-' `-'`----'`-'  `-'`-'  `-'`---'",
    "",
    "Marie-Josée Castellanos, Gabrielle Guidote, Amrit Sohpal",
    ""
    ]

    for line in title:
        print(line)

    # the main game loop
    while True:
        print(game)
        winner = game.has_winner()
        if winner is not None:
            print(f"{winner.name} wins!")
            # game.output_handler.write_turn(game)
            game.output_handler.write_end_game(winner.name,game.turns_played) 
            break

        if game.options.game_type == GameType.AttackerVsDefender: # manual
            game.human_turn()
            game.output_handler.write_turn(game)
        elif game.options.game_type == GameType.AttackerVsComp and game.next_player == Player.Attacker: # Human Attacker Vs AI Defender
            game.human_turn()
            game.output_handler.write_turn(game)
        elif game.options.game_type == GameType.CompVsDefender and game.next_player == Player.Defender: # AI Attacker vs Human Defender
            game.human_turn()
            game.output_handler.write_turn(game)
        else:     # AI Attacker and AI Defender or simply AI turn
            player = game.next_player 
            move = game.computer_turn()
            if move is not None:
                game.post_move_to_broker(move) # Sends suggested move from computer_turn() to 
            else:
                print("Computer doesn't know what to do!!!")
                exit(1)

##############################################################################################################

if __name__ == '__main__':
    main()
