# from main import Designs._get_intersection
from scripts.shift_script_v6.point import Point

from matplotlib.patches import Circle, Ellipse
import matplotlib.pyplot as plt
import numpy as np
import math

Sync_SHRINK_FACTOR = 1
GAS_SHRINK_FACTOR = 0.7
LINE_WIDTH = 1


class Designs:
    def _get_intersection(line1: tuple[Point, Point], line2: tuple[Point, Point]):
        p1, p2 = line1
        p3, p4 = line2

        denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        if denom == 0:
            print("parallel lines")
            return None

        px = (
            (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x)
            - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
        ) / denom
        py = (
            (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y)
            - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)
        ) / denom
        return (px, py)

    ############################################################################################################################################
    ############################################################# Line #########################################################################
    ############################################################################################################################################

    class Line:
        def __init__(self, p1: Point, p2: Point):
            self.p1 = p1
            self.p2 = p2
            self.m, self.b = self._calculate_parameters()
            self.mid_point = self._find_mid_point()
            self.length = self.p1.distance(self.p2)
            self.angle = 0 if not self.m else math.degrees(math.atan(self.m))
            return

        def y(self, x):
            return self.m * x + self.b if self.m is not None else self.b

        def _calculate_parameters(self):
            x1 = self.p1.x
            y1 = self.p1.y
            x2 = self.p2.x
            y2 = self.p2.y

            if x1 == x2:
                # vertical line
                return None, x1

            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            return m, b

        def _find_mid_point(self):
            x1 = self.p1.x
            x2 = self.p2.x
            if x1 == x2:
                y1 = self.p1.y
                y2 = self.p2.y
                mid_y = abs(y2 - y1) / 2 + min(y1, y2)
                return Point(x1, mid_y)
            else:
                mid_x = abs(x2 - x1) / 2 + min(x1, x2)
                mid_y = self.y(mid_x)
                return Point(mid_x, mid_y)

        def draw(self):
            plt.plot(self.p1.x, self.p1.y, "o", c="blue", zorder=100)
            plt.plot(self.p2.x, self.p2.y, "o", c="blue", zorder=100)
            plt.plot(self.mid_point.x, self.mid_point.y, "o", c="red", zorder=100)

            # to draw the edge
            plt.plot(
                (self.p1.x, self.p2.x), (self.p1.y, self.p2.y), c="blue", zorder=99
            )

            plt.show()
            return

    ############################################################################################################################################
    ######################################################### Kitchen Sync #####################################################################
    ############################################################################################################################################

    class Kitchen_Sync:
        def __init__(self, points):
            self.points = points
            self.n = len(self.points)
            self.height = 0
            self.width = 0
            self.angle = 0
            self.center = (0, 0)
            self.designs = []

            self._calculate_parameters()
            return

        def _calculate_parameters(self):
            if self.n != 4:
                print("Error: Sync must be a quadrilateral (4 Points) Shape")
                return

            side_A1 = Designs.Line(self.points[0], self.points[1])
            side_B1 = Designs.Line(self.points[1], self.points[2])
            side_A2 = Designs.Line(self.points[2], self.points[3])
            side_B2 = Designs.Line(self.points[3], self.points[0])

            print(abs(self.points[0].x - self.points[1].x))
            print(abs(self.points[0].y - self.points[1].y))
            if self.points[0].distance(self.points[1]) < self.points[1].distance(
                self.points[2]
            ):
                self.width = (
                    side_A1.mid_point.distance(side_A2.mid_point)
                    / 2
                    * Sync_SHRINK_FACTOR
                )
                self.height = (
                    side_B1.mid_point.distance(side_B2.mid_point)
                    / 2
                    * Sync_SHRINK_FACTOR
                )
                print("@@@@@@@@@ 1")
            else:
                self.height = (
                    side_A1.mid_point.distance(side_A2.mid_point)
                    / 2
                    * Sync_SHRINK_FACTOR
                )
                self.width = (
                    side_B1.mid_point.distance(side_B2.mid_point)
                    / 2
                    * Sync_SHRINK_FACTOR
                )
                print("@@@@@@@@@ 2")

            L1, L2 = (
                (side_A1, side_A2)
                if side_A1.length + side_A2.length > side_B1.length + side_B2.length
                else (side_B1, side_B2)
            )
            self.angle = min(L1.angle, L2.angle)

            # x_center, y_center = Designs._get_intersection((points[0],points[2]), (points[1],points[3]))
            x_center, y_center = Designs._get_intersection(
                (side_A1.mid_point, side_A2.mid_point),
                (side_B1.mid_point, side_B2.mid_point),
            )
            self.center = Point(x_center, y_center)

            ellipse = Ellipse(
                xy=(self.center.x, self.center.y),
                width=self.width,
                height=self.height,
                angle=self.angle,  # degrees
                fill=False,
                linewidth=LINE_WIDTH,
                color="blue",
            )
            self.designs.append(ellipse)
            return

        def show(self):
            fig, ax = plt.subplots()

            # draw the outside shape
            for i, point in enumerate(self.points):
                plt.plot(point.x, point.y, "o", c="blue", zorder=100)
                next_point = points[(i + 1) % self.n]
                plt.plot(
                    (point.x, next_point.x),
                    (point.y, next_point.y),
                    c="blue",
                    zorder=99,
                )

            # draw the center point
            plt.plot(self.center.x, self.center.y, "o", c="red", zorder=100)

            # draw the inner shape
            ax.add_patch(self.ellipse)

            plt.show()
            return

    ############################################################################################################################################
    ######################################################### Kitchen Gas ######################################################################
    ############################################################################################################################################

    class Kitchen_Gas:
        def __init__(self, points, num_of_heads=4):
            self.points = points
            self.n = len(self.points)
            self.num_of_heads = num_of_heads
            self.height = 0
            self.width = 0
            self.angle = 0
            self.centers = []
            self.designs = []

            self._calculate_parameters()
            return

        def _calculate_parameters(self):
            if self.n != 4:
                print("Error: Gas must be a quadrilateral (4 Points) Shape")
                return

            side_A1 = Designs.Line(self.points[0], self.points[1])
            side_A1_i = Designs.Line(side_A1.p1, side_A1.mid_point)
            side_A1_ii = Designs.Line(side_A1.mid_point, side_A1.p2)

            side_B1 = Designs.Line(self.points[1], self.points[2])
            side_B1_i = Designs.Line(side_B1.p1, side_B1.mid_point)
            side_B1_ii = Designs.Line(side_B1.mid_point, side_B1.p2)

            side_A2 = Designs.Line(self.points[2], self.points[3])
            side_A2_i = Designs.Line(side_A2.p1, side_A2.mid_point)
            side_A2_ii = Designs.Line(side_A2.mid_point, side_A2.p2)

            side_B2 = Designs.Line(self.points[3], self.points[0])
            side_B2_i = Designs.Line(side_B2.p1, side_B2.mid_point)
            side_B2_ii = Designs.Line(side_B2.mid_point, side_B2.p2)

            self.radius = (
                min(
                    min(side_A1.length, side_A2.length),
                    min(side_B1.length, side_B2.length),
                )
                / 4
                * GAS_SHRINK_FACTOR
            )

            mid_lines_1 = [
                (side_A1_i.mid_point, side_A2_ii.mid_point),
                (side_A1_ii.mid_point, side_A2_i.mid_point),
                (side_A1_i.mid_point, side_A2_ii.mid_point),
                (side_A1_ii.mid_point, side_A2_i.mid_point),
            ]
            mid_lines_2 = [
                (side_B1_i.mid_point, side_B2_ii.mid_point),
                (side_B1_i.mid_point, side_B2_ii.mid_point),
                (side_B1_ii.mid_point, side_B2_i.mid_point),
                (side_B1_ii.mid_point, side_B2_i.mid_point),
            ]

            for i in range(self.num_of_heads):
                x_center, y_center = Designs._get_intersection(
                    mid_lines_1[i], mid_lines_2[i]
                )
                center = Point(x_center, y_center)
                self.centers.append(center)

                circle = Circle(
                    (center.x, center.y),
                    self.radius,
                    fill=False,
                    linewidth=LINE_WIDTH,
                    color="blue",
                )
                self.designs.append(circle)

            return

        def show(self):
            fig, ax = plt.subplots()

            # draw the outside shape
            for i, point in enumerate(self.points):
                plt.plot(point.x, point.y, "o", c="blue", zorder=100)
                next_point = points[(i + 1) % self.n]
                plt.plot(
                    (point.x, next_point.x),
                    (point.y, next_point.y),
                    c="blue",
                    zorder=99,
                )

            # draw the center points
            for center in self.centers:
                plt.plot(center.x, center.y, "o", c="red", zorder=100)

            # draw the inner shapes
            for circle in self.designs:
                ax.add_patch(circle)

            plt.show()
            return

    ############################################################################################################################################
    ######################################################### Test #############################################################################
    ############################################################################################################################################


# points = [Point(10,30),Point(160,50),Point(190,30),Point(30,10)]
# points = [Point(0,0),Point(0,10),Point(10,10),Point(10,0)]
# d = Designs()
# sync = Designs.Kitchen_Gas(points)
# sync.show()
