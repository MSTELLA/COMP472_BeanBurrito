# AI handler with minimax alphabeta e0 e1 e2
from GameTree import GameTree

class MinimaxHandler:
    heuristic = ""
    game = None

    #create Search Tree wiht minmax levels?

    #method minimax

    #method minimax with alphabeta

    #heuristic e0
    def e0(self, game, defender, attacker) -> int:
        self.game = game
        unit_weights = [9999, 3, 3, 3, 3] # AI, Tech, Virus, Program, Firewall

        # P1 sum  - P2 sum, defender is P1 and attacker is P2 , therefore defender is minimizing and attacker is maximizing
        unit_count_p1, unit_count_p2 = [0, 0 , 0 , 0, 0], [0, 0 , 0 , 0, 0] # AI, Tech, Virus, Program, Firewall
        # get the number of units for each player
        for p1_unit in game.player_units(defender):
            unit_count_p1[p1_unit[1].type.value] += 1
        for p2_unit in game.player_units(attacker):
            unit_count_p2[p2_unit[1].type.value] += 1

        sum_p1, sum_p2 = 0, 0
        for unit in [0, 1, 2, 3, 4]:  # AI, Tech, Virus, Program, Firewall
            sum_p1 = sum_p1 + (unit_weights[unit] * unit_count_p1[unit])
            sum_p2 = sum_p2 + (unit_weights[unit] * unit_count_p2[unit])
        
        return sum_p1 - sum_p2
    
    #heuristic e1
    '''
    - AI health difference (attacker wants to minimize defender AI health) (defender wants to maximize defender AI health)
       '''
    def e1(self, game, defender, attacker) -> int:
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        return game.player_ai_health(defender) - game.player_ai_health(attacker)

    #heuristic e2
    '''
	- AI health difference (attacker wants to minimize defender AI health) (defender wants to maximize defender AI health)
	- Open distance between attacker units and defender AI (minimize) (inverse so that defender wants to maximize defender AI health)
	- Damage potential (AI damage separate from defender units) ( utilizes self-destruct )
    - Number of units engaged in combat
    '''
    def e2(self, game, defender, attacker):
        # difference in AI health
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        ai_health_dif = game.player_ai_health(defender) - game.player_ai_health(attacker)

        # open distance between attackers units and defender AI, specifically Virus units because they can kill the AI in one hit
        # using the euclidean distance to calculate distance between units
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        open_distance = 0
        unit_weights = [0.3, 0.3, 0.9, 0.1, 0.1] # AI, Tech, Virus, Program, Firewall weighted by their damage to AI
        # using 0.0 so that values arent too big
        defender_ai_location = (list(game.locate_unit_on_board(defender, "AI")))[0]
        for attacker_unit in game.player_units(attacker):
            distance = game.calculate_distance_units(defender_ai_location, attacker_unit[0])
            open_distance += (unit_weights[attacker_unit[1].type.value] * distance)

        # inverse attacker damage potential , we use the inverse that that defender is always maximizing and attacker is minimizing
        # from current position what damage can be done

        # number of units engaged in combat

        return ai_health_dif + open_distance
