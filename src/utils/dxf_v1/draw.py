import os
import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique
import math

def aci_to_rgb(aci_color):
    if not aci_color or aci_color < 1:
        return (0, 0, 0)
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)

def line_length(start, end):
    return math.sqrt((end['x'] - start['x'])**2 + (end['y'] - start['y'])**2)

def entity_offset(ent1, ent2):
    mid1_x = (ent1['start']['x'] + ent1['end']['x']) / 2 if ent1.get('start') and ent1.get('end') else 0
    mid1_y = (ent1['start']['y'] + ent1['end']['y']) / 2 if ent1.get('start') and ent1.get('end') else 0
    mid2_x = (ent2['start']['x'] + ent2['end']['x']) / 2 if ent2.get('start') and ent2.get('end') else 0
    mid2_y = (ent2['start']['y'] + ent2['end']['y']) / 2 if ent2.get('start') and ent2.get('end') else 0
    return math.sqrt((mid2_x - mid1_x)**2 + (mid2_y - mid1_y)**2)

def draw_entities(
    entities,
    entities2=None,
    width=20, height=16, dpi=200,
    file_path=None,
    show_length=True,
    round_lengths=True,
    length_fontsize=14   # <-- new parameter for bigger text
):
    os.makedirs("./tmp", exist_ok=True)
    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".png"

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_aspect('equal')
    ax.grid(True)

    grouped1 = defaultdict(list)
    grouped2 = defaultdict(list)

    for ent in entities:
        grouped1[ent.get("entity_type")].append(ent)
    if entities2:
        for ent in entities2:
            grouped2[ent.get("entity_type")].append(ent)

    # Draw POINT
    for pt in grouped1.get("POINT", []):
        ax.scatter(pt.get('x',0), pt.get('y',0), color=aci_to_rgb(pt.get('aci')), s=30)
    if entities2:
        for pt in grouped2.get("POINT", []):
            ax.scatter(pt.get('x',0), pt.get('y',0), color='black', s=30)

    # Draw LINE
    line2_list = grouped2.get("LINE", []) if entities2 else []
    for i, ln in enumerate(grouped1.get("LINE", [])):
        start, end = ln.get("start"), ln.get("end")
        if start and end:
            ax.plot([start['x'], end['x']], [start['y'], end['y']], color=aci_to_rgb(ln.get("aci")), linestyle='-')
            if show_length:
                length = line_length(start, end)
                offset_text = ""
                if entities2 and i < len(line2_list):
                    offset = entity_offset(ln, line2_list[i])
                    offset_text = f" ({round(offset) if round_lengths else offset})"
                mid_x, mid_y = (start['x']+end['x'])/2, (start['y']+end['y'])/2
                length_text = round(length) if round_lengths else length
                ax.text(mid_x, mid_y+0.1, f"{length_text}{offset_text}", color='black', 
                        fontsize=length_fontsize, ha='center', va='bottom', backgroundcolor='white')

    # Draw LWPOLYLINE
    lw2_list = grouped2.get("LWPOLYLINE", []) if entities2 else []
    for i, poly in enumerate(grouped1.get("LWPOLYLINE", [])):
        pts = poly.get("vertices", [])
        if not pts:
            continue
        if poly.get("closed"):
            pts = pts + [pts[0]]
        for j in range(len(pts)-1):
            x1, y1 = pts[j]['x'], pts[j]['y']
            x2, y2 = pts[j+1]['x'], pts[j+1]['y']
            ax.plot([x1,x2],[y1,y2], color=aci_to_rgb(poly.get("aci")))
            if show_length:
                length = line_length(pts[j], pts[j+1])
                offset_text = ""
                if entities2 and i < len(lw2_list):
                    pts2 = lw2_list[i].get("vertices", [])
                    if lw2_list[i].get("closed") and pts2:
                        pts2 = pts2 + [pts2[0]]
                    if j < len(pts2):
                        offset = line_length(pts[j], pts2[j])
                        offset_text = f" ({round(offset) if round_lengths else offset})"
                mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                length_text = round(length) if round_lengths else length
                ax.text(mid_x, mid_y+0.1, f"{length_text}{offset_text}", color='black', 
                        fontsize=length_fontsize, ha='center', va='bottom', backgroundcolor='white')

    # Draw second entities as black dashed lines
    if entities2:
        for ln in line2_list:
            start, end = ln.get("start"), ln.get("end")
            if start and end:
                ax.plot([start['x'], end['x']], [start['y'], end['y']], color='black', linestyle='--')
        for poly in lw2_list:
            pts = poly.get("vertices", [])
            if not pts:
                continue
            if poly.get("closed"):
                pts = pts + [pts[0]]
            for j in range(len(pts)-1):
                x1, y1 = pts[j]['x'], pts[j]['y']
                x2, y2 = pts[j+1]['x'], pts[j+1]['y']
                ax.plot([x1,x2],[y1,y2], color='black', linestyle='--')

    # Draw TEXT
    for txt in grouped1.get("TEXT", []):
        pos = txt.get('position', {})
        x, y = pos.get('x',0), pos.get('y',0)
        ax.text(x, y, txt.get('text',''), color=aci_to_rgb(txt.get('aci')), fontsize=txt.get('height',12))

    plt.title("Comparison of Entities" + (" with Lengths" if show_length else ""))
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    return file_path
