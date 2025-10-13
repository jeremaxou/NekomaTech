import subprocess


class Point:
    def __init__(self, x, y):
        self._x = [x]
        self._y = [y]

    @property
    def x(self):
        return self._x[0]

    @x.setter
    def x(self, value):
        self._x[0] = value  # Change dynamiquement

    @property
    def y(self):
        return self._y[0]

    @y.setter
    def y(self, value):
        self._y[0] = value  # Change dynamiquement
        
    def mix_x_y(self, point1, point2):
        self._x[0] = point1.x
        self._y[0] = point2.y
    
    def symetrical_y(self, point1, point2):
        self.y[0] = 2*point2.y - point1.y
    
    def move(self, x, y):
        self.move_x(x)
        self.move_y(y)

    def move_x(self, x):
        self._x[0] = x
    
    def move_y(self, y):
        self._y[0] = y

    def pos(self):
        return [self._x[0], self._y[0]]
    
    def pos_int(self):
        return [int(self._x[0]), int(self._y[0])]

    def is_different(self, point):
        return self.pos() != point.pos()
    
class Point_param(Point):
    def __init__(self, name, x, y, color):
        super().__init__(x, y)
        self.name = name
        self.color = color
    
    def __repr__(self):
        return f"Point_param(name={self.name}, x={self._x}, y={self._y}, color={self.color})"

if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])