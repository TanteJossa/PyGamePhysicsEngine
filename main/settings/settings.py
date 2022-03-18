from matplotlib.pyplot import spring
from screen import *
import pygame

#Colors
white = (255,255,255)
blue = (0,0,255)
liteblue = (80, 80, 255)
green = (0,255,0)
red = (255,0,0)
black = (0,0,0)
gray = (50, 50, 50)
litegray = (100, 100, 100)
litergray = (150, 150, 150)


#Settings
#screen (dont change)
screenX = 1200
screenY = 600

#TIME
#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 30 #0.0001   
#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 10 #100000

#how much effect pulling on an object has
clickSpringConstant = 0.957
springMultiplier = 1 #10 * 10**10

#PHYSICS
#gravity
Zw = -9.81
G = 6.650338e-11
GravtityPixelsEnabled = False

#ARROWS
#pijl grootte multiplier hoe kleiner hoe groter de pijlen
Fmultiplier = 10 #30e19 #
Velmultiplier = 1 #10e2 # 
#what forces are given an arrow
enabledArrows = ("Fz","Flucht", "Fres", "Fzw", "Fspring")
enabledArrowsColors = (black, liteblue, blue, litegray, white)

#screen layout [[viewer x, viewer y], [menu under x, menu under y], [menu right x, menu right y]]
screenlayout = [[7, 20],[7, 9], [5, 1]]
singleSettingList = ["Grafiek", "Settings"]


#SIMFIELD
#simfieldsize in m
simfieldsizex = None #8e11 #None  #
#simfieldsizey = None
simfieldsizey = 40000.0


                        













#START PYGAME
#initialize pygame
pygame.init()
screen = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)

#mouse an mouse arrow setup
mousePressed = False
click_arrow_start = (0, 0)
click_arrow_end = (0, 0)
last_click_selected_obj = False
mouseHoldLength = 0

#text fonts
fontfreesan = pygame.font.Font('freesansbold.ttf', 20)

#caption and icon
pygame.display.set_caption("engine")

simFieldX1 = 10
simFieldY1 = 10
simFieldX2 = screen.get_width() / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
simFieldY2 = 10 + screen.get_height()  / (screenlayout[0][1] + screenlayout[1][1]) * screenlayout[0][1]
screenXYratio = (simFieldY2 - simFieldY1) /  (simFieldX2 - simFieldX1)


if simfieldsizex == None:
    simfieldsizex = simfieldsizey * screenXYratio
elif simfieldsizey == None:
    simfieldsizey = simfieldsizex * screenXYratio

print(simfieldsizex)
print(simfieldsizey)

#initialize button gui 
#manager = pygame_gui.UIManager((screenX, screenY))
clock = pygame.time.Clock()

#SETUP
#simulation
TotalIRLTime = 0
TotalSteps = 0

#objects
id = 0

