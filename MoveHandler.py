
class MoveHandler:

    type=""
    action_consequence=""
    valid_direction=False
    valid_engaged_in_combat=False
    # AI = 0
    # Tech = 1
    # Virus = 2
    # Program = 3
    # Firewall = 4

    def valid_direction(src_unit:Unit, coords: CoordPair):
        self.valid_direction = src_unit.validate_move_direction(coords) 
        return self.valid_direction

    # def valid_engaged_in_combat(src_unit:Unit, src:Coord, board):
        # TODO must iterate around and see if there are any adverserial units around => should be in game class or unit class?
        # if src_unit.type==0 or src_unit.type==3 or src_unit.type==4:
            
            
        # else:
        #     self.valid_engaged_in_combat=True
        # return self.valid_engaged_in_combat

    # def action_type():
        # after all validations
        # if target coordinate empty => movement
        # if target enemy => attack
        # if target ally => repair (have to validate also)
        # if target same (directionality is 4) => self-destruct 

    # def movement():
    

    # def attack():
    
    # def repair():

    # def self_Destruct():

    def clear_move(self):
        self.type=""
        self.directionality=""
        self.action_consequence=""
