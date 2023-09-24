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
        # + "\n Alpha-Beta: " + options.alpha_beta => Future Deliverable
        #  If a player is an AI, indicate the name of your heuristic => Future Deliverable
        return start_game_string

    def write_turn(self,game):
        turn_string="\nTurn #" + str(game.turns_played) +"\n "
        current_player= "Attacker" if game.next_player.value==0 else "Defender"
        turn_string += current_player + ": " 
        turn_string += game.move_handler.ACTION.name + " from "+game.move_handler.coords.src.to_string() + " to " +game.move_handler.coords.dst.to_string() +"\n"
        turn_string += game.board_print() + "\n"
        with open(self.filepath, 'a') as file:
            file.write(turn_string)

    def write_end_game(self,player_type, turns_played):
        """ Generates end of game text and closes the OutputHandler file"""
        end_game_string=f"\nEnd of Game! {player_type} wins in {turns_played} turns."
        with open(self.filepath, 'a') as file:
            file.write(end_game_string)
        self.game_file.close()