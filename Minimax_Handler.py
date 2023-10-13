# AI handler with minimax alphabeta e0 e1 e2
from GameTree import GameTree

class Minimax_Handler:
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
        p1_units = list(game.player_units(defender))
        p2_units = list(game.player_units(attacker))

        unit_count_p1, unit_count_p2 = [0, 0 , 0 , 0, 0] # AI, Tech, Virus, Program, Firewall
        # get the number of units for each player
        for p1_unit in game.player_units(defender):
            unit_count_p1[p1_unit.type] = unit_count_p1[p1_unit.type] + 1
        for p2_unit in game.player_units(attacker):
            unit_count_p2[p2_unit.type] = unit_count_p2[p2_unit.type] + 1

        sum_p1, sum_p2 = 0
        for unit in [0, 1, 2, 3, 4]:  # AI, Tech, Virus, Program, Firewall
            sum_p1 = sum_p1 + (unit_weights[unit] * unit_count_p1[unit])
            sum_p2 = sum_p2 + (unit_weights[unit] * unit_count_p2[unit])
        
        return sum_p1 - sum_p2
    
    '''
    A combination of the following :
    Attacker
	- AI health difference (attacker wants to minimize defender AI health)
	- Open distance between attacker units and defender AI (minimize)
	- Damage potential (AI damage separate from defender units) ( utilizes self-destruct )
    Defender
	- AI health difference (defender wants to maximize defender AI health)
	- Open distance between attacker units and defender AI (minimize)
	- Position of techs and firewalls around AI
    '''
    #heuristic e1
    '''
    - AI health difference (attacker wants to minimize defender AI health)
    - AI health difference (defender wants to maximize defender AI health)
       '''
    def e1(self, game, defender, attacker) -> int:
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        return game.player_ai_health(defender) - game.player_ai_health(attacker)

    #heuristic e2
    '''
	- AI health difference (attacker wants to minimize defender AI health)
	- Open distance between attacker units and defender AI (minimize)
	- Damage potential (AI damage separate from defender units) ( utilizes self-destruct )

	- AI health difference (defender wants to maximize defender AI health)
	- Open distance between attacker units and defender AI (minimize)
	- Position of techs and firewalls around AI
    def e2():
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        ai_health_dif = game.player_ai_health(player.Defender) - game.player_ai_health(Player.Attacker)

        # inverse attacker damage potential , we use the inverse that that defender is always maximizing and attacker is minimizing
    '''