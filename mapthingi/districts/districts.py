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
    xOverlap = 0
    yOverlap = 0
    xInclude = 0 #1 if poly1 includes poly2, -1 if poly2 includes poly1
    yInclude = 0 #1 if poly1 includes poly2, -1 if poly2 includes poly1
    if poly1.edges[0]<poly2.edges[0] and poly2.edges[0]<poly1.edges[1]:
        xOverlap = 1
        if poly2.edges[1]<poly1.edges[1]:
                xInclude = 1
    if poly2.edges[0]<poly1.edges[0] and poly1.edges[0]<poly2.edges[1]:
        xOverlap = 1
        if poly1.edges[1]<poly2.edges[1]:
                xInclude = -1                
    if poly1.edges[2]<poly2.edges[2] and poly2.edges[2]<poly1.edges[3]:
        yOverlap = 1
        if poly2.edges[3]<poly1.edges[3]:
                yInclude = 1
    if poly2.edges[2]<poly1.edges[2] and poly1.edges[2]<poly2.edges[3]:
        yOverlap = 1
        if poly1.edges[3]<poly2.edges[3]:
                yInclude = -1     

    return [xOverlap,yOverlap,xInclude,yInclude]
    

class Polygon:

    def __init__(self,points):
        self.points = points
        self.edges = []
        self.center = [0,0,0]

    def addVertex(self, vertex):
        if len(vertex)==2:
            vertex.append(0)
        if len(vertex)>3 or len(vertex)<2:
            raise ValueError('unvalid vertex')
        self.points.append(vertex)

    def calculateEdges(self):
        x_values = self._getX()
        y_values = self._getY()
        self.center = [sum(x_values)/len(x_values),sum(y_values)/len(y_values),0]
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
        for i in range(0,len(self.points)):
            self.points[i][0]+=vector[0]
            self.points[i][1]+=vector[1]
            self.points[i][2]+=vector[2]

    def addBorder(self,width):
        self.translate([-self.center[0],-self.center[1],0])
        for i in range(0,len(self.points)):
            pointlen = length(self.points[i])
            self.points[i][0]*=(pointlen-width)/pointlen
            self.points[i][1]*=(pointlen-width)/pointlen
        self.translate(self.center)

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
        print "write district: %s" % self.name
        numpolygons = len(self.polygons)
        print "%d polygons" % numpolygons
        if(numpolygons==2):
            rel=relationship(self.polygons[0],self.polygons[1])
            if(rel[2]==rel[3]):
                if(rel[3]==1):
                    print "%d points" % len(self.polygons[0].points)
                    Writer.extrude(self.polygons[0].points, self.height)
                    print "%d points" % len(self.polygons[1].points) 
                    Writer.extrude(self.polygons[1].points.reverse(), self.height)
                else :
                    print "%d points" % len(self.polygons[0].points)
                    Writer.extrude(self.polygons[0].points.reverse(), self.height)
                    print "%d points" % len(self.polygons[1].points) 
                    Writer.extrude(self.polygons[1], self.height)                   
        elif(numpolygons>2) :
            rel=[]
            for i in range(0,numpolygons):
                for j in range(i+1,numpolygons):
                    rel=relationship(self.polygons[i],self.polygons[j])
                    if (rel[2] == -1) and (rel[3] == -1):
                        Writer.extrude(self.polygons[i].points.reverse(), self.height)
                        print "%d points" % len(self.polygons[i].points) 
                        break
                    if (j== numpolygons-1):
                        Writer.extrude(self.polygons[i].points, self.height)
                        print "%d points" % len(self.polygons[i].points) 
        else :
            Writer.extrude(self.polygons[0].points, self.height)
            print "%d points" % len(self.polygons[0].points) 
        

    def simplify(self,freq):
        for polygon in self.polygons:
            polygon.simplify(freq)

    def addBorder(self,width):
        numpolygons = len(self.polygons)
        if(numpolygons==2):
            rel=relationship(self.polygons[0],self.polygons[1])
            if(rel[2]==rel[3]):
                if(rel[3]==1):
                    self.polygons[0].addBorder(width)
                    self.polygons[1].addBorder(-width)
                else :
                    self.polygons[0].addBorder(-width)
                    self.polygons[1].addBorder(width)                       
        elif(numpolygons>2) :
            rel=[]
            for i in range(0,numpolygons):
                for j in range(i+1,numpolygons):
                    rel=relationship(self.polygons[i],self.polygons[j])
                    if (rel[2] == -1) and (rel[3] == -1):
                        self.polygons[i].addBorder(-width)
                        break
                    if (j== numpolygons-1):
                        self.polygons[i].addBorder(width)
        else :
            for polygon in self.polygons:
                polygon.addBorder(width)


def importDistricts(folder, groundheight = 0):
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
        district = District(name=first_line, height=10+random.randint(0,5))
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
                    district.addVertex([float(split_line[0].strip())*10,
                                        float(split_line[1].strip())*10,
                                        groundheight
                                        ], None);


        print("Number of Vertices: %d" % len(district.polygons[0].points));
        for polygon in district.polygons:
            polygon.calculateEdges()

        districts.append(district)
        fp.close()
        
    return districts


#test code

folder = "../poly"
groundheight=2
districts = importDistricts(folder,groundheight)
freq=400
width=0.5
with open('test.stl', 'wb') as stl:
    writer = STLWriter.STL_Writer(stl)
    count = 0
    xmin=0
    xmax=0
    ymin=0
    ymax=0
    for district in districts:
        #district.simplify(freq)
        #district.addBorder(width)
        #district.write(writer)

        for poly in district.polygons:
            if(poly.edges[0]<xmin):
                xmin=poly.edges[0]
            if(poly.edges[1]>xmax):
                xmax=poly.edges[1]
            if(poly.edges[2]<ymin):
                xmin=poly.edges[2]
            if(poly.edges[3]>ymax):
                xmin=poly.edges[3]
    print "xmin = %f" % xmin
    print "xmax = %f" % xmax
    print "ymin = %f" % ymin
    print "ymax = %f" % ymax
    floor = [[xmin,ymin,0],[xmax,ymin,0],[xmax,ymax,0],[xmin,ymax,0]]
    writer.extrude(floor,groundheight)
    writer.close()
#print "%d districts" % len(districts)
#for district in districts:
#    print "%s" % district.name

