from typing import TYPE_CHECKING
from pydantic import BaseModel
import abstracts


BaseModel.model_config['arbitrary_types_allowed'] = True


class Operation(BaseModel):
    object: abstracts.AbstractDrawable
    coordinate: tuple

    def __str__(self):
        return f"({self.object}, {self.coordinate})"
    
    def __eq__(self, other):
        return self.object.id == other.object.id


class Move(BaseModel):
    """represents a single move a player does; 
    example: Move(source=(2, 4), dest=(2, 5))

    Args:
        BaseModel (_type_): _description_
    """
    
    source: tuple[int, int]
    dest: tuple[int, int]