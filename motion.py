import abstracts
import datatypes
import math
from typing import SupportsIndex


class Motion:
    def __init__(self, speed: int):
        self.operations: list[datatypes.Operation] = []
        self.speed = speed

    def add_operation(
        self, drawable: abstracts.AbstractDrawable, destination: tuple[int, int]
    ):
        """add a motion operation to the list of operations.

        Args:
            drawable (abstracts.AbstractDrawable): The object to be moved.
            destination (tuple[int, int]): The destination coordinates to move to.
        """
        # if there is already an operation exists, we just update its destination
        i = self.find_operation(drawable)
        if i is not None:
            operation = self.operations[i]
            operation.coordinate = destination
            return

        new_operation = datatypes.Operation(object=drawable, coordinate=destination)
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
                operation.coordinate[0] - operation.object.rect.x,
                operation.coordinate[1] - operation.object.rect.y,
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
                operation.object.rect.x = operation.coordinate[0]
                operation.object.rect.y = operation.coordinate[1]
                self.remove_operation(operation.object)
                continue

            operation.object.move_x(step_x)
            operation.object.move_y(step_y)
