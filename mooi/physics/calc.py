from math import *
from settings.settings import *

#PHYSICS
# F = 0.5 * v^2 * luchtdruk * A * Cw
def calc_flucht(R, v2=0, A=1.5, drag=0.7): 
    Flucht = 0.5 * R * v2 * A * drag
    return Flucht

# Pa(h) = Pa(0) * E ^(-M * G * H / (R * T)) * 100
# ρ = Pa * M / R * T
def calc_luchtdruk(h, Zw=-9.81, MolMassaLucht=0.0288, Temp=0):
    Pa = 1013.00 * 2.7182818 ** (-MolMassaLucht * -Zw * h / (8.3144598 * (273.15 + Temp))) * 100
    R = (Pa * MolMassaLucht) / (8.3144598 * (273.15 + Temp))
    return R

def calc_gravity(obj1, obj2):
    global G
    corner = atan2((obj2.posy - obj1.posy), (obj2.posx - obj1.posx))

    F = (G * obj1.m * obj2.m) / ((obj2.posx - obj1.posx)**2 + (obj2.posy - obj1.posy)**2 + 0.0001) 

    Fzw = ((F * cos(corner)), 
           (F * sin(corner)))

    return Fzw
