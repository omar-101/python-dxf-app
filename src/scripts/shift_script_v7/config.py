colors_categories_dict = {
    1: "outline",
    2: "inside",
    3: "ignore",
    4: "remove",
    5: "keep_point",
    6: "sink",
    7: "gas",
    8: "electric_sq",
    9: "electric_cr",
}

aci_color_code_dict = {
    6   : "magenta",
    7   : "white",
    202 : "purple",
    8   : "darkgray",
    30  : "orange",
    34  : "brown", # inside
    72  : "green",
    12  : "red",
    152 : "blue",
    253 : "gray",
    40  : "yellow",
    0   : "black" # for testing
}

aci_color_code_inverse_dict = {
    "magenta"  : 6,
    "white"    : 7,
    "purple"   : 202,
    "darkgray" : 8,
    "orange"   : 30,
    "brown"    : 34,
    "green"    : 72,
    "red"      : 12,
    "blue"     : 152,
    "gray"     : 253,
    "yellow"   : 40,
}

categories_to_code_dict = {
    "outline": 1,
    "inside": 2,
    "ignore": 3,
    "remove": 4,
    "keep_point" : 5,
    "sink": 6,
    "gas": 7,
    "electric_sq" : 8,
    "electric_cr": 9,
}

smartscale_3d = [
"  ______                              _____    _________    ______     _____                _         _______ ",
" / ____ \  |¯¯\    /¯¯|      /\      |  __ \  |___   ___|  / ____ \   / ____|      /\      | |       |  _____|",
"| (____    |   \  /   |     /  \     | |__) |     | |     | (____    | |          /  \     | |       | |____  ",
" \____ \   | |\ \/ /| |    / /\ \    |  _  /      | |      \____ \   | |         / /\ \    | |       |  ____| ",
" _____) |  | | \__/ | |   / ____ \   | | \ \      | |      _____) |  | |____    / ____ \   | |_____  | |_____ ",
"|______/   |_|      |_|  /_/    \_\  |_|  \_\     |_|     |______/    \_____|  /_/    \_\  |_______| |_______|",
]
