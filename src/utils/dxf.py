import ezdxf
import matplotlib.pyplot as plt
import math

class Dxf:
    def __init__(self, file_path):
        self.file_path = file_path
        self.coordinates = {}
    def extract(self):
        # Load DXF
        doc = ezdxf.readfile(self.file_path)
        msp = doc.modelspace()
        
        self.coordinates["LINE"] = msp.query("LINE")
        self.coordinates["CIRCLE"] = msp.query("CIRCLE")
        self.coordinates["ARC"] = msp.query("ARC")
        self.coordinates["LWPOLYLINE"] = msp.query("LWPOLYLINE")

        
        # Extract and draw LINE
        for e in msp.query("LINE"):
            print(e)
            # start = e.dxf.start
            # end = e.dxf.end
            # ax.plot([start.x, end.x], [start.y, end.y], color='black')

        # Extract and draw CIRCLE
        for e in msp.query("CIRCLE"):
            print(e)
            # center = e.dxf.center
            # radius = e.dxf.radius
            # circle = plt.Circle((center.x, center.y), radius, fill=False, color='blue')
            # ax.add_patch(circle)

        # Extract and draw ARC
        for e in msp.query("ARC"):
            print(e)
            # center = e.dxf.center
            # radius = e.dxf.radius
            # start_angle = math.radians(e.dxf.start_angle)
            # end_angle = math.radians(e.dxf.end_angle)
            # theta = [start_angle + t * (end_angle - start_angle) / 100 for t in range(101)]
            # x = [center.x + radius * math.cos(t) for t in theta]
            # y = [center.y + radius * math.sin(t) for t in theta]
            # ax.plot(x, y, color='green')

        # Extract and draw LWPOLYLINE
        for e in msp.query("LWPOLYLINE"):
            print(e)
            # points = e.get_points("xy")
            # x, y = zip(*points)
            # ax.plot(x, y, color='red')

    def draw(self):
        # Set up Matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        ax.axis('off')  # Optional: hide axes
        
        print(self.coordinates["LINE"])
        for e in self.coordinates["LINE"]:
            start = e.dxf.start
            end = e.dxf.end
            ax.plot([start.x, end.x], [start.y, end.y], color='black')
        plt.savefig("extracted_geometry.png", dpi=300, bbox_inches="tight", pad_inches=0)
        plt.close()
  

# def dfx_extract(file_path: str):
#     # Load DXF
#     doc = ezdxf.readfile(file_path)
#     msp = doc.modelspace()

#     # Set up Matplotlib figure
#     fig, ax = plt.subplots(figsize=(10, 10))
#     ax.set_aspect('equal')
#     ax.axis('off')  # Optional: hide axes

#     # Extract and draw LINE
#     for e in msp.query("LINE"):
#         start = e.dxf.start
#         end = e.dxf.end
#         ax.plot([start.x, end.x], [start.y, end.y], color='black')

#     # Extract and draw CIRCLE
#     for e in msp.query("CIRCLE"):
#         center = e.dxf.center
#         radius = e.dxf.radius
#         circle = plt.Circle((center.x, center.y), radius, fill=False, color='blue')
#         ax.add_patch(circle)

#     # Extract and draw ARC
#     for e in msp.query("ARC"):
#         center = e.dxf.center
#         radius = e.dxf.radius
#         start_angle = math.radians(e.dxf.start_angle)
#         end_angle = math.radians(e.dxf.end_angle)
#         theta = [start_angle + t * (end_angle - start_angle) / 100 for t in range(101)]
#         x = [center.x + radius * math.cos(t) for t in theta]
#         y = [center.y + radius * math.sin(t) for t in theta]
#         ax.plot(x, y, color='green')

#     # Extract and draw LWPOLYLINE
#     for e in msp.query("LWPOLYLINE"):
#         points = e.get_points("xy")
#         x, y = zip(*points)
#         ax.plot(x, y, color='red')

#     # Save the image
#     plt.savefig("extracted_geometry.png", dpi=300, bbox_inches="tight", pad_inches=0)
#     plt.close()