
class Parser():

    def parsing(self, input_file: str) -> None:

        with open(input_file, "r") as file:
            for line in file:
                print(line)