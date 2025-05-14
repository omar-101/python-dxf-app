import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique as unique_str

class Dxf:
    def __init__(self, file_path):
        self.file_path = file_path
    def extract(self):
        # Load DXF
        doc = ezdxf.readfile(self.file_path)
        msp = doc.modelspace()
        coordinates = []
        for entity in msp:
            entity_type = entity.dxftype()

            if entity_type == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
            for pt in [start, end]:
                x, y, z = pt
                coordinates.append({"entity_type": entity_type, "x":x, "y":y, "z":z})
        return coordinates


        
        

    def draw(self, coordinates):
        file_path = "./tmp/" + unique_str.unique_string(20) + ".png"

        entities = defaultdict(list)
        for coordinate in coordinates:
            entities[coordinate.entity_type].append((coordinate.x, coordinate.y))
            
        # Setup plot
        plt.figure(figsize=(10, 10))
        ax = plt.gca()
        ax.set_aspect('equal')
        plt.title("Entities from DXF")
        plt.grid(True)
        
        for etype, coords in entities.items():
                    # Draw every two points as a line segment
            for i in range(0, len(coords), 2):
                if i + 1 < len(coords):
                    x1, y1 = coords[i]
                    x2, y2 = coords[i + 1]
                    plt.plot([x1, x2], [y1, y2], 'b-', label='LINE' if i == 0 else "")
                    
                    
        handles, labels = plt.gca().get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        plt.legend(unique.values(), unique.keys())
        
        # Save to file
        plt.savefig(file_path)
        plt.show()
        return file_path