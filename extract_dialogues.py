import os

import drama_states


class DramaContext:
    def __init__(self, drama_path):
        self.current_state = drama_states.DramaBeginning()
        self.dialogues = []
        self.drama_path = drama_path

    def get_quotes(self):
        return self.dialogues

    def process_line(self, line):
        self.current_state = self.current_state.transition(line, context=self)
        self.current_state.handle(line, context=self)

    def process_drama(self):
        print(f"\nPrzetwarzanie {self.drama_path}")
        with open(self.drama_path, encoding="utf8") as drama:
            for line in drama:
                self.process_line(line)
        if self.current_state.__class__ != drama_states.DramaEnded:
            print(f"\n{self.drama_path} -- niepoprawny stan: {self.current_state.__class__.__name__}")
        else:
            print(f"Przetwarzanie {self.drama_path} zakończone, znaleziono {len(self.dialogues)} dialogów "
                  f"(złożonych z {sum(len(dialogue) for dialogue in self.dialogues)} wypowiedzi)")


def extract_dialogues(folder_path="dramas", output_file="drama_quotes.txt"):
    dialogues = []
    if not folder_path.endswith("/") or not folder_path.endswith("\\"):
        slash = "/"
        if "\\" in folder_path:
            slash = "\\"
        folder_path = folder_path + slash
    for drama_path in os.listdir(folder_path):
        drama = DramaContext(folder_path + drama_path)
        drama.process_drama()
        dialogues += drama.get_quotes()
    print(f"Znaleziono {len(dialogues)} dialogów "
          f"(złożonych z {sum(len(dialogue) for dialogue in dialogues)} wypowiedzi)")
    with open(output_file, "w", encoding="utf8") as file:
        for quote in dialogues:
            file.write(str(quote) + "\n")


if __name__ == "__main__":
    extract_dialogues()