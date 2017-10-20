import abc
from typing import List


class State(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def should_transit_to(line: str) -> bool:
        pass

    @abc.abstractmethod
    def transition(self, line: str, context) -> 'State':
        pass

    @abc.abstractmethod
    def handle(self, line: str, context):
        pass


class DramaBeginning(State):
    @staticmethod
    def should_transit_to(line: str):
        return False

    def transition(self, line: str, context) -> State:
        if StageDirections.should_transit_to(line):
            return StageDirections(previous_state=self)
        if DramatisPersonae.should_transit_to(line):
            return DramatisPersonae()
        if WaitingForDialogue.should_transit_to(line):
            return WaitingForDialogue()
        if Dialogue.should_transit_to(line):
            return Dialogue()
        return self

    def handle(self, line: str, context):
        pass


class DramatisPersonae(State):
    beginnings = ["osoby", "statyści", "chóry"]
    first_line = True

    @staticmethod
    def should_transit_to(line):
        return any(line.lower().startswith(beggining) for beggining in DramatisPersonae.beginnings)

    def transition(self, line: str, context) -> State:
        if line.strip() != "" and not line.strip().startswith("*"):
            return DramaBeginning()
        return self

    def handle(self, line: str, context):
        if not self.first_line and line.strip() != "":
            print(line.strip(" *\n"))
        self.first_line = False


class WaitingForDialogue(State):
    beginnings = ["AKT", "SCENA", "PROLOG"]

    @staticmethod
    def should_transit_to(line: str):
        scene_beggining = any(line.startswith(beggining) for beggining in WaitingForDialogue.beginnings)
        return scene_beggining

    def transition(self, line: str, context) -> State:
        if DramaEnded.should_transit_to(line):
            return DramaEnded()
        if StageDirections.should_transit_to(line):
            return StageDirections(previous_state=self)
        if DramatisPersonae.should_transit_to(line):
            return DramatisPersonae()
        if Dialogue.should_transit_to(line):
            return Dialogue()
        return self

    def handle(self, line: str, context):
        pass


class Dialogue(State):
    def __init__(self):
        self.long_monologue = False
        self.current_quote = []
        self.current_dialogue = []

    @staticmethod
    def should_transit_to(line):
        return (line.strip().isupper() and
                not WaitingForDialogue.should_transit_to(line) and
                not DramatisPersonae.should_transit_to(line) and
                not line.startswith("ISBN"))

    @staticmethod
    def remove_stage_directions(line):
        if line.count("/") != 2:
            return line
        begining, end = line.find("/"), line.rfind("/")
        line = line[:begining] + line[end + 1:]
        line = "".join(line.split())
        return line

    def transition(self, line: str, context) -> State:
        if DramaEnded.should_transit_to(line):
            self.save_dialogue(context)
            return DramaEnded()
        if StageDirections.should_transit_to(line):
            return StageDirections(previous_state=self)
        if DramatisPersonae.should_transit_to(line):
            return DramatisPersonae()
        if WaitingForDialogue.should_transit_to(line) or self.long_monologue:
            self.save_dialogue(context)
            return WaitingForDialogue()
        return self

    def handle(self, line: str, context):
        if self.should_transit_to(line) and "".join(self.current_quote).strip() != "":  # next actor
            self.add_quote_to_dialogue()
            self.current_quote = []
        if not self.should_transit_to(line) and not StageDirections.single_line_stage_directions(line):
            cleared_line = self.remove_stage_directions(line.strip())
            self.add_line_to_quote(cleared_line)
            if self.to_long_monologue():
                self.long_monologue = True

    def to_long_monologue(self):
        def words_count(quote: List[str]):
            return sum(len(line.split()) for line in quote)
        quote = self.current_quote
        if len(quote) > 3 or words_count(quote) > 20:
            return True
        return False

    def add_quote_to_dialogue(self):
        if not self.to_long_monologue():
            for line_idx, line in enumerate(self.current_quote[1:]):
                line_idx += 1
                if self.current_quote[line_idx-1][-1] != '.':
                    line = line[0].lower() + line[1:]
                line = " " + line
                self.current_quote[line_idx] = line
            self.current_dialogue.append("".join(self.current_quote))

    def save_dialogue(self, context):
        if self.current_dialogue != []:
            context.dialogues.append(self.current_dialogue)

    def add_line_to_quote(self, line):
        only_alpha = [char for char in line if char.isalpha()]
        if line.strip() != "" and only_alpha != []:
            self.current_quote.append(line)


class StageDirections(State):
    @staticmethod
    def should_transit_to(line: str):
        line = line.strip()
        return line.startswith("/") and not line.endswith("/")

    @staticmethod
    def single_line_stage_directions(line) -> bool:
        return line.startswith("/") and line.endswith("/")

    def __init__(self, previous_state: State):
        self.previous_state = previous_state

    def transition(self, line: str, context) -> State:
        assert self.previous_state is not None
        if line.strip().endswith("/"):
            return self.previous_state
        return self

    def handle(self, line: str, context):
        pass


class DramaEnded(State):
    ending_string = "Ta lektura, podobnie jak tysiące innych, dostępna jest na stronie wolnelektury.pl."

    @staticmethod
    def should_transit_to(line):
        return line.strip() == DramaEnded.ending_string

    def transition(self, line: str, context) -> State:
        return self

    def handle(self, line: str, context):
        pass
