import numpy as np
import matplotlib.pyplot as plt
from utils.dxf_shift.config import aci_color_code_dict

class Shape:
    def __init__(self, list_of_points, color="blue"):
        self.points = list_of_points
        self.n = len(self.points)
        self.color = color
        self.area = self.calculate_area()
        return

    def calculate_area(self):
        if self.n < 3:
            print("not a polygon")
            return 0

        sum = 0
        for i in range(self.n):
            p1 = self.points[i]
            p2 = self.points[(i+1) % self.n]
            sum += p1.x * p2.y - p2.x * p1.y

        area = abs(sum) / 2
        return area

    def change_point(self, index, new_point):
        self.points[index] = new_point
        self.area = self.calculate_area()
        return

    def _copy_points(self):
        points_copy = []
        for point in self.points:
            points_copy.append(point.mcopy())
        return points_copy

    def mcopy(self, color="black"):
        return Shape(self._copy_points(), color)

    def exshow(self, to_export=False):
        xs = []
        ys = []
        colors = []
        for point in self.points:
            xs.append(point.x)
            ys.append(point.y)
            colors.append(aci_color_code_dict[point._color_code])

        xs.append(self.points[0].x)
        ys.append(self.points[0].y)

        plt.scatter(np.array(xs), np.array(ys), s=50, c=colors, zorder=100)
        plt.plot(np.array(xs), np.array(ys), c=self.color, zorder=99)

        for i in range(len(xs)):
            plt.text(xs[i]*(1+(2*i/100)), ys[i], str(i), fontsize=12, ha='right', va='bottom', color="red")

        if to_export:
            plt.savefig(f"{self.color}_{self.n}N_shape.png")
        else:
            plt.show()
        return

    def show(self, to_export=False):
        for i in range(self.n):
            point = self.points[i]
            c = aci_color_code_dict[point._color_code]
            plt.plot(point.x, point.y, 'o', c=c, zorder=100)
            plt.text(point.x+5, point.y, str(i%self.n), fontsize=12, ha='left', va='bottom', color=c)

            # to draw the edge
            next_point = self.points[(i+1) % self.n]
            plt.plot((point.x, next_point.x), (point.y, next_point.y), c=aci_color_code_dict[next_point._color_code], zorder=99)

        if to_export:
            plt.savefig(f"{self.color}_{self.n}N_shape.png")
        else:
            plt.show()
        return
    
    def download(self):
        self.show(to_export=True)
        return

