from pydantic import BaseModel
import abstracts


class Coordinate(BaseModel):
    x: int
    y: int

    def __str__(self):
        return f"({self.x}, {self.y})"
    

class Operation(BaseModel):
    object: abstracts.AbstractDrawable
    coordinate: Coordinate

    def __str__(self):
        return f"({self.object}, {self.coordinate})"
    
    def __eq__(self, other):
        return self.object.id == other.object.id
