import math
import random
from os import listdir
from os.path import isfile, join
import imp
import re
STLWriter = imp.load_source('STLWriter', '../STLWriter/STLWriter.py')

def length(point):
    l=0
    for p in point:
        l+=p*p
    return math.sqrt(l)

def relationship(poly1,poly2):
    xOverlap = FALSE
    yOverlap = FALSE
    xInclude = 0 #1 if poly1 includes poly2, -1 if poly2 includes poly1
    yInclude = 0 #1 if poly1 includes poly2, -1 if poly2 includes poly1
    if poly1.edges[0]<poly2.edges[0] and poly2.edges[0]<poly1.edges[1]:
        xOverlap = TRUE
        if poly2.edges[1]<poly1.edges[1]:
                xInclude = 1
    if poly2.edges[0]<poly1.edges[0] and poly1.edges[0]<poly2.edges[1]:
        xOverlap = TRUE
        if poly1.edges[1]<poly2.edges[1]:
                xInclude = -1                
    if poly1.edges[2]<poly2.edges[2] and poly2.edges[2]<poly1.edges[3]:
        yOverlap = TRUE
        if poly2.edges[3]<poly1.edges[3]:
                yInclude = 1
    if poly2.edges[2]<poly1.edges[2] and poly1.edges[2]<poly2.edges[3]:
        yOverlap = TRUE
        if poly1.edges[3]<poly2.edges[3]:
                yInclude = -1     

    return [xOverlap,yOverlap,xInclude,yInclude]
    

class Polygon:

    def __init__(self,points):
        self.points = points
        self.edges = []

    def addVertex(self, vertex):
        if len(vertex)==2:
            vertex.append(0)
        if len(vertex)>3 or len(vertex)<2:
            raise ValueError('unvalid vertex')
        self.points.append(vertex)

    def calculateEdges(self):
        x_values = self._getX()
        y_values = self._getY()
        self.edges = [min(x_values),max(x_values),min(y_values),max(y_values)]

    def _getX(self):
        return [point[0] for point in self.points]
    
    def _getY(self):
        return [point[1] for point in self.points]

    def translate(self,vector):
        if len(vector)>3 or len(vector)<2:
             raise ValueError('unvalid translation vector')
        if len(vector)==2:
            vector.append(0)
        translated = []
        for point in self.points:
            translated.append([point[0]+vector[0],point[1]+vector[1],point[2]+vector[2]])
        return translated

    def center(self):
        x_values = self._getX()
        y_values = self._getY()
        if len(x_values)==0 or len(y_values)==0:
             raise ValueError('polygon has no points')            
        return [sum(x_values)/len(x_values),sum(x_values)/len(x_values),0]

    def addBorder(self,width):
        center = self.center()
        self.points = self.translate([-center[0],-center[1],0])
        for i,point in enumerate(self.points):
            pointlen = length(point)
            self.points[i][0]*=(pointlen-width)/pointlen
            self.points[i][1]*=(pointlen-width)/pointlen
        self.translate(center)

    def scale(self,s):
        center = self.center()
        self.points = self.translate([-center[0],-center[1],0])
        for i,point in enumerate(self.points):
            self.points[i][0]*=s
            self.points[i][1]*=s
        self.translate(center)

    def simplify(self,freq):
        #keep only every freq point
        i = 0
        for point in self.points:
            i += 1
            if i == freq :
                i = 0
            else :
                self.points.remove(point)
            

class District:
    """ District, consisting of a name, base polygon, and height
    """

    def __init__(self, name, height=1):
        self.name = name
        self.polygons = []
        self.height = height

    def addPolygon(self):
        self.polygons.append(Polygon([]))

    def removePolygon(self):
        self.polygons.pop()

    def addVertex(self, vertex, polygon_id):
        if polygon_id == None:
            polygon_id = len(self.polygons)-1
        self.polygons[polygon_id].addVertex(vertex)

    def write(self, Writer):
        for polygon in self.polygons:
            Writer.extrude(polygon.points, self.height)

    def simplify(self,freq):
        for polygon in self.polygons:
            polygon.simplify(freq)

    def addBorder(self,width):
         for polygon in self.polygons:
            polygon.addBorder(freq)       


def importDistricts(folder, granularity=1):
    districts = []

    # collect all poly filenames
    files = [
        join(folder,f) for f in listdir(folder) 
            if isfile(join(folder,f))
            and f.endswith(".poly")
    ];

    print("File count: %d" % len(files));

    for h_idx, file_ in enumerate(files):
        fp = open(file_,"r")

        # read name from file's first line
        first_line = next(fp)
        random.seed()
        district = District(name=first_line, height=random.random()*5+5)
        # next(fp)
        
        i = 0

        # split multipolygons
        polygon_end = False

        # scad_fp.write("[")
        # district.addPolygon()

        p = re.compile('[0-9]+')

        print("District's name: %s" % district.name);
        # iterate lines
        for idx, line in enumerate(fp):

            m = p.match(line)
            if m:
                # polygon start
                district.addPolygon()
                print("match: %s" % m.group())

            if line == "END\n":
                # polygon end or file end
                if not polygon_end:
                    print("polygon end")
                    #scad_fp.write("],")
                polygon_end = True
            else:
                polygon_end = False

            # only add if granularity is correct
            #if idx%granularity != 0:
            #    continue

            if line.startswith("   "):
                split_line = line.strip().split("   ");
                if len(split_line) == 2:
                    district.addVertex([float(split_line[0].strip()),
                                        float(split_line[1].strip())
                                        ], None);


        print("Number of Vertices: %d" % len(district.polygons[0].points));
        for polygon in district.polygons:
            polygon.calculateEdges()

        districts.append(district)
        fp.close()
        
    return districts


#test code

folder = "../poly"
districts = importDistricts(folder)
freq=800
width=1
with open('test.stl', 'wb') as stl:
    writer = STLWriter.STL_Writer(stl)
    for district in districts:
        district.simplify(freq)
        district.addBorder(width)
        district.write(writer)
    writer.close()
print "%d districts" % len(districts)
for district in districts:
    print "%s" % district.name

