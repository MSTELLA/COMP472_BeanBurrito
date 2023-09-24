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
    coords = None

    # AI = 0
    # Tech = 1
    # Virus = 2
    # Program = 3
    # Firewall = 4

    def action_type(self, src_unit, dst_unit, coords):
        # after validations: Coords are on the board, unit belongs to player, src is not empty
        # if target and source are the same (directionality is 4) => self-destruct 
        self.coords=coords
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
    def validate_movement(self, src_unit, coords, board) -> bool:
        """ Validates that this unit can perform this movement and isn't restrained by being engaged in combat"""
        # Validation that this type of unit for this player type can move in this direction
        valid_direction = self.valid_direction(src_unit,coords)
        # Validation that this unit is not engaged in combat
        # Only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat
        valid_engaged_in_combat=self.valid_engaged_in_combat(src_unit, coords.src, board)
        self.movement_string(src_unit, coords)
        return (valid_direction and valid_engaged_in_combat)

    def valid_direction(self, src_unit, coords)-> bool:
        valid_direction=src_unit.validate_move_direction(coords)
        if not valid_direction:
            self.action_consequence="Unit cannot move in that direction."
        return valid_direction
        
    def valid_engaged_in_combat(self, src_unit, src_coord, board)-> bool:
        """ Iterate around source coordinates and see if there are any adverserial units around """
        valid_engaged_in_combat=True
        dim = len(board)
        #(Only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat)
        if src_unit.type.value==0 or src_unit.type.value==3 or src_unit.type.value==4:
            for coord in src_coord.iter_adjacent():
                if not (coord.row < 0 or coord.row >= dim or coord.col < 0 or coord.col >= dim):
                    coord_content=board[coord.row][coord.col]
                    if coord_content is not None:
                            if coord_content.player.value != src_unit.player.value:
                                valid_engaged_in_combat=False # TRUE = there is an adversarial unit in the adjacent coordinates
                                self.action_consequence="Unit cannot move: Adversarial unit adjacent!"
        return valid_engaged_in_combat

    def movement_string(self, src_unit, coords):
        self.action_consequence="Movement Action Performed. " + src_unit.type.name + " Unit at " + coords.src.to_string() + " is now at " + coords.dst.to_string()

    def movement(self, board, src_unit, coords):
        board[coords.dst.row][coords.dst.col]=src_unit
        board[coords.src.row][coords.src.col]=None
        return board

#---------------------------------- ATTACK ---------------------------------- #

    def attack_string(self, src_unit, dst_unit, coords):
        damage = ""
        # if the destination unit destroyed
        if (dst_unit.damage_amount(src_unit) == 0):
            damage = damage + src_unit.type.name + " Unit destroyed !"
        else:
            damage = damage + src_unit.type.name + " Unit took " + str(dst_unit.damage_amount(src_unit)) + " damage. \n"
        # if the source unit destroyed
        if (src_unit.damage_amount(dst_unit) == 0):
            damage = damage + dst_unit.type.name + " Unit destroyed !"
        else:
            damage = damage + dst_unit.type.name + " Unit took " + str(src_unit.damage_amount(dst_unit)) + " damage. \n"

        action = src_unit.type.name + " Unit at " + coords.src.to_string() + " has attacked " + dst_unit.type.name + " Unit at " + coords.dst.to_string() + ". \n"
        self.action_consequence= "Attack Action Performed. " + action + damage

    def validate_attack(self, src_unit, dst_unit, coords)-> bool:
        self.ACTION=ACTION(1)
        src_unit.validate_move_direction(coords)
        # first check that the src_unit and dst_unit are adjacent
        # units are on adjacent teams
        valid_attack = False
        for adjacent_coord in coords.src.iter_adjacent():
            if (adjacent_coord == coords.dst): 
                valid_attack = True 
        
        self.action_consequence = "Unit cannot attack: Targeted unit not adjacent!"
        return valid_attack 

    def attack(self, src_unit, dst_unit, coords):
        # combat is bi-directional,  if S attacks T, S damages T but T also damages S
        # meaning that if S attacks T, S does an attack damage to T, but T also does its attack damage to S
        dst_dmg = src_unit.damage_amount(dst_unit)
        src_dmg = dst_unit.damage_amount(src_unit)

        if ((dst_unit.health - dst_dmg) > 0): # damage below 0 they are killed, damage_amount return target health when they are killed
            dst_unit.health = dst_unit.health - dst_dmg
        else: dst_unit.health = 0 # unit died
                
        if ((src_unit.health - src_dmg) > 0): # damage below 0 they are killed, damage_amount return target health when they are killed
            src_unit.health = src_unit.health - src_dmg
        else: src_unit.health = 0 # unit died
                
        self.attack_string(src_unit, dst_unit, coords)

#---------------------------------- REPAIR ---------------------------------- #

    # def repair():

#---------------------------------- SELF-DESTRUCT ---------------------------------- #

    def validate_selfdestruct(self, src_unit, coords):
        """ Sets Action type in MoveHandler"""
        self.ACTION=ACTION(3)
        src_unit.validate_move_direction(coords)

    def self_Destruct(self, board, src_unit, src_coord):
        dim=len(board)
        damaged_units=[]
        destroyed_units=[]
        for coord in src_coord.iter_range(1):
            if not (coord.row < 0 or coord.row >= dim or coord.col < 0 or coord.col >= dim):
                coord_content=board[coord.row][coord.col]
                if coord_content is not None:
                    print("SD STEPS: Damaging nearby unit " , coord_content.type.name, " health: ", coord_content.health)
                    coord_content.mod_health(-2)
                    print("SD STEPS: Damaged nearby unit " , coord_content.type.name, " health: ", coord_content.health)
                    if coord_content.health >0 : damaged_units.append(coord_content)
                    else: destroyed_units.append(coord_content)
        self.selfdestruct_string(src_unit,src_coord,damaged_units,destroyed_units)
        board[src_coord.row][src_coord.col].health=0 # src unit now has 0 health
        return board

    def selfdestruct_string(self, src_unit, src_coord, damaged_units, destroyed_units):
        self.action_consequence="Self-Destruct Action Performed. " + src_unit.type.name + " Unit at " + src_coord.to_string() + " and has damaged "+ str(len(damaged_units))+" nearby units and destroyed " +str(len(destroyed_units))+ " nearby units."
    #TODO: FORMAT THIS STRING