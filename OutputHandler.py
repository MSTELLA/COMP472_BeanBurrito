class OutputHandler:
    game_file = None
    filename = ""
    filepath=""
    action_consequence=""

    def setupfile(self,options):
        """ Creates File with appropriate filename and writes Game parameters"""
        # WE SHOULD ERASE FIRST
        self.generate_filename(options.alpha_beta, options.max_time, options.max_turns)
        self.filepath="./" + self.filename
        self.write_to_file(self.filepath,self.start_game_string(options))

    def generate_filename(self, alpha_beta, max_time, max_turns):
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
        current_player= "Attacker" if game.next_player.value==0 else "Defender"
        turn_string += current_player + ": " 
        turn_string += game.move_handler.ACTION.name + " from "+game.move_handler.coords.src.to_string() + " to " +game.move_handler.coords.dst.to_string()

        if (game.options.game_type.value == 3): #  CompVsComp = 3
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)

        elif (game.options.game_type.value == 1 and game.next_player.value==1 ): #     AttackerVsComp = 1     Defender = 1
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)

        elif (game.options.game_type.value == 2 and game.next_player.value==0 ): #     CompVsDefender = 2     Attacker = 0
            turn_string += "\n time for this action: " + str(round(game.stats.elapsed_seconds_current_action,2)) + "s"
            turn_string += "\n heuristic score: " + str(game.stats.score_current_action)

        turn_string += "\n" + game.board_print() + "\n"

        with open(self.filepath, 'a') as file:
            file.write(turn_string)

    def write_end_game(self,player_type, turns_played):
        """ Generates end of game text and closes the OutputHandler file"""
        end_game_string=f"\nEnd of Game! {player_type} wins in {turns_played} turns."
        with open(self.filepath, 'a') as file:
            file.write(end_game_string)
        self.game_file.close()