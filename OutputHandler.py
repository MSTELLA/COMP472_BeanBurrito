import os

class OutputHandler:
    filename = ""
    action_consequence=""

    def generate_filename(self, alpha_beta, timeout, max_turns):
        filename = f"gameTrace-{alpha_beta}-{timeout}-{max_turns}.txt"

    def write_to_file(self, file_path, text):
        with open(file_path, 'w') as file:
            file.write(text)
        self.action_consequence="Writting to'{file_path}' succesful!"
