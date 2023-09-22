
class MoveHandler:

    type=""
    directionality=""
    action_consequence=""


    def validate_move_unit(playerType, unit, CoordPair) -> boolean:
        """ Verifies that the unit at source coordinated is allowed to do the move"""

        # Will use new method for unit to check validity of direcitonality
            # this method will use Coordpair new method to figure if its left right up down
            # ALSO CHECK ENGAGED IN COMBAT OR NOT ( Only AI, Firewall and program)
        return True

    # AI = 0
    # Tech = 1
    # Virus = 2
    # Program = 3
    # Firewall = 4

    # def engaged_in_combat():
        # TODO must iterate around and see if there are any

    # def movement():
        # TODO?

    # def attack():
    
    # def repair():

    # def self_Destruct():

    def clear_move(self):
        self.type=""
        self.directionality=""
        self.action_consequence=""
