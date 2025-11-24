from scripts.shift_script.config import aci_color_code_dict

class Point:
  def __init__(self, x, y, info=[], color=0):
    self._info = info # to store the original point's position in the data file
    self._color_code = color
    self.x = x
    self.y = y
    return

  def distance(self, point):
    x1, y1 = (self.x, self.y)
    x2, y2 = (point.x, point.y)
    distance = np.sqrt((x1-x2)**2 + (y1-y2)**2)
    return distance

  def move(self, delta_x=0, delta_y=0):
    self.x += delta_x
    self.y += delta_y
    return

  def mcopy(self):
    return Point(self.x, self.y, self._info, self._color_code)

  def pprint(self):
    return f"({self.x},{self.y})"

  ###############################################################

  def __add__(self, other):
    return Point(self.x + other.x, self.y + other.y, self._info, self._color_code)

  def __sub__(self, other):
    return Point(self.x - other.x, self.y - other.y, self._info, self._color_code)

  def __mul__(self, scalar: float):
    return Point(self.x * scalar, self.y * scalar, self._info, self._color_code)

  def __eq__(self, other):
    if not isinstance(other, Point):
        return False
    return self.x==other.x and self.y==other.y

  def __repr__(self):
    return f"Point({self.x}, {self.y}), color={aci_color_code_dict[self._color_code]}, index={self._info}"