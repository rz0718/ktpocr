import math

def calDeg(x1,y1,x2,y2):
    myradians = math.atan2(y1-y2, x1-x2)
    mydegrees = math.degrees(myradians)
    mydegrees = mydegrees if mydegrees >= 0 else 360+mydegrees
    return mydegrees