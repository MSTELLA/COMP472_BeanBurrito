class OutputHandler:
    game_file = None
    filename = ""
    filepath=""
    action_consequence=""

    def setupfile(self,options):
        """ Creates File with appropriate filename and writes Game parameters"""
        self.generate_filename(options.alpha_beta, options.max_time, options.max_turns)
        self.filepath="./" + self.filename
        self.write_to_file(self.filepath,self.start_game_string(options))

    def generate_filename(self, alpha_beta, max_time, max_turns):
        """ Creates file name with game parameters entered by user"""
        self.filename = f"gameTrace-{alpha_beta}-{max_time}-{max_turns}.txt"

    def write_to_file(self, filepath, text):
        """ Creates file object with appropriate filename and sets OutputHandler file attribute"""
        with open(filepath, 'w') as file:
            self.game_file=file
            file.write(text)
        self.action_consequence="Writting to'{file_path}' succesful!"

    def start_game_string(self,options):
        start_game_string="Game Parameters:\n Timeout: "+ str(options.max_time) + " seconds" + "\n Max number of turns: " + str(options.max_turns) + "\n Play mode: " + options.game_type.name
        if (options.game_type.value != 0):  # AttackerVsDefender = 0
            start_game_string += "\n Alpha-Beta: " + str(options.alpha_beta)
            start_game_string +=  "\n Heuristic: " + options.heuristic 
        
        start_game_string += "\n"
        return start_game_string

    def write_turn(self,game):
        turn_string="\nTurn #" + str(game.turns_played) +"\n "
        current_player= "Attacker" if game.next_player.value==1 else "Defender" #  Defender = 1
        turn_string += current_player + ": " 
        turn_string += game.move_handler.ACTION.name + " from "+game.move_handler.coords.src.to_string() + " to " +game.move_handler.coords.dst.to_string()

        if (game.options.game_type.value == 3): #  CompVsComp = 3
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)
            
            turn_string += "\nGame cumulative information:"
            total_evals = sum(game.stats.evaluations_per_depth.values())
            turn_string += "\n Evals: " + str(total_evals)

            turn_string += "\n Evals by depth: " 
            eval_depth_str = "" 
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str += (f"{k}:{game.stats.evaluations_per_depth[k]}  ")
            turn_string += eval_depth_str

            turn_string += "\n Evals by depth %: " 
            eval_depth_str_pct = ""
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str_pct+= (f"{k}:{round((game.stats.evaluations_per_depth[k]/total_evals*100),1)} ")
            turn_string += eval_depth_str_pct

            turn_string += "\n Average branching factor: " +  str(round(game.stats.average_branching_factor,2))


        elif (game.options.game_type.value == 1 and game.next_player.value==0 ): #     AttackerVsComp = 1     Defender = 1 just player, so next player is 0
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)
            
            turn_string += "\nGame cumulative information:"
            total_evals = sum(game.stats.evaluations_per_depth.values())
            turn_string += "\n Evals: " + str(total_evals)

            turn_string += "\n Evals by depth: " 
            eval_depth_str = "" 
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str += (f"{k}:{game.stats.evaluations_per_depth[k]}  ")
            turn_string += eval_depth_str

            turn_string += "\n Evals by depth %: " 
            eval_depth_str_pct = ""
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str_pct+= (f"{k}:{round((game.stats.evaluations_per_depth[k]/total_evals*100),1)} ")
            turn_string += eval_depth_str_pct

            turn_string += "\n Average branching factor: " +  str(round(game.stats.average_branching_factor,2))


        elif (game.options.game_type.value == 2 and game.next_player.value==1 ): #     CompVsDefender = 2     Attacker = 0 just played so next player is 1
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)

            turn_string += "\nGame cumulative information:"
            total_evals = sum(game.stats.evaluations_per_depth.values())
            turn_string += "\n Evals: " + str(total_evals)

            turn_string += "\n Evals by depth: " 
            eval_depth_str = "" 
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str += (f"{k}:{game.stats.evaluations_per_depth[k]}  ")
            turn_string += eval_depth_str

            turn_string += "\n Evals by depth %: " 
            eval_depth_str_pct = ""
            for k in sorted(game.stats.evaluations_per_depth.keys()):
                eval_depth_str_pct+= (f"{k}:{round((game.stats.evaluations_per_depth[k]/total_evals*100),1)} ")
            turn_string += eval_depth_str_pct

            turn_string += "\n Average branching factor: " +  str(round(game.stats.average_branching_factor,2))


        turn_string += "\n" + game.board_print() + "\n"

        with open(self.filepath, 'a') as file:
            file.write(turn_string)

    def write_end_game(self,player_type, turns_played):
        """ Generates end of game text and closes the OutputHandler file"""
        end_game_string=f"\nEnd of Game! {player_type} wins in {turns_played} turns."
        with open(self.filepath, 'a') as file:
            file.write(end_game_string)
        self.game_file.close()