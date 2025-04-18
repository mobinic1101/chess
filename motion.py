import abstracts
import datatypes
import math
from typing import SupportsIndex


class Mtion:
    def __init__(self, speed: int):
        self.operations: list[datatypes.Operation] = []
        self.speed = speed

    def add_operation(
        self, drawable: abstracts.AbstractDrawable, destination: datatypes.Coordinate
    ):
        """add a motion operation to the list of operations.

        Args:
            drawable (abstracts.AbstractDrawable): The object to be moved.
            destination (datatypes.Coordinate): The destination coordinates to move to.
        """
        i = self.find_operation(drawable)
        if i is not None:
            operation = self.operations[i]
            operation.coordinate = destination
            return

        new_operation = datatypes.Operation(drawable, destination)
        self.operations.append(new_operation)

    def remove_operation(self, drawable: abstracts.AbstractDrawable):
        i = self.find_operation(drawable)
        if i is not None:
            del self.operations[i]
            return 1
        return 0

    def find_operation(self, drawable: abstracts.AbstractDrawable) -> SupportsIndex:
        for i in range(len(self.operations)):
            operation = self.operations[i]
            if operation.object.id == drawable.id:
                return i
        return None

    def apply_motion(self):
        for operation in self.operations:
            dx, dy = ( # the direction arrow
                operation.coordinate.x - operation.object.rect.x,
                operation.coordinate.y - operation.object.rect.y,
            )
            distance = math.sqrt(dx ** 2 + dy ** 2) # length of the arrow
            if distance == 0: # avoid ZeroDivisionError
                continue

            # reducing lenght of the arrow
            new_dx, new_dy = dx / distance, dy / distance
            step_x, step_y = new_dx * self.speed, new_dy * self.speed

            # if the distance between the object and the target is less than the step
            # we can reach the target instantly and we can stop the operation
            if distance < math.sqrt(step_x ** 2 + step_y ** 2):
                operation.object.rect.x = operation.coordinate.x
                operation.object.rect.y = operation.coordinate.y
                self.remove_operation(operation.object)
                continue

            operation.object.move_x(step_x)
            operation.object.move_y(step_y)

