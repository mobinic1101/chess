from pydantic import BaseModel
import abstracts
    

class Operation(BaseModel):
    object: abstracts.AbstractDrawable
    coordinate: tuple

    def __str__(self):
        return f"({self.object}, {self.coordinate})"
    
    def __eq__(self, other):
        return self.object.id == other.object.id
