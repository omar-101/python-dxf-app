import ezdxf
import matplotlib.pyplot as plt
import math

class Dxf:
    def __init__(self, file_path):
        self.file_path = file_path
        self.coordinates = []
    def extract(self):
        # Load DXF
        doc = ezdxf.readfile(self.file_path)
        msp = doc.modelspace()
                
        for entity in msp:
            entity_type = entity.dxftype()

            if entity_type == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
            for pt in [start, end]:
                x, y, z = pt
                self.coordinates.append({"entity_type": entity_type, "x":x, "y":y, "z":z})
        return self.coordinates


        
        

    def draw(self):
        # Set up Matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        ax.axis('off')  # Optional: hide axes
        
   
        # Extract and draw LINE
        for e in self.coordinates["LINE"]:
            start = e.dxf.start
            end = e.dxf.end
            ax.plot([start.x, end.x], [start.y, end.y], color='black')
            
        # Extract and draw CIRCLE
        for e in self.coordinates["CIRCLE"]:
            center = e.dxf.center
            radius = e.dxf.radius
            circle = plt.Circle((center.x, center.y), radius, fill=False, color='blue')
            ax.add_patch(circle)
            
            
        #Extract and draw ARC
        for e in self.coordinates["ARC"]:
            center = e.dxf.center
            radius = e.dxf.radius
            start_angle = math.radians(e.dxf.start_angle)
            end_angle = math.radians(e.dxf.end_angle)
            theta = [start_angle + t * (end_angle - start_angle) / 100 for t in range(101)]
            x = [center.x + radius * math.cos(t) for t in theta]
            y = [center.y + radius * math.sin(t) for t in theta]
            ax.plot(x, y, color='green')
            
            
        # Extract and draw LWPOLYLINE
        for e in self.coordinates["LWPOLYLINE"]:
            points = e.get_points("xy")
            x, y = zip(*points)
            ax.plot(x, y, color='red')
            
        # Extract and draw POINT
        for e in self.coordinates["POINTS"]:
            pt = e.dxf.location
            print(pt)
            ax.plot(pt.x, pt.y, 'ko', markersize=3)  # Black dot

            
        
        plt.savefig("extracted_geometry.png", dpi=300, bbox_inches="tight", pad_inches=0)
        plt.close()
  