# AI handler with minimax alphabeta e0 e1 e2
from GameTree import GameTree
import time
from datetime import datetime
from bigtree import Node, print_tree

class MinimaxHandler:
    heuristic = ""
    game = None
    evaluations_per_depth = {}
    current_Tree = None
    time_limit = None
    start_time = None

    def set_gametree_root(self, current_game):
        """ creates GameTree having the current game as its root. Used for iterative level creation and traversal."""
        self.current_Tree = GameTree(current_game)
        self.heuristic_counter_per_level = 0

    def set_heuristic(self, heuristic):
        """ Used to set the heuristic input by the player during the setup of the game"""
        self.heuristic = heuristic

    def self_destruct_potential(self, game, defender, attacker) -> int:
        defender_ai = game.ai_unit_on_board(defender)
        attacker_ai = game.ai_unit_on_board(attacker)
        
        if (defender_ai == None): return -1000 # ATTACKER WINS
        elif (attacker_ai == None): return 1000 # DEFENDER WINS

        potential = 0
        if game.next_player == attacker:
            for attacker_unit in game.player_units(attacker):
                for adjacent in attacker_unit[0].iter_adjacent():
                    if game.get(adjacent) is not None:
                        unit = game.get(adjacent)
                        if attacker_unit[1].player != unit.player: 
                            # if they do damage to opponenent AI this is good !
                            if unit.unit_name == "AI": potential -= 10 * (2)
                            else: potential -= 2 # else its oki
                        else:
                            # if they do damage to opponenent AI this is bad !
                            if unit.unit_name == "AI": potential += 10 * (2)
                            else: potential += 2 # else its oki
        else:
            for defender_unit in game.player_units(defender):
                for adjacent in defender_unit[0].iter_adjacent():
                    if game.get(adjacent) is not None:
                        unit = game.get(adjacent)
                        if defender_unit[1].player != unit.player: 
                            # if they do damage to opponenent AI this is good !
                            if unit.unit_name == "AI": potential += 10 * (2)
                            else: potential += 2 # else its oki
                        else:
                            # if they do damage to opponenent AI this is bad !
                            if unit.unit_name == "AI": potential -= 10 * (2)
                            else: potential -= 2 # else its oki
        return potential

    # heuristic e0
    '''
    - e0 = (3VP1 + 3TP1 + 3FP1 + 3PP1 + 9999AIP1) - (3VP2 + 3TP2 + 3FP2 + 3PP2 + 9999AIP2) where:
        VPi =nbofVirusofPlayeri TPi =nbofTechofPlayeri FPi =nbofFirewallofPlayeri PPi =nbofProgramofPlayeri AIPi =nbofAIofPlayeri
    '''
    def e0(self, game, defender, attacker) -> int:
        self.game = game
        unit_weights = [9999, 3, 3, 3, 3]  # AI, Tech, Virus, Program, Firewall

        # P1 sum - P2 sum, defender is P1 and attacker is P2 , therefore defender is maximizing and attacker is minimizing
        unit_count_p1, unit_count_p2 = [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]  # AI, Tech, Virus, Program, Firewall
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

    # heuristic e1
    '''
    - AI health difference (attacker wants to minimize defender AI health) (defender wants to maximize defender AI health)
    '''
    def e1(self, game, defender, attacker) -> int:
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        defender_ai = game.ai_unit_on_board(defender)
        attacker_ai = game.ai_unit_on_board(attacker)
        
        if (defender_ai == None): return -1000 # ATTACKER WINS
        elif (attacker_ai == None): return 1000 # DEFENDER WINS

        return (game.ai_unit_on_board(defender)[1].health - game.ai_unit_on_board(attacker)[1].health) + self.self_destruct_potential(game, defender, attacker)


    # heuristic e2
    '''
	- AI health difference (attacker wants to minimize defender AI health) (defender wants to maximize defender AI health)
	- Open distance between attacker units and defender AI (minimize) (inverse so that defender wants to maximize defender AI health)
	- Damage potential (AI damage separate from defender units)
    - Number of units engaged in combat
    '''

    def e2(self, game, defender, attacker) -> int:

        defender_ai = game.ai_unit_on_board(defender)
        attacker_ai = game.ai_unit_on_board(attacker)
        
        if (defender_ai == None): return -1000 # ATTACKER WINS
        elif (attacker_ai == None): return 1000 # DEFENDER WINS
        # difference in AI health
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        ai_health_dif = game.ai_unit_on_board(defender)[1].health - game.ai_unit_on_board(attacker)[1].health
        
        # open distance between attackers units and defender AI, specifically Virus units because they can kill the AI in one hit
        # using the euclidean distance to calculate distance between units
        # defender is trying to maximize this number, and attacker is trying to minimize this number 
        distance_to_defender_ai = 0
        unit_weights = [3, 3, 9, 1, 1]  # AI, Tech, Virus, Program, Firewall weighted by their damage to AI
        defender_ai_location = game.ai_unit_on_board(defender)[0]
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
                    if attacker_unit[1].player != unit.player:  # for now we only consider damage is can do on the defender
                        inverse_damage_potential -= attacker_unit[1].damage_amount(unit)

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
        return ai_health_dif + distance_to_defender_ai + inverse_damage_potential + number_units_engaged_in_combat + self.self_destruct_potential(game, defender, attacker)


    # TODO implement a if else statement that calculates heuristic depending on heuristic chosen by user.
    def calculate_heuristic(self, node):
        self.game = node.game
        node_level = node.depth-1
        if node_level in self.evaluations_per_depth.keys():
            self.evaluations_per_depth[node_level] = self.evaluations_per_depth[node_level] + 1 
        else:
            self.evaluations_per_depth[node_level] = 1

        if self.heuristic == "e0":
            return self.e0(node.game, self.game.players[0], self.game.players[1])
        elif self.heuristic =="e1":
            return self.e1(node.game, self.game.players[0], self.game.players[1]) 
        elif self.heuristic =="e2":
            return self.e2(node.game, self.game.players[0], self.game.players[1])

    # Implement iterative deepening for our minimax

    def iter_deep_minimax(self, max_depth, alpha_beta = False, time_limit=None):
        best_val = None
        best_move = None
        self.evaluations_per_depth = {}
        # print(" score ", str(best_val), " & move ", str(best_move), " at depth of search ", "start of iter_deep_max - should be None")

        if time_limit:
            self.time_limit = time_limit
            self.start_time = datetime.now()

        for depth in range(1, max_depth+1):
            
            # if time_limit and time.time() - start_time >= time_limit:
            elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
            # print("iterative with depth :", str(depth) , " TIME - ", str(elapsed_seconds) )
            if elapsed_seconds >= self.time_limit-0.5:
                # print("OUT OF TIME - ", str(elapsed_seconds) )
                return best_val, best_move

            # self.current_Tree.root = self.current_Tree.expand_tree_1_level() # expands on the current leaves 
        # iterate through each leaf or better nodes from a specific level and apply expand_one_node to them
            current_leaves = list(self.current_Tree.root.leaves)
            for leaf in current_leaves:
                self.current_Tree.expand_one_node(leaf)
                elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
                if elapsed_seconds >= self.time_limit-0.3:
                    # print("OUT OF TIME while creating a node - ", str(elapsed_seconds) )
                    break


            current_val, current_move = self.minimax(self.current_Tree.root,depth,alpha_beta)  # note default alpha beta is used
            # print(" score ", str(current_val), " & move ", current_move, " at depth of search ", str(depth))
            if current_val is not None:
                best_val, best_move = current_val, current_move
            # return best_val, best_move

        return best_val, best_move

    # method minimax with alphabeta option
    def minimax(self, node, depth, alpha_beta=False, alpha=-float('inf'), beta=float('inf')):

        if node.is_leaf:
            e_node = self.calculate_heuristic(node)
            # print("REACHED LEAF ", str(node.get_attr("move")), "at level ", str(node.depth), " with e(n): ", str(e_node))
            return e_node, node.get_attr("move")


        # Defender player logic
        if node.get_attr("minimax") == "MAX":
            maxEval = -float('inf')
            bestMove = None
            
            for child in node.children:
                # we are recursively calling the minimax player where the maximizing player is now false
                # At this depth it is the minimizing players turn (Attackers)
                currentEval, currentMove = self.minimax(child, depth - 1, alpha_beta, alpha,beta)

                # In suggest_move we are storing the returns in a two variable tuple, therefor need to store best move
                if currentEval > maxEval:
                    maxEval = currentEval
                    bestMove = child.get_attr("move") # best move is the move in the leaf...so should be child.

                # if we turn on alpha beta pruning:
                if alpha_beta:
                    alpha = max(alpha, currentEval)  # Setting our new alpha value (the larger number out of the two)
                    # If beta is greater than or equal to alpha, prune the rest of the branches!
                    if beta <= alpha:
                        break

            return maxEval, bestMove

        # Attacker Player Logic
        else:
            minEval = float('inf')
            bestMove = None

            for child in node.children:
                # we are recursively calling the minimax player where the maximizing player is now True
                # At this depth it is the minimizing players turn (Attackers)
                currentEval, currentMove = self.minimax(child, depth - 1, alpha_beta, alpha, beta)

                if currentEval < minEval:
                    minEval = currentEval
                    bestMove = child.get_attr("move") 

                # if alpha beta is turned on
                if alpha_beta:
                    beta = min(beta, currentEval)  # Setting our new beta value (the smaller number out of the two)
                    # For min if alpha is greater than or equal to beta, PRUNE!
                    if beta <= alpha:
                        break

            return minEval, bestMove


