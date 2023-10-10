# AI handler with minimax alphabeta e0 e1 e2

class Minimax_Handler:
    heuristic = ""
    game = None

    #create Search Tree wiht minmax levels?

    #method minimax

    #method minimax with alphabeta

    #heuristic e0
    # def e0():
    #     unit_weights = [9999, 3, 3, 3, 3] # AI, Tech, Virus, Program, Firewall
    #     game.player_units(Player.Attacker)
    #     game.player_units(player.Defender)
        # iterate through Attacker units and * by weights
        # - iterate through Attacker units and * by weights

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
    def e1():
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        return game.player_ai_health(player.Defender) - game.player_ai_health(Player.Attacker)
    '''
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