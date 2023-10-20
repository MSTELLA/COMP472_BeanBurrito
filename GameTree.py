import bigtree
from bigtree import Node, print_tree

class GameTree:
    time_info=None

    def __init__(self, current_game):
        current_player_minimax = "MIN" if current_game.next_player.value == 0 else "MAX" # We maximize for defender (1), minimize for attacker (0)
        self.root = Node("current_game", game=current_game, minimax = current_player_minimax)
        # self.max_search_depth = max_search_depth

    # def expand_tree_max_levels(self):
    #     for i in range(self.max_search_depth):
    #         # print("TEST TREE: working on LEVEL ", str(i))
    #         self.expand_tree_1_level()

    def expand_tree_1_level(self):
        # iterate through each leaf or better nodes from a specific level and apply expand_one_node to them
        current_leaves = list(self.root.leaves)
        for leaf in current_leaves:
            self.expand_one_node(leaf)
            # print_tree(self.root)
        return self.root
    
    def expand_one_node(self, parent_node):
        # CHECK IF GAME IS NOT OVER (also checks max turns)
        if parent_node.game.has_winner_internal():
            return None

        # mode_candidates() returns a list of possible moves from the current game. Returns a list of valid CoorPair
        children=[]
        i = 0 # for generating children ids

        for child_CoordPair in parent_node.game.move_candidates(): #for each CoordPair in move_candidates CoorPair list
            # print("TESTING TREE: going to perform move ", child_CoordPair.src.to_string(), " to ", child_CoordPair.dst.to_string())
            
            # shallow copy of current game
            newgame = parent_node.game.clone()

            # perform the possible CoordPair move
            newgame.perform_move_on_board_only(child_CoordPair)

            minimax =  "MAX" if parent_node.get_attr("minimax")=="MIN" else "MIN" # Heuristics made to be maximized by defender and minimized by attacker
            
            newgame.next_turn()

            #Create a new Node
            id = "node_level(" + str(parent_node.depth) + ")-childnode(" + str(i) + ")" # Node id
            new_node_child = Node(id, parent = parent_node, game = newgame, move=child_CoordPair, minimax=minimax)
            # print("TESTING TREE: created node: ", id)
            i+=1
            children.append(new_node_child)

        # Add these new nodes to the parent
        parent_node.children=children
            
