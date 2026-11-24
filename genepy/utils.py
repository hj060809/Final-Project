from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .object import Object

class Scatter:
    def __init__(self, generator: Callable[[int], Object], count: int = 0, density: float = 0):
        if count < 0 or density < 0:
            raise ValueError('count and density must not be negative')
        if (count > 0) == (density > 0):
            raise ValueError('specify exactly one of count or density')
    
        self.generator = generator
        self.count = count
        self.density = density

    def uniform(self, width: int, height: int) -> list[Object]:
        count = self.count or round(self.density * width * height)

        objects = []
        for i in range(count):
            obj = self.generator(i)
            objects.append(obj)

        return objects
