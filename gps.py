
#probably want to take a couple measurements and average them.
#The base station is there to fix drifting.

def get_coords():
    #read nmea GPS and parse (proably with a plugin, probably through tcp/ip as well)
    return coords
    #will probably return an array with latitude and longitude

def get_base_coords():
    #read base GPS coords over internet connection (see gps_client.py)
    return base_coords

def find_position(pos, base_pos, init_pos):
    fixed_coords[1] = pos[1] - (base_pos[1] - init_pos[1])
    fixed_coords[2] = pos[2] - (base_pos[2] - init_pos[2])
    fixed_coords[3] = (pos[3] + base_pos[3]) / 2
    return fixed_coords

#initialization
init_pos = get_base_coords()
position_log = []
maxdistance = 0

#position[1] = x coords, position[2] = y coords, distances in meters

#Main Loop
while distance > 5 || maxdistance < 10:
    coords.append(get_coords())
    base_coords.append(get_base_coords(pos))
    #compare times of last measurement and find where they are equal
    if base_coords[len(base_coords)][3] >= coords[len(coords)][3]:
        #this case should never happen since the base is a remote device and latency should be significantly greater
        i = 0
        pos_time = coords[len(coords)][3]
        base_pos_time = base_coords[len(base_coords)][3]
        while  base_pos > pos:
            pos_time = coords[len(coords)-i][3]
            i = i+1
        pos = [coords[len(coords)-i][1],coords[len(coords)-i][2], pos_time]
        base_pos = [base_coords[len(base_coords)][1],base_coords[len(base_coords)][2], base_pos_time]
    else:
        i = 0
        pos_time = coords[len(coords)][3]
        base_pos_time = base_coords[len(base_coords)][3]
        while  pos_time > base_pos_time:
            pos_time = base_coords[len(base_coords)-i][3]
            i = i+1
        pos = [coords[len(coords)][1],coords[len(coords)][2], pos_time]
        base_pos = [base_coords[len(base_coords)-i][1],base_coords[len(base_coords)-i][2], base_pos_time]

    #might want to repeat getting the position a few times and take the average
    #probably also want to change it to a cartesian coordinate system from the lat/lon format
    position = find_position(pos, base_pos, init_pos)
    position_log.append(position)
    if sqrt((position[1]-init_pos[1])^2+(position[2]-init_pos[2])^2) > maxdistance:
        maxdistance sqrt((position[1]-init_pos[1])^2+(position[2]-init_pos[2])^2)

#map area inside polygon:
#This is the complicated part. Find a path inside the polygon which does not
#decrease effeciency too much.

#Easiest way is to follow the path of the first side of the field that was done with an offset equals to the width
#of the tractor (which should be input by the operator). Then simply copy the path checking each point is inside the polygon and if
#tehre are no more points to follow continue in a straight line until the edge of the polygon.

#to chack if points are in the polygon
#Use matplotlib.nxutils.points_inside_poly, which implements a very efficient test.
#Examples and further explanation of this 40-year-old algorithm at the matplotlib FAQ.
#Update: Note that points_inside_poly is deprecated since version 1.2.0 of matplotlib. Use matplotlib.path.Path.contains_points instead.


#follow path:
#probably ask operator for initial positioning.

#check direction close to direction of first two points
#prompt ready
#check dot product of direction vector and points in certain radius in certain order
#find closest point with angle to distance ratio below specific threshold
#repeat until reach last point
