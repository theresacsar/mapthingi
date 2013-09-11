#binary stl writer
#STL Format description: http://www.ennex.com/~fabbers/StL.asp
#based on http://code.activestate.com/recipes/578246-stl-writer/

import struct

#functions for calculation of the normal vector (right-thumb-rule)
def crossProduct(a, b):
    #calculate cross product of two threedimensional vectors
    if (len(a)!=3) or (len(b)!=3):
        raise ValueError('unvalid value')
    return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]

def diff(v1,v2):
    #substracting one list from another
    if (len(v1)!=3) or (len(v2)!=3):
        raise ValueError('unvalid value')
    return [v1[0]-v2[0],v1[1]-v2[1],v1[2]-v2[2]]

            
def normal(v1,v2,v3):
    #calculate normal vector on triangle spanned by the three vertices
    #tells in which direction the plane looks "right-thumb-rule"
    if (len(v1)!=3) or (len(v2)!=3) or (len(v2)!=3):
        raise ValueError('unvalid value')
    n=crossProduct(diff(v2,v1),diff(v3,v1))
    absolut=0
    for i in n:
        if i>=0:
            absolut+=i
        else:
            absolut-=i
    if absolut == 0:
        print "this should not have happened!"
        return n
    else :
        return [n[0]/absolut,n[1]/absolut,n[2]/absolut]

#simple function to create sets of three vertices
##def triangulate(vertices):
##    print "triangulate!"
##    n=len(vertices)
##    if(n==3):
##        return vertices
##    elif n<3:
##        raise ValueError('not enough vertices')
##    else:
##        #print "facet has %d vertices" % n
##        facets=[]
##        for i in range(0,n-2):
##            facet=[vertices[0],vertices[i+1],vertices[i+2]]
##            facets.append(facet)
##        return facets
##
##def triangulate1(vertices):
##    #print "triangulate!"
##    n=len(vertices)
##    if(n==3):
##        return vertices
##    elif n<3:
##        raise ValueError('not enough vertices')
##    else:
##        #print "facet has %d vertices" % n
##        facets=[]
##        for i in range(0,n-2):
##            #print "i = %d" % i
##            if i == 0:
##                facet=[vertices[0],vertices[1],vertices[2]]
##            else:
##                if ((i % 2)==1) :
##                    facet[1]=facet[0]
##                    facet[0]=vertices[n-(i+1)/2]
##                else :
##                    facet[1]=facet[2]
##                    facet[2]=vertices[2+i/2]
##            facets.append(facet[:])
##            #print '[%s]' % ', '.join(map(str, facet))
##        return facets

def triangulate(poly):
    """
    triangulates poly and returns a list of triangles
    poly: list of points that form an anticlockwise polygon (self-intersecting polygons won't work, results are... undefined)
    """
    triangles = []
    remaining = poly[:]
    # while the poly still needs clipping
    while len(remaining) > 2:
        print("doing %d" % len(remaining))
        # rotate the list:
        # this stops the starting point from getting stale which sometimes a "fan" of polys, which often leads to poor convexisation
        remaining = remaining[1:]+remaining[:1]
        # clip the ear, store it
        ear, remaining = _get_ear(remaining)
        if ear != []:
            triangles.append(ear)
    # return stored triangles
    return triangles

def _get_ear(poly):
    count = len(poly)
    # not even a poly
    if count < 3:
        return [], []
    # only a triangle anyway
    if count == 3:
        return poly, []

    # start checking points
    for i in range(count):
        ia = (i-1) % count
        ib = i
        ic = (i+1) % count
        a = poly[ia]
        b = poly[ib]
        c = poly[ic]
        # is point b an outer corner?
        if _is_corner(a,b,c):
            # are there any other points inside triangle abc?
            valid = True
            for j in range(count):
                if not(j in (ia,ib,ic)):
                    p = poly[j]
                    if _point_in_triangle(p,a,b,c):
                        valid = False
            # if no such point found, abc must be an "ear"
            if valid:
                remaining = []
                for j in range(count):
                    if j != ib:
                        remaining.append(poly[j])
                # return the ear, and what's left of the polygon after the ear is clipped
                return [a,b,c], remaining
            
    # no ear was found, so something is wrong with the given poly (not anticlockwise? self-intersects?)
    return [], []

def _is_corner(a,b,c):
    # returns if point b is an outer corner
    return not(is_clockwise([a,b,c]))


#STL Writer
class STL_Writer:
    def __init__(self, stream):
        self.st = stream
        self.count = 0
        self._write_header()
        
    def close(self):
        self._write_header()

    def _write_header(self):
        self.st.seek(0)
        #format characters: http://docs.python.org/2/library/struct.html
        self.st.write(struct.pack("80sI", b'Python Binary STL Writer', self.count))

    def _write(self, facet):
        self.count += 1
        #print "add facet %d" % self.count
        n=normal(facet[0],facet[1],facet[2])
        data = [
            n[0], n[1], n[2],
            facet[0][0], facet[0][1], facet[0][2],
            facet[1][0], facet[1][1], facet[1][2],
            facet[2][0], facet[2][1], facet[2][2],
            0
        ]
        #format characters: http://docs.python.org/2/library/struct.html
        self.st.write(struct.pack("12fH", *data))

    def add_facet(self, facet):
        if len(facet) == 3:
            #print "add_facet"
            #print '[%s]' % ', '.join(map(str, facet))
            self._write(facet)
            
        elif len(facet) > 3:
            facets = triangulate(facet)
            self.add_facets(facets)
        else:
            raise ValueError('wrong number of vertices')

    def add_facets(self, facets):
        #print "add %d facets" % len(facets)

        for facet in facets:
            self.add_facet(facet)

    def extrude(self,bottom,height):
        if len(bottom) < 3 :
            raise ValueError('not a polygon')
        else :
            top = []
            
            for vertice in bottom :
                top.append([vertice[0],vertice[1],vertice[2]+height])

            bottom.reverse()
            self.add_facet(bottom)
            bottom.reverse()
            
            for i in range(0,len(bottom)-1) :
                self.add_facet([bottom[i],bottom[i+1],top[i+1],top[i]])
            self.add_facet([bottom[len(bottom)-1],bottom[0],top[0],top[len(bottom)-1]])
                          
            self.add_facet(top)

ASCII_FACET = """facet normal {n[0]:.4f} {n[1]:.4f} {n[2]:.4f}
outer loop
vertex {face[0][0]:.4f} {face[0][1]:.4f} {face[0][2]:.4f}
vertex {face[1][0]:.4f} {face[1][1]:.4f} {face[1][2]:.4f}
vertex {face[2][0]:.4f} {face[2][1]:.4f} {face[2][2]:.4f}
endloop
endfacet
"""

BINARY_HEADER ="80sI"
BINARY_FACET = "12fH"

class ASCII_STL_Writer(STL_Writer):
    """ Export 3D objects build of 3 or 4 vertices as ASCII STL file.
    """
    def __init__(self, stream):
        self.fp = stream
        self._write_header()

    def _write(self, face):
        print "----- ASCII write facet ------"
        print '[%s]' % ', '.join(map(str, face))
        self.fp.write(ASCII_FACET.format(n=normal(face[0],face[1],face[2]),face=face))

    def _write_header(self):
        self.fp.write("solid python\n")

    def close(self):
        self.fp.write("endsolid python\n")

 
#functions to create some polygons
def polygon(s):
    v1=[0,0,0]
    v2=[s,0,0]
    v3=[s,s/2,0]
    v4=[s/2,s,0]
    v5=[0,s/2,0]
    return [v1,v2,v3,v4,v5]

def polygon2(s,m):
    v1=[m,m,0]
    v2=[m+s,m,0]
    v3=[m+s,m+s/2,0]
    v4=[m+s/2,m+s,0]
    v5=[m+0,m+s/2,0]
    return [v1,v2,v3,v4,v5]


#example
def example():
    with open('test.stl', 'wb') as doc:
        writer = STL_Writer(doc)
        #writer.add_faces(polygon(20))
        bottom=polygon(20)
        writer.extrude(bottom,5)
        hole=polygon2(5,5)
        #vertices have to be in reverse order for a hole
        hole.reverse()
        writer.extrude(hole,5)
        writer.close()

def example2():
    with open('test2.stl', 'wb') as doc:
        writer = ASCII_STL_Writer(doc)
        #writer.add_faces(polygon(20))
        bottom=polygon(20)
        writer.extrude(bottom,5)
        hole=polygon2(5,5)
        #vertices have to be in reverse order for a hole
        hole.reverse()
        writer.extrude(hole,5)
        writer.close()
