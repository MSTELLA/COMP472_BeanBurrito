# AI handler with minimax alphabeta e0 e1 e2
from GameTree import GameTree

class MinimaxHandler:
    heuristic = ""
    game = None

    #create Search Tree wiht minmax levels?

    #method minimax

    #method minimax with alphabeta

    #heuristic e0
    '''
    - e0 = (3VP1 + 3TP1 + 3FP1 + 3PP1 + 9999AIP1) - (3VP2 + 3TP2 + 3FP2 + 3PP2 + 9999AIP2) where:
        VPi =nbofVirusofPlayeri TPi =nbofTechofPlayeri FPi =nbofFirewallofPlayeri PPi =nbofProgramofPlayeri AIPi =nbofAIofPlayeri
    '''
    def e0(self, game, defender, attacker) -> int:
        self.game = game
        unit_weights = [9999, 3, 3, 3, 3] # AI, Tech, Virus, Program, Firewall

        # P1 sum - P2 sum, defender is P1 and attacker is P2 , therefore defender is maximizing and attacker is minimizing
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
    def e2(self, game, defender, attacker) -> int:
        # difference in AI health
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        ai_health_dif = game.player_ai_health(defender) - game.player_ai_health(attacker)

        # open distance between attackers units and defender AI, specifically Virus units because they can kill the AI in one hit
        # using the euclidean distance to calculate distance between units
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        distance_to_defender_ai = 0
        unit_weights = [3, 3, 9, 1, 1] # AI, Tech, Virus, Program, Firewall weighted by their damage to AI
        defender_ai_location = game.locate_unit_ai_board(defender)
        for attacker_unit in game.player_units(attacker):
            distance = game.calculate_distance_units(defender_ai_location, attacker_unit[0])
            distance_to_defender_ai += (unit_weights[attacker_unit[1].type.value] * distance)

        # inverse attacker damage potential , we use the inverse that that defender is always maximizing and attacker is minimizing
        # from current position what damage can be done
        inverse_damage_potential = 0
        for attacker_unit in game.player_units(attacker):
            for adjacent in attacker_unit[0].iter_adjacent():
                if game.get(adjacent) is not None:
                    unit = game.get(adjacent)
                    if attacker_unit[1].player != unit.player: # for now we only consider damage is can do on the defender
                        inverse_damage_potential -= attacker_unit.damage_amount(unit)

        # number of units engaged in combat
        # defender engaged will minus and attacker engaged will add to this value, therefore
        # # defender is trying to maximize this number, and attacker is trying to minimize this number 
        number_units_engaged_in_combat = 0
        for attacker_unit in game.player_units(attacker):
            # (only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat)
            if attacker_unit[1].type.value == 0 or attacker_unit[1].type.value == 3 or attacker_unit[1].type.value == 4:
                for adjacent in attacker_unit[0].iter_adjacent():
                    if game.get(adjacent) is not None:
                        if game.get(adjacent).player != attacker_unit[1].player:
                                # they are engaged in combat
                                number_units_engaged_in_combat += 1

        for defender_unit in game.player_units(defender):
            # (only 0:AI, 3:Program and 4:Firewall cannot move if engaged in combat)
            if defender_unit[1].type.value == 0 or defender_unit[1].type.value == 3 or defender_unit[1].type.value == 4:
                for adjacent in defender_unit[0].iter_adjacent():
                    if game.get(adjacent) is not None:
                        if game.get(adjacent).player != defender_unit[1].player:
                            # they are engaged in combat
                            number_units_engaged_in_combat -= 1

        # TODO : maybe we can add weights to these ?
        return ai_health_dif + distance_to_defender_ai + inverse_damage_potential + number_units_engaged_in_combat

    # TODO implement a if else statement that calculates heuristic depending on heuristic chosen by user.
    def calculate_heuristic(self,node,heuristic):
        if heuristic == 'e0':
            return self.e0(node.game, node.Player.Defender, node.Player.Attacker) # NOT SURE IF RIGHT WAY TO IMPLEMENT
        if heuristic == 'e1':
            return self.e1(node.game, node.Player.Defender, node.Player.Attacker)  # NOT SURE IF RIGHT WAY TO IMPLEMENT
        if heuristic == 'e2':
            return self.e2(node.game, node.Player.Defender, node.Player.Attacker)  # NOT SURE IF RIGHT WAY TO IMPLEMENT

    # method minimax with alphabeta
    def minimax(self,node,depth,maximizing_player,alpha_beta = False, alpha=-float('inf'), beta=float('inf')):

        if depth == 0 or node.is_terminal():
            return self.calculate_heuristic(node)

        # Defender player logic
        if maximizing_player:  # NEED TO CHANGE IF PLAYER == Defender
            maxEval = -float('inf')
            for child in node.children:
                # we are recursively calling the minimax player where the maximizing player is now false
                # At this depth it is the minimizing players turn (Attackers)
                currentEval = self.minimax(child, depth - 1, False, alpha_beta, alpha, beta) #TODO somehow set player defender max and attacker min
                maxEval = max(maxEval, currentEval)  # will replace max eval if currentEval > maxEval

                # if we turn on alpha beta pruning:
                if alpha_beta:
                    alpha = max(alpha, currentEval)  # Setting our new alpha value (the larger number out of the two)
                    # If beta is greater than or equal to alpha, prune the rest of the branches!
                    if beta <= alpha:
                        break

            return maxEval

        # Attacker Player Logic
        else:
            minEval = float('inf')
            for child in node.children:
                # we are recursively calling the minimax player where the maximizing player is now True
                # At this depth it is the minimizing players turn (Attackers)
                currentEval = self.minimax(child,depth-1,True, alpha_beta, alpha, beta)
                minEval = min(minEval, currentEval)

                # if alpha beta is turned on
                if alpha_beta:
                    beta = min(beta,currentEval)  # Setting our new beta value (the smaller number out of the two)
                    # For min if alpha is greater than or equal to beta, PRUNE!
                    if beta <= alpha:
                        break

            return minEval
