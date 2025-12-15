import sys
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List

from scripts.shift_script_v6.point import Point
from scripts.shift_script_v6.shape import Shape
from scripts.shift_script_v6.config import (
    colors_categories_dict,
    aci_color_code_dict,
    aci_color_code_inverse_dict,
    smartscale_3d,
)
from scripts.shift_script_v6.designs import Designs


X = 0
Y = 1
valide_entity_types = ["LWPOLYLINE", "POINT", "LINE"]

### added in v6 to ignore sink, gas and electric as well as regular ignores
ignore_codes = [3, 6, 7, 8, 9]
design_categories = {
    "sync": Designs.Kitchen_Sync,
    "gas": Designs.Kitchen_Gas,
    "electric": None,
}
design_parts = []
###

colors_shift_dict = {
    "purple": 0,
    "darkgray": 0,
    "orange": 0,
    "green": 0,
    "red": 0,
    "blue": 0,
    "gray": 0,
    "yellow": 0,
}

outline_colors = []
inside_colors = []
ignore_colors = []
remove_colors = []
keep_point_colors = []

############################################################################################################################################
####################################################### Utilities ##########################################################################
############################################################################################################################################


def _print_logo():
    for line in smartscale_3d:
        print(line)
    return


def _print_banner(text):
    text = " " + text + " "
    min_len = 111
    min_side = 5
    N = len(text)

    side = int(max(min_side, (min_len - N) / 2))
    print("")
    print("#" * int(2 * side + N))
    print("#" * side + text + "#" * side)
    print("#" * int(2 * side + N))
    return


def _load_data_file():
    # _print_banner("Load Data File")
    args = sys.argv
    if len(args) < 2:
        print("Error: please provide the json file path")
        sys.exit(1)
    filename = args[1]
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        # print("Data file loaded successfully")
        return data, filename
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        sys.exit(1)
    return


############################################################################################################################################
##################################################### Data Parsing #########################################################################
############################################################################################################################################


# divides the colors into 4 lists according to the categories code from shifts
# and fills colors_shift_dict with the shift amount for each color
def _parse_colors_list(shifts):
    _print_banner("Colors & Shitfs")
    categories = ["outline", "inside", "ignore", "remove", "keep_point"]
    lists = [
        outline_colors,
        inside_colors,
        ignore_colors,
        remove_colors,
        keep_point_colors,
    ]

    for line in shifts:
        color, shitf, code = line
        colors_shift_dict[aci_color_code_dict[color]] = shitf
        ### added in v6 to support sink, gas and electric ignore
        list_type = 2 if code in ignore_codes else code - 1
        ###
        lists[list_type].append(color)

    for i in range(len(lists)):
        print(f"\n{categories[i]} colors list:")
        for color in lists[i]:
            shitf = colors_shift_dict[aci_color_code_dict[color]]
            print(
                f"{aci_color_code_dict[color]} ({("+" if shitf > 0 else "") + str(shitf)})"
            )

    return


def _parse_line(line):
    if line["entity_type"] == "LWPOLYLINE":
        vertices = line["vertices"]
    elif line["entity_type"] == "POINT":
        vertices = [line]
    elif line["entity_type"] == "LINE":
        vertices = [line["start"], line["end"]]
    else:
        vertices = []
    return vertices


def parse_data(data, to_print=False):
    _print_banner("Parse Data")
    outline_points = []
    inside_points = []
    ignore_points = []
    counter = 0
    design_counter = 0  # to keep track of sync, gas, electric...
    # if "coordinates" in data:
    for line in data:
        if "entity_type" in line and "layer" in line and "aci" in line:
            if (
                line["entity_type"].upper() in valide_entity_types
                and line["layer"] != "Frames"
            ):

                ### added in v5 to only keep points that in color code "keep_point" category
                if (line["entity_type"] == "POINT") and (
                    line["aci"] not in keep_point_colors
                ):
                    continue
                ###

                for design_category in design_categories.keys():
                    if design_category in line["layer"]:
                        design_parts.append((design_counter, design_category))

                vertices = _parse_line(line)
                to_incease_counter = (
                    True
                    if line["aci"] in outline_colors or line["aci"] in inside_colors
                    else False
                )

                if to_print:
                    print(
                        "###############################################################################################"
                    )
                    print(line["entity_type"])
                    print(vertices)

                points = []
                for point in vertices:
                    if to_print:
                        print(point)

                    if "x" in point and "y" in point:
                        # points.append(Point(round(point["x"]), round(point["y"]), info=[counter], color=line["aci"]))
                        points.append(
                            Point(
                                point["x"],
                                point["y"],
                                info=[counter],
                                color=line["aci"],
                            )
                        )
                        if to_print:
                            print(f"created {points[-1]}")
                        if to_incease_counter:
                            counter += 1

                if line["aci"] in outline_colors:
                    outline_points.append(points)
                elif line["aci"] in inside_colors:
                    inside_points.append(points)
                elif line["aci"] in ignore_colors:
                    ignore_points.append(points)
                    design_counter += 1
                ### added in v5 to only keep points that in color code "keep_point" category
                elif (
                    line["aci"] in keep_point_colors and line["entity_type"] == "POINT"
                ):
                    outline_points.append(points)
                ###

    all_points = [
        ("outline_points", outline_points),
        ("inside_points", inside_points),
        ("ignore_points", ignore_points),
    ]
    for points in all_points:
        print(f"\n++++++++++ {points[0]} ++++++++++")
        for i, points_group in enumerate(points[1]):
            print(f"group {i+1}:")
            for point in points_group:
                print(point)

    return outline_points, inside_points, ignore_points


def parse_simple_data(data):
    all_points = []
    for point in data:
        all_points.append(Point(point["X"], point["Y"], info=[""], color=12))

    s = Shape(all_points)
    s.show()
    return all_points, []


def view(points, draw_edges=True):
    n = len(points)
    all_points = []
    for group in points:
        all_points += group

    for i, point in enumerate(all_points):
        c = aci_color_code_dict[point._color_code]
        plt.plot(point.x, point.y, "o", c=c, zorder=100)
        plt.text(
            point.x + 5,
            point.y,
            str(i % n),
            fontsize=12,
            ha="left",
            va="bottom",
            color=c,
        )

        if draw_edges:
            # to draw the edge
            next_point = all_points[(i + 1) % n]
            plt.plot(
                (point.x, next_point.x),
                (point.y, next_point.y),
                c=aci_color_code_dict[next_point._color_code],
                zorder=99,
            )

    plt.show()
    return


############################################################################################################################################
###################################################### Smartscale ##########################################################################
############################################################################################################################################


def draw_shapes(shapes, designs, title="shapes", to_export=False):
    fig, ax = plt.subplots()
    for shape in shapes:
        points, color = shape
        n = len(points)
        for i in range(n):
            point = points[i]
            c = aci_color_code_dict[point._color_code] if color is None else color
            plt.plot(point.x, point.y, "o", c=c, zorder=100)
            if color is None:
                plt.text(
                    point.x + 5,
                    point.y,
                    str((i + 1) % n),
                    fontsize=12,
                    ha="left",
                    va="bottom",
                    color=c,
                )

            # to draw the edge
            next_point = points[(i + 1) % n]
            c = aci_color_code_dict[next_point._color_code] if color is None else color
            linestyle = "-" if color is None else "--"
            linewidth = 1 if color is None else 1
            alpha = 1 if color is None else 1
            plt.plot(
                (point.x, next_point.x),
                (point.y, next_point.y),
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                c=c,
                zorder=99,
            )

    for design in designs:
        ax.add_patch(design)

    if to_export:
        plt.savefig(f"{title}.png")
    else:
        plt.show()
    return


def _extract_piece_points(source, index, destination, to_reverse):
    if source and source[index]:
        piece = source.pop(index)
        if to_reverse:
            piece.reverse()

        # merge the two similar points' info
        if destination:
            common_point = piece.pop(0)
            destination[-1]._info += common_point._info

        # copy all remaining points in order
        for point in piece:
            destination.append(point)
    return


def match_points(all_points):
    if not all_points:
        return []
    _print_banner("Match Points")
    print(all_points)
    result = []
    _extract_piece_points(
        source=all_points, index=0, destination=result, to_reverse=False
    )
    print(
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    )
    print(result)

    had_match = True
    while all_points and had_match:
        last_point = result[
            -1
        ]  # search for new match with the last point of last matched piece
        had_match = False  # to ensure ach point find a match in each iteration
        for i, piece in enumerate(all_points):
            if piece[0] == last_point:
                _extract_piece_points(
                    source=all_points, index=i, destination=result, to_reverse=False
                )
                had_match = True
            elif piece[-1] == last_point:
                _extract_piece_points(
                    source=all_points, index=i, destination=result, to_reverse=True
                )
                had_match = True

    if len(all_points) != 0 or result[0] != result[-1]:
        print("Error: not a closed shape")
        raise RuntimeError("Error: not a closed shape")
        # sys.exit(1)

    last_point = result.pop(-1)
    result[0]._info += last_point._info
    result[0]._color_code = last_point._color_code
    return result


def _get_intersection_point(line1: tuple[Point, Point], line2: tuple[Point, Point]):
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


def _create_new_shape(shape, index, new_point1, new_point2):
    n = shape.n
    i1 = index
    i2 = (index + 1) % n

    # get the original points' info
    new_point1._info = shape.points[i1]._info
    new_point2._info = shape.points[i2]._info

    new_point1._color_code = shape.points[i1]._color_code
    new_point2._color_code = shape.points[i2]._color_code

    # create a new shape with the new points
    new_shape = shape.mcopy()
    new_shape.change_point(index=i1, new_point=new_point1)
    new_shape.change_point(index=i2, new_point=new_point2)
    return new_shape


def move_edge(shape, p1_index, p2_index, delta):
    points = shape.points
    abs_delta = abs(delta)
    n = shape.n

    p1 = points[p1_index % n]
    p2 = points[p2_index % n]

    dx, dy = p2.x - p1.x, p2.y - p1.y
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("not an edge")

    # positive shape option
    positive_normal = Point(-dy / length, dx / length)
    p1_pos = p1 + positive_normal * abs_delta
    p2_pos = p2 + positive_normal * abs_delta
    positive_shape = _create_new_shape(
        shape=shape, index=p1_index, new_point1=p1_pos, new_point2=p2_pos
    )

    # negative shape option
    negative_normal = Point(dy / length, -dx / length)
    p1_neg = p1 + negative_normal * abs_delta
    p2_neg = p2 + negative_normal * abs_delta
    negative_shape = _create_new_shape(
        shape=shape, index=p1_index, new_point1=p1_neg, new_point2=p2_neg
    )

    if delta >= 0:
        return (
            (p1_pos, p2_pos)
            if positive_shape.area > negative_shape.area
            else (p1_neg, p2_neg)
        )
    else:
        return (
            (p1_pos, p2_pos)
            if positive_shape.area < negative_shape.area
            else (p1_neg, p2_neg)
        )


def applay_edges_movements(shape, colors_shift_dict):
    edges_after_moving = []
    for i in range(shape.n):
        # edge color is the secound point's color
        j = (i + 1) % shape.n
        color_code = shape.points[j]._color_code
        color = aci_color_code_dict[color_code]

        # get the edge's shift according to it's color
        shift = colors_shift_dict[color]

        if shift != 0:
            # applay the shift on the edge
            print(f"moving {color} Edge({i},{i+1}) by {shift}")
            new_edge = move_edge(shape, i, (i + 1), shift)
            edges_after_moving.append(new_edge)
        else:
            # save the edge without change
            edges_after_moving.append((shape.points[i], shape.points[j]))

    print("\nedges_after_moving:")
    for e in range(len(edges_after_moving)):
        print(f"Edge {e} : {edges_after_moving[e]}")

    return edges_after_moving


def connect_edges(edges):
    n = len(edges)
    points = []
    print("\nconnecting the new edges:")
    for i in range(n):
        j = (i + 1) % n
        intersection_point = _get_intersection_point(edges[i], edges[j])
        print(f"intersection_point {i},{j} : {intersection_point}")
        point = Point(intersection_point[X], intersection_point[Y])
        points.append(point)

    return Shape(points)


def smartscale(shape, shifts):
    _print_banner("Moving Edges")
    edges = applay_edges_movements(shape, shifts)
    new_shape = connect_edges(edges)

    # copy the original Shape's info into the new Shape
    for i in range(shape.n):
        j = (i - 1) % shape.n
        new_shape.points[j]._info = shape.points[i]._info
        new_shape.points[j]._color_code = shape.points[i]._color_code

    return new_shape


############################################################################################################################################
###################################################### Write Back ##########################################################################
############################################################################################################################################


def _create_data_sequence(points):
    max_index = 0
    for point in points:
        max_index = max(max(point._info), max_index)

    sequence = [0 for _ in range(max_index + 1)]
    for point in points:
        for index in point._info:
            sequence[index] = (point.x, point.y)

    return sequence


def _update_data(data, sequence):
    _print_banner("Write Back The Updated Data")
    counter = 0

    # if "coordinates" in data:
    for line in data:
        if "entity_type" in line and "layer" in line and "aci" in line:
            if (
                line["entity_type"].upper() in valide_entity_types
                and line["layer"] != "Frames"
            ):

                ### added in v5 to only keep points that in color code "keep_point" category
                if (line["entity_type"] == "POINT") and (
                    line["aci"] not in keep_point_colors
                ):
                    continue
                ###

                vertices = _parse_line(line)
                for point in vertices:
                    if (
                        "x" in point
                        and "y" in point
                        and (
                            line["aci"] in outline_colors
                            or line["aci"] in inside_colors
                        )
                    ):
                        if counter < len(sequence):
                            point["x"] = sequence[counter][X]
                            point["y"] = sequence[counter][Y]
                            counter += 1
                        else:
                            print("Error: too many points to write back")
                            raise RuntimeError("Error: too many points to write back")
                            # sys.exit(1)
    print(
        "\n" + "All Points Updated Successfully!"
        if counter == len(sequence)
        else "Error: did not write all points back"
    )
    return data


### use in case of outlines only ###
def write_back(path, shape):
    # read data from json file
    with open(path, "r") as f:
        data = json.load(f)

    # update the data according to the given shape
    sequence = _create_data_sequence(shape.points)
    _update_data(data, sequence)

    # write the new data back to the json file
    new_path = path.split(".json")
    name = new_path[0] + "_output.json"
    with open(name, "w") as f:
        json.dump(data, f, indent=2)
    return


############################################################################################################################################
######################################################### MAIN #############################################################################
############################################################################################################################################


def main(data, shifts):
    _print_logo()

    # save the info in colors_shift_dict and the 4 color categories lists
    _parse_colors_list(shifts)

    # split the points from the data by color category
    outline_points, inside_points, ignore_points = parse_data(data)
    # view(outline_points)#, draw_edges=False)

    # create the outline shape
    points = match_points(outline_points)
    shape = Shape(points)
    shape.show()

    # create the inner shape (if exists)
    print(f"\ninside_shape {inside_points}")
    inside_shape = None
    if inside_points:
        inside_shape = Shape(inside_points[0])
        print(f"inside_shape {inside_shape.points}")
        inside_shape.show()

    # applay the shifts on the outline shape
    new_shape = smartscale(shape, colors_shift_dict)

    # create the sync, gas and electric designs
    all_designs = []
    for design_part in design_parts:
        index, design_type = design_part
        design_obj = design_categories[design_type](ignore_points[index])
        all_designs += design_obj.designs

    # draw the outlines, inner points and extras
    extras = [(e, None) for e in ignore_points]
    inside_shape_points = inside_shape.points if inside_shape else []
    draw_shapes(
        [(shape.points, "black"), (new_shape.points, None), (inside_shape_points, None)]
        + extras,
        all_designs,
        "test_100",
    )

    # update the original json file data
    sequence = _create_data_sequence(new_shape.points + inside_shape_points)
    updated_data = _update_data(data, sequence)
    cleaned = [{k: v for k, v in obj.items() if v is not None} for obj in updated_data]
    return cleaned


############################################################################################################################################
######################################################### Test #############################################################################
############################################################################################################################################

# if __name__ == "__main__":
#     data, path = _load_data_file()
#     #             pink      white   darkgray    red      orange      brown      yellow     green      blue       purple       gray
#     dshifts = [(6, 30, 1), (7,0,4), (8,0,4), (12,-3,1), (30,-2,1), (34,-15,7), (40,0,3), (72,40,1), (152,0,6), (202, 0, 1), (253,0,3)]
#     # dshifts = [(6, 30, 1), (7,0,4), (8,0,4), (12,-3,1), (30,-2,1), (34,-15,2), (40,0,3), (72,40,1), (152,0,3), (202, 0, 1), (253,0,3)]
#     updated_data = smartscale_main(data, dshifts)
#     sys.exit(0)
