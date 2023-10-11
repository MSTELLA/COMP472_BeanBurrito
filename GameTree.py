import bigtree
from bigtree import Node, print_tree

class GameTree:
    time_info=None

    def __init__(self, current_game, heuristic, max_search_depth = 1):
        self.root = Node("current_game", game=current_game)
        self.max_search_depth = max_search_depth

    def expand_tree_max_levels(self):
        limit = self.max_search_depth
        while (limit >= 0):
            self.expand_tree_1_level()
            # keep track of stats TODO
            limit = limit - 1

    def expand_tree_1_level(self):
        # iterate through each leaf or better nodes from a specific level and apply expand_one_node to them
        for leaf in self.root.leaves:
            self.expand_one_node(leaf)
    
    def expand_one_node(self, parent_node):
        # CHECK IF GAME IS NOT OVER
        if parent_node.game.has_winner():
            return None

        # CHECK IF max_turns
        if parent_node.game.has_winner():
            return None

        # mode_candidates() returns a list of possible moves from the current game. Returns a list of valid CoorPair
        # children_CoordPair = parent_node.game.move_candidates()  
        # print("TESTING TREE: generated ", str(len(list(enumerate(children_CoordPair))))," candidate moves")
        children=[]
        i = 0 # for generating children ids

        for child_CoordPair in parent_node.game.move_candidates(): #for each CoordPair in move_candidates CoorPair list
            # print("TESTING TREE: going to perform move ", child_CoordPair.src.to_string(), " to ", child_CoordPair.dst.to_string())
            newgame = parent_node.game.clone() # shallow copy of current game
            newgame.perform_move(child_CoordPair) # perform the possible CoordPair move
            newgame.next_turn() # get the consequences of this CoordPair
            # print("TESTING TREE: performed move ",child_CoordPair.src.to_string(), " to ", child_CoordPair.dst.to_string())

            #Create a new Node
            id = "parent(" + str(parent_node.name) + ")-node_level(" + str(parent_node.depth + 1) + ")-child(" + str(i) + ")" # Node id : child level, parent name (level and child of parent) child number of parent
            new_node_child = Node(id, parent = parent_node, game = newgame, move=child_CoordPair)
            # print("TESTING TREE: created node: ", id)
            i+=1
            children.append(new_node_child)
        
        # Add these new nodes to the parent
        parent_node.children=children

    
            
