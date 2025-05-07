from abstracts import AbstractPlayer, AbstractInputSource


class Player(AbstractPlayer):
    def __init__(self, name: str, color: str, input_source: AbstractInputSource):
        super().__init__(name, color, input_source)
