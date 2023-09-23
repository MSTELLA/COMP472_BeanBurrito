from enum import Enum

class ACTION(Enum):
    """Every Action type."""
    Movement = 0
    Attack = 1
    Repair = 2
    SelfDestruct = 3

class MoveHandler:
    ACTION: ACTION.Movement
    action_consequence=""

    # AI = 0
    # Tech = 1
    # Virus = 2
    # Program = 3
    # Firewall = 4

    def action_type(self,src_unit, dst_unit, coords):
        # after validations: Coords are on the board, unit belongs to player, src is not empty
        # if target and source are the same (directionality is 4) => self-destruct 
        if coords.directionality==4:
            self.ACTION = ACTION.SelfDestruct
        # if target coordinate empty => movement
        elif dst_unit is None:
            self.ACTION = ACTION.Movement
        # if target enemy => attack
        elif src_unit.player != dst_unit.player:
            self.ACTION = ACTION.Attack
        # if target ally => repair (have to validate also)
        elif src_unit.player == dst_unit.player:
            self.ACTION = ACTION.Repair
        
    def clear_move(self):
        self.ACTION = ACTION.Movement
        self.action_consequence=""

#---------------------------------- MOVEMENT ---------------------------------- #
    def validate_movement(self,src_unit, coords, board) -> bool:
        """ Validated that this unit can perform this movement and isn't restrained by being engaged in combat"""
        # Validation that this type of unit for this player type can move in this direction
        valid_direction = self.valid_direction(src_unit,coords)
        # print("MOVEMENT STEPS: Direction Valid:", valid_direction)
        # Validation that this unit is not engaged in combat(Only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat)
        valid_engaged_in_combat=self.valid_engaged_in_combat(src_unit, coords.src, board)
        # print("MOVEMENT STEPS: Engaged in combat Valid (meaning ok to move):", valid_engaged_in_combat)
        self.movement_string(src_unit, coords)
        return (valid_direction and valid_engaged_in_combat)

    def valid_direction(self,src_unit, coords)-> bool:
        # print("MOVEMENT STEPS: Validating direction")
        valid_direction=src_unit.validate_move_direction(coords)
        if not valid_direction:
            self.action_consequence="Unit cannot move in that direction."
        return valid_direction
        
    def valid_engaged_in_combat(self,src_unit, src_coord, board)-> bool:
        """ Iterate around source coordinates and see if there are any adverserial units around """
        # print("MOVEMENT STEPS: Validating engaged in combat")
        valid_engaged_in_combat=True
        dim = len(board)
        #(Only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat)
        if src_unit.type.value==0 or src_unit.type.value==3 or src_unit.type.value==4:
            for coord in src_coord.iter_adjacent():
                if not (coord.row < 0 or coord.row >= dim or coord.col < 0 or coord.col >= dim):
                    coord_content=board[coord.row][coord.col]
                    if coord_content is not None:
                            if coord_content.player.value != src_unit.player.value:
                                valid_engaged_in_combat=False # there is an adversarial unit in the adjacent coordinates
                                self.action_consequence="Unit cannot move: Adversarial unit adjacent!"
        return valid_engaged_in_combat

    def movement_string(self, src_unit, coords):
        self.action_consequence="Movement Action Performed. " + src_unit.type.name + " Unit at " + coords.src.to_string() + " is now at " + coords.dst.to_string()
    
    def movement(self,board,src_unit, coords):
        board[coords.dst.row][coords.dst.col]=src_unit
        board[coords.src.row][coords.src.col]=None
        return board

#---------------------------------- ATTACK ---------------------------------- #

    # def attack():

#---------------------------------- REPAIR ---------------------------------- #

    # def repair():

#---------------------------------- SELF-DESTRUCT ---------------------------------- #

    # def self_Destruct():
