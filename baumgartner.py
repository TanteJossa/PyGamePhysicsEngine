import matplotlib as plt
import os
from time import time, sleep
import time
import pygame
#from simphysics import *
#import pygame_gui
from math import *

#initialize pygame
pygame.init()

#screen (dont change)
screenX = 1200
screenY = 600
screen = pygame.display.set_mode((screenX, screenY), pygame.RESIZABLE)

#SETTINGS
#initialize button gui 
#manager = pygame_gui.UIManager((screenX, screenY))
clock = pygame.time.Clock()

#physics
#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 0.0002
#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 100000

#Zwaartekracht
Zw = 0
G = 6.650338e-11
GravtityPixelsEnabled = False

#pijl grootte multiplier hoe kleiner hoe groter de pijlen
Fmultiplier = 30e19
Velmultiplier = 10e2


#SETUP
#simulation
TotalIRLTime = 0
TotalSteps = 0

#objects
id = 0

#GUI
#colours
white = (255,255,255)
blue = (0,0,255)
liteblue = (80, 80, 255)
green = (0,255,0)
red = (255,0,0)
black = (0,0,0)
gray = (50, 50, 50)
litegray = (100, 100, 100)
litergray = (150, 150, 150)

#text fonts
fontfreesan = pygame.font.Font('freesansbold.ttf', 20)

#caption and icon
pygame.display.set_caption("engine")

enabledArrows = ("Fz","Flucht", "Fres", "Fzw")
enabledArrowsColors = (black, liteblue, blue, litegray)


#screen layout [[viewer x, viewer y], [menu under x, menu under y], [menu right x, menu right y]]
screenlayout = [[7, 20],[7, 9], [5, 1]]
singleSettingList = ["Grafiek", "Settings"]


simFieldX1 = 10
simFieldY1 = 10
simFieldX2 = screen.get_width() / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
simFieldY2 = 10 + screen.get_height()  / (screenlayout[0][1] + screenlayout[1][1]) * screenlayout[0][1]
screenXYratio = (simFieldY2 - simFieldY1) /  (simFieldX2 - simFieldX1)

#simfieldsize in m
simfieldsizex = 8e11
#simfieldsizey = 4e11
simfieldsizey = simfieldsizex * screenXYratio


#CLASSES
#physics
class physics_object():
    #
    #s = positie (hoogte)
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    instancelist = []

    def __init__(self, name, startposx=200, startposy=39045, massa=80, startvelx=0.0, startvely=0.0, colboxX=16, colboxY=16, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000, useAirRes=True, useSolarSys=False, icon=None):
        global id

        physics_object.instancelist.append(self)
        
        #setup object
        self.name = name
        self.id = id
        id = id + 1
        self.m = massa
        self.posy = startposy
        self.posx = startposx
        self.startposy = startposy
        self.startposx = startposx
        self.opp = opp
        self.drag = drag
        self.Fres = (0, 0)
        self.Fzw = (0, 0)
        self.Fz = (0, 0)
        self.startposy = startposy
        self.calc_onscreen_pos()

        self.Luchtdruk = 0
        self.useAirRes = useAirRes
        self.useSolarSys= useSolarSys
        self.useParachute = useParachute
        self.parachuteOpp = parachuteOpp
        self.parachuteDrag = parachuteDrag
        self.parachuteDeployHeight = parachuteDeployHeight
        self.parachuteDeployTime = parachuteDeployTime
        self.vel = (startvelx, startvely)
        self.parachuteStep = 0.00
        self.pasty = []
        self.pastx = []
        self.pastvely = []
        self.pastvelx = []
        self.paststep = []
        self.colboxX = colboxX
        self.colboxY = colboxY
        if icon == None:
            self.icon = self.name
        else:
            self.icon = icon
 
    def draw_force_arrows(self, enabledArrows=[], enabledArrowsColors=[]):
        global Fmultiplier
        global screenXYratio

        begin=(self.objectX + self.colboxX / 2, self.objectY  + self.colboxY / 2)
        arrowNumber = 0
        for item in enabledArrows:
            Fresend=(self.objectX + self.colboxX / 2 + getattr(self, item)[0] / Fmultiplier, self.objectY + self.colboxY / 2 - getattr(self, item)[1] / Fmultiplier)

#            if Fresend[0] - begin[0] >= 0.01 and Fresend[1] - begin[1] >= 0.01:
            create_arrow(begin=begin,end=Fresend,text=str(item),color=enabledArrowsColors[arrowNumber],textposoffset=15 * arrowNumber + 1, textColor=enabledArrowsColors[arrowNumber])
            arrowNumber = arrowNumber + 1
        
    def draw_vel_arrow(self):
        begin=(self.objectX + self.colboxX / 2, self.objectY  + self.colboxY / 2)

        Fresend=(self.objectX + self.colboxX / 2 + self.vel[0] / Velmultiplier, self.objectY + self.colboxY / 2 - self.vel[1] / Velmultiplier)


        create_arrow(begin=begin,end=Fresend,text="vel",color=red,textposoffset=15)


    def check_pos(self, x, y):
        if self.objectX - x <= 0 and self.objectY - y <= 0:
            if self.objectX + self.colboxX - x >= 0 and self.objectY + self.colboxY - y >= 0:
                return True
        return False

    def calc_pos(self):

        #Verander de positie met de snelheid, als een object niet op de grond ligt
        self.posx = self.posx + (self.vel[0] / StepsPerSec)

        if self.posy > 0:
            self.posy = self.posy + (self.vel[1] / StepsPerSec)
        elif self.posy < 0:
            self.posy = 0
          
        self.calc_onscreen_pos()

  
    def calc_onscreen_pos(self):
        global  simFieldX1
        global  simFieldY1
        global  simFieldX2    
        global  simFieldY2
        global  simfieldsizex
        global  simfieldsizey

        self.objectY = 10 + (simFieldY2 - simFieldY1) * ((simfieldsizey - self.posy) / simfieldsizey)
        self.objectX = 10 + (simFieldX2 - simFieldX1) * (self.posx / simfieldsizex)
      
    
    def display_object(self):
        global TotalSteps
        global StepsPerSec

        self.calc_onscreen_pos()

        self.calc_pos()

        if self.icon == 'skydiving':
            if self.posy < self.parachuteDeployHeight:
                self.objectImg = pygame.image.load('icons/' + 'parachute.png')
            else:
                self.objectImg = pygame.image.load('icons/' + 'skydiving.png')
        else:
            self.objectImg = pygame.image.load('icons/' + self.icon + '.png')

        screen.blit(self.objectImg,(self.objectX, self.objectY))

    def update(self):
        global Zw
        global StepsPerSec
        global TotalSteps
        global SpeedMultiplier
        global TotalIRLTime

        #Fz = Zw * m
        self.Fz = (0, Zw * self.m)

        #bereken luchtsweerstand
        if self.posy < self.parachuteDeployHeight and self.useParachute == True: 
            if self.parachuteStep < 1:
                self.parachuteStep = self.parachuteStep + (1 / (self.parachuteDeployTime * StepsPerSec))

                if self.parachuteDrag * self.parachuteStep > self.drag:
                    valdrag = self.parachuteDrag * self.parachuteStep
                else: 
                    valdrag = self.drag
                
                if self.parachuteOpp * self.parachuteStep > self.opp:
                    valopp = self.parachuteOpp * self.parachuteStep
                else:
                    valopp = self.opp
            else: 
                valdrag = self.parachuteDrag
                valopp = self.parachuteOpp

        else:
            valopp = self.opp
            valdrag = self.drag

        #bereken Flucht door eerst de dichtheid van de lucht op een bepaalde hoogte te berekenen en dan te berekenen welk effect dat heeft op het object
        if self.useAirRes == True:
          self.Luchtdruk = calc_luchtdruk(self.posy, Zw, Temp=4)
          self.Flucht = (-1 * calc_flucht(self.Luchtdruk, v2=self.vel[0]**2, A=valopp, drag=valdrag), calc_flucht(self.Luchtdruk, v2=self.vel[1]**2, A=valopp, drag=valdrag))
        else:
          self.Flucht = (0, 0)

        self.Fzw = (0, 0)

        if self.useSolarSys == True:
            #calc zw
            for instance in physics_object.instancelist:
                if not instance.id == self.id:
                    gravity = calc_gravity(self, instance)
                    self.Fzw = (self.Fzw[0] + gravity[0], self.Fzw[1] + gravity[1])


        #Tel alle krachten bij elkaar  op
        self.Fres = (self.Fz[0] + self.Flucht[0] + self.Fzw[0] , self.Fz[1] + self.Flucht[1] + self.Fzw[1])
        
        #Tel Fres op bij de snelheid en deel door massa a = F/m
        self.vel = (self.vel[0] + (self.Fres[0] / StepsPerSec / self.m), self.vel[1] + (self.Fres[1] / StepsPerSec / self.m))
        
        #apply forces and calculate pos
        self.calc_pos()
        
        #print("Current Height: " + str(round(self.posy, 2)) + f"{'Current Speed: '  + str(round(float(self.vel[0]), 2)) + 'm/s':>30}" + f"{'Current Fres Per Sec: '  + str(round(float(self.Fres[0]), 2)) + 'n':>40}" + f"{'Flucht Per Sec: ' + str(round(float(self.Flucht[0]), 2)) + 'n':>40}" + f"{'Tijd in Sim: ' + str(round(TotalSteps / StepsPerSec, 2)):>30}" + f"{'IRL Tijd: ' + str(round(TotalIRLTime, 2)) + 's':>20}")
        
        #Als een object op de grond ligt beweegt het object niet verder naar beneden
#        if self.posy <= 0:
#            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s" + "          " + "Finished Sim in: " + str(round(TotalIRLTime, 2)))
            
            #maak st-grafiek 
#            plot_data("hoogte",self.name, self.paststep, self.pasty, 'Tijd (sec)', 'Hoogte (m)')

            #maak vt-grafiek
#            plot_data("snelheid", self.name, self.paststep, self.pastvely, "Tijd (sec)", "Snelheid (m/s)")

        #save data voor grafiek
        self.pastx.append(self.posx)
        self.pasty.append(self.posy)
        self.pastvelx.append(self.vel[0])
        self.pastvely.append(self.vel[1])
        self.paststep.append(TotalSteps / StepsPerSec)


#FUNCTIONS
#GUI
#texts
def create_text(text='text',Centre=None, maxcoords=((100, 100), (400, 200)), color=liteblue,font=fontfreesan, antialias=True, outline=None):
    if not Centre == None:
        text = font.render(text, antialias, color)
        textRect = text.get_rect()
        textRect.center = (Centre[0], Centre[1])
    else:
        textpos = calc_text_coords(text, ((maxcoords[0][0] + maxcoords[1][0]) / 2, (maxcoords[0][1] + maxcoords[1][1]) / 2), font)

        coordsDiffX = textpos[1][0] - textpos[0][0]
        coordsDiffY = textpos[1][1] - textpos[0][1]

        maxCoordsDifX = maxcoords[1][0] - maxcoords[0][0]
        maxCoordsDifY = maxcoords[1][1] - maxcoords[0][1]
        
        if (maxCoordsDifX / coordsDiffX) <= (maxCoordsDifY / coordsDiffY):
            font = pygame.font.Font('freesansbold.ttf', round((maxCoordsDifX / coordsDiffX) * 20.0))
        else:
            font = pygame.font.Font('freesansbold.ttf', round((maxCoordsDifY / coordsDiffY) * 20.0))

        textsize = calc_text_coords(text, ((maxcoords[0][0] + maxcoords[1][0]) / 2, (maxcoords[0][1] + maxcoords[1][1]) / 2), font)

        text = font.render(text, antialias, color)
        textRect = text.get_rect()
        if outline == None:
            textRect.center = ((maxcoords[0][0] + maxcoords[1][0]) / 2 - (textsize[0][0] - maxcoords[0][0]), (maxcoords[0][1] + maxcoords[1][1]) / 2 - (textsize[0][1] - maxcoords[0][1]))
        
        elif outline == "right":
            textRect.center = ((maxcoords[0][0] + maxcoords[1][0]) / 2 + (textsize[0][0] - maxcoords[0][0]), (maxcoords[0][1] + maxcoords[1][1]) / 2 + (textsize[0][1] - maxcoords[0][1]))



    screen.blit(text, textRect)
    return text, textRect

#input two coord and print a rectangle
def create_rectangle(leftup=(10, 10), rightdown=(100, 100), color=gray, withheight=None, surface=screen, border_radius= -1, border_top_left_radius= -1, border_top_right_radius= -1, border_bottom_left_radius= -1, border_bottom_right_radius= -1):
    if withheight == None:
        width = rightdown[0] - leftup[0]
        height = rightdown[1] - leftup[1]
    elif withheight != None:
        width = withheight[0]
        height = withheight[1]

    pygame.draw.rect(surface, color, pygame.Rect(leftup[0], leftup[1], width, height),  border_radius= -1, border_top_left_radius= -1, border_top_right_radius= -1, border_bottom_left_radius= -1, border_bottom_right_radius= -1)

#give the start and end of an arrow you can set a text that will be in the centre
def create_arrow(begin=(100, 100), end=(200, 400), width=5, arrow_size=None, color=blue, text=None, textColor=None, textfont=fontfreesan, textposoffset=0):
    global screenXYratio
    length = sqrt((end[0]-begin[0])**2 + (end[1]-begin[1])**2)

    angle = atan2((end[1]-begin[1]), (end[0]-begin[0]))

    cosangle = cos(angle)
    sinangle = sin(angle)

    if arrow_size == None:
        arrow_length = width
    else:
        arrow_length = arrow_size


    maxArrow  = 3000
    minArrow = -maxArrow


    if length < maxArrow:
        rotatexoffset = width / 2 * cos(radians(90 - degrees(angle)))
        rotateyoffset = width / 2 * sin(radians(90 - degrees(angle)))

        pointTriBeginX = begin[0] + (length - arrow_length) * cosangle
        pointTriBeginY = begin[1] + (length - arrow_length) * sinangle

        vertecies = [(begin[0] + rotatexoffset, begin[1] - rotateyoffset), 
                    (pointTriBeginX + rotatexoffset, pointTriBeginY - rotateyoffset),
                    (pointTriBeginX + rotatexoffset * 2, pointTriBeginY - 2 * rotateyoffset),
                    (end[0], end[1]),
                    (pointTriBeginX - rotatexoffset * 2, pointTriBeginY + 2 * rotateyoffset),
                    (pointTriBeginX - rotatexoffset, pointTriBeginY + rotateyoffset),
                    (begin[0] - rotatexoffset, begin[1] + rotateyoffset)
                    ]

        if textColor == None:
            textColor = color


        if text != None:
            textpos = (begin[0] + (length / 2) * cosangle + 10 + textfont.size(text)[0] / 2, begin[1] + (length / 2) * sinangle - 5 - textfont.size(text)[1] / 2 + textposoffset)
            create_text(text, textpos, color=textColor)


    else: 
        angle = atan2((end[1]-begin[1]), (end[0]-begin[0]))

        rotatexoffset = width / 2 * cos(radians(90 - degrees(angle)))
        rotateyoffset = width / 2 * sin(radians(90 - degrees(angle)))
        
        pointTriBeginX = begin[0] + (maxArrow - arrow_length) * cosangle
        pointTriBeginY = begin[1] + (maxArrow - arrow_length) * sinangle

        vertecies = [(begin[0] + rotatexoffset, begin[1] - rotateyoffset), 
                    (pointTriBeginX + rotatexoffset, pointTriBeginY - rotateyoffset),
                    (pointTriBeginX + rotatexoffset * 2, pointTriBeginY - 2 * rotateyoffset),
                    (begin[0] + maxArrow * cosangle, begin[1] + maxArrow * sinangle),
                    (pointTriBeginX - rotatexoffset * 2, pointTriBeginY + 2 * rotateyoffset),
                    (pointTriBeginX - rotatexoffset, pointTriBeginY + rotateyoffset),
                    (begin[0] - rotatexoffset, begin[1] + rotateyoffset)
                    ]

        if textColor == None:
            textColor = color

        if text != None:
            textpos = (begin[0] + (maxArrow / 2) * cosangle + 10 + textfont.size(text)[0] / 2, begin[1] + (maxArrow / 2) * sinangle - 5 - textfont.size(text)[1] / 2 + textposoffset)
            create_text(text, textpos, color=textColor)

    pygame.draw.polygon(screen, color, vertecies)


#create menu with values or settings/buttons
def create_menu(leftup=(10, 10), rightdown=(100, 100), color1=gray, color2=litegray, color3=litergray, color4=liteblue, divisions=[1], names=['name'], isVertical=True, nameSize=30, settingValues=None, Font='freesansbold.ttf', fontTitelSize=20, fontSettingSize=15, settings=[[["Hoogte", "10"]],[],[]]):
    if len(names) != len(divisions):
        print('Every menu should have a name.')
        return

    #check if there is enough space for the menu
    # if isVertical == True:
    #     if rightdown[0] - leftup[0] < 2 * 5 + (len(divisions) - 1) * 5 + 3 * len(divisions) + 40 * len(divisions):
    #         print('Not enough space.')
    #         return
    # elif isVertical == False:
    #     if rightdown[1] - leftup[1] < 2 * 5 + (len(divisions) - 1) * 5 + 3 * len(divisions) + 20 * len(divisions):
    #         print('Not enough space.')
    #         return

    #create menu fonts
    menuFont = pygame.font.Font(Font, fontTitelSize)
    settingFont = pygame.font.Font(Font, fontSettingSize)
    create_rectangle(leftup, rightdown, color1)
    divisioncount = 0
    totalDivNumber = 0
    totalSpace = 5

    for i in divisions:
        totalDivNumber = totalDivNumber + i

    while divisioncount < len(divisions):
        if isVertical == True:
            space = (rightdown[1] - leftup[1] - (len(divisions) * 5) + 10) * (divisions[divisioncount] / totalDivNumber)
            create_rectangle((leftup[0] + 5, leftup[1] + totalSpace),(rightdown[0] - 5, leftup[1] + totalSpace + space - 5), color2)
            create_rectangle((leftup[0] + 8, leftup[1] + totalSpace + 3),(rightdown[0] - 8, leftup[1] + totalSpace + nameSize), color3)
            create_text(str(names[divisioncount]), maxcoords=((leftup[0] + 8, leftup[1] + totalSpace + 5),(leftup[0] + (leftup[0] + rightdown[0]) / 2, leftup[1] + totalSpace + nameSize)), color=color4, font=menuFont)

            reached_bottom = 0
            setting_row_count = 0
            
            for setting in settings[divisioncount]:
                if leftup[1] + totalSpace + nameSize + setting_row_count * 30 + 10 <= totalSpace + space: 
                    setting_row_count = setting_row_count + 1
                else:
                    reached_bottom = reached_bottom + 1
                    setting_row_count = 0


                create_text(str(setting[0]), maxcoords=((leftup[0] + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2, leftup[1] + totalSpace + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                                                        (leftup[0] + (rightdown[0] - leftup[0]) / 4 + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2, leftup[1] + totalSpace + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25)))
                

                valueBox = ((leftup[0] + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2 + (rightdown[0] - leftup[0] - 30) / 4, leftup[1] + totalSpace + nameSize - 15 + setting_row_count * 25 + reached_bottom * 25), 
                            (leftup[0] + (rightdown[0] - leftup[0] - 20) / 2 + 10 + reached_bottom * (rightdown[0] - leftup[0] - 30) / 2, leftup[1] + totalSpace + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25))

                if isinstance(setting[1],(int, float)):
                    create_text(str(round(setting[1] * 1.00, 2)), maxcoords=valueBox, color=white, outline="right")
                elif not setting[1] == None: 
                    create_text(str(setting[1]), maxcoords=valueBox, color=white, outline="right")
                else:
                    create_text("None", maxcoords=valueBox, color=white, outline="right")


            totalSpace = totalSpace + space

        elif isVertical == False:
            space = (leftup[0]  + (rightdown[0] - leftup[0])) * (divisions[divisioncount] / totalDivNumber)
            create_rectangle((leftup[0] + totalSpace, leftup[1] + 5),(leftup[0] + totalSpace + space - 5, rightdown[1] - 5), color2)
            create_rectangle((leftup[0] + totalSpace + 3, leftup[1] + 8),(leftup[0] + totalSpace + space - 8, leftup[1] + nameSize), color3)
            create_text(str(names[divisioncount]), maxcoords=((leftup[0] + totalSpace + 8, leftup[1] + 5),(leftup[0] + totalSpace + space - 5, leftup[1] + nameSize)), color=color4, font=menuFont)

            reached_bottom = 0
            setting_row_count = 0
            
            for setting in settings[divisioncount]:
                if leftup[0] + totalSpace + space / 2<= totalSpace + space: 
                    setting_row_count = setting_row_count + 1
                else:
                    reached_bottom = reached_bottom + 1
                    setting_row_count = 0

                if names[divisioncount] in singleSettingList:
                    reached_bottom = 0
                    #makes it so you texts are not very small in small menu's
                    firstSettingSpacing = 2
                    secondSettingSpacing = 1
                else:
                    firstSettingSpacing = 4
                    secondSettingSpacing = 2

                create_text(str(setting[0]), maxcoords=((leftup[0] + reached_bottom * (totalSpace + space) / 2 + totalSpace, leftup[1] + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                                                        (leftup[0] + reached_bottom * (totalSpace + space) / 2 + totalSpace + space / firstSettingSpacing, leftup[1] + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25)))
                

                valueBox = ((leftup[0] + reached_bottom * (totalSpace + space) + totalSpace + space / firstSettingSpacing, leftup[1] + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                            (leftup[0] + reached_bottom * (totalSpace + space) + totalSpace + space / secondSettingSpacing - 10, leftup[1] + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25))

                if isinstance(setting[1],(int, float)):
                    create_text(str(round(setting[1] * 1.00, 2)), maxcoords=valueBox, color=white, outline="right")
                elif not setting[1] == None: 
                    create_text(str(setting[1]), maxcoords=valueBox, color=white, outline="right")
                else:
                    create_text("None", maxcoords=valueBox, color=white, outline="right")

            totalSpace = totalSpace + space

        divisioncount = divisioncount + 1

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

#OTHER
#make a graph with a x and y arrays
def plot_data(name, objectName, dataX, dataY, xlabelname, ylabelname):
    plt.figure()
    plt.plot(dataX, dataY)
    plt.ylabel(ylabelname)
    plt.xlabel(xlabelname)
    plt.xlim(left=0)
    plt.grid(which='both')
    plt.savefig(str(name) +  '-' + str(objectName) + '.png')
    os.startfile(str(name) + '-' + str(objectName) + '.png')

#select the object that is going to display its settings in the menu
def set_selected_obj(obj):
    selected_obj = obj
    return selected_obj

def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))

#calculate text coords: [[xtop, ytop],[xend, yend]]
def calc_text_coords(text="test",centre=(100, 100), font=fontfreesan):
    size = font.size(text)
    return [[centre[0] - size[0] / 2, centre[1] - size[1] / 2], [centre[0] + size[0] / 2, centre[1] + size[1] / 2]]

# def calc_pixel_to_game_coords(x, y):
#     return ( x / simfieldsizex * (simFieldX2 - simFieldX1), (simfieldsizey - y) / simfieldsizey * (simFieldY2 - simFieldY1))

def calc_game_to_pixel_coords(x=None, y=None):
    if x != None and y != None:
        return ( x / simfieldsizex * (simFieldX2 - simFieldX1) + simFieldX1, (simfieldsizey - y) / simfieldsizey * (simFieldY2 - simFieldY1))
    elif x != None:
        return  x / simfieldsizex * (simFieldX2 - simFieldX1) + simFieldX1
    elif y != None:
        return  (simfieldsizey - y) / simfieldsizey * (simFieldY2 - simFieldY1) + simFieldY1
    else:
        print("did not put in a x or y in calc_game_to_pixel_coords()")

def calc_pixel_to_game_coords(x=None, y=None):
    if x != None and y != None:
        return ( (x - 10) / (simFieldX2 - simFieldX1) * simfieldsizex, (simFieldY2 - y) / (simFieldY2 - simFieldY1) * simfieldsizey )
    elif x != None:
        return   (x - 10) / (simFieldX2 - simFieldX1) * simfieldsizex

    elif y != None:
        return  (simFieldY2 - y) / (simFieldY2 - simFieldY1) * simfieldsizey
    else:
        print("did not put in a x or y in calc_game_to_pixel_coords()")

#create Baumgartner
#Baumgartner = physics_object(name='Baumgartner',startposy=39045, startposx=200, startvelx=100, massa=80, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000)

sun = physics_object(name='sun', startposy=simfieldsizey / 2, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, useAirRes=False, useSolarSys=True)
sun2 = physics_object(name='sun2', startposy=simfieldsizey / 4 * 3, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, startvelx=30000, useAirRes=False, useSolarSys=True, icon='sun')

mercury = physics_object(name='mercury', startposy=sun.startposy, startposx=sun.startposx - 0.58e11, massa=3.285E23 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=47480)

venus = physics_object(name='venus', startposy=sun.startposy, startposx=sun.startposx - 1.08e11, massa=4.867E24 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=35020)

earth = physics_object(name='earth', startposy=sun.startposy, startposx=sun.startposx - 1.6e11, massa=5.97219e24, useParachute=False, useAirRes=False, startvelx=0, startvely=29780, useSolarSys=True)

moon = physics_object(name='moon', startposy=earth.startposy, startposx=earth.startposx - 3.844e9, massa=7.34767309e22 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=earth.vel[1] + 1023, startvelx=1000)

mars = physics_object(name='mars', startposy=sun.startposy, startposx=sun.startposx - 2.28e11, massa=6.39E23, useParachute=False, useAirRes=False, startvelx=0, startvely=24130, useSolarSys=True)



#game loop
running = True
clock = pygame.time.Clock()

#initialize phisics objects
[instance.update() for instance in physics_object.instancelist]

#reload selected of
set_selected_obj_name = earth


#run gui till the program is quitted
while running:
    #setup for frame time calculation
    StartTime = time.time()
    time_delta = clock.tick(60)/1000.0

    #set the screen size if it has changed
    screenX = screen.get_size()[0]
    screenY = screen.get_size()[1]
    simFieldX1 = 10
    simFieldY1 = 10
    simFieldX2 = screen.get_width() / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
    simFieldY2 = 10 + screen.get_height()  / (screenlayout[0][1] + screenlayout[1][1]) * screenlayout[0][1]
    screenXYratio = (simFieldY2 - simFieldY1) /  (simFieldX2 - simFieldX1)

    #event loop
    for event in pygame.event.get():
        #stop the program if someone exits
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(str(pygame.mouse.get_pos()) + str((calc_pixel_to_game_coords(pygame.mouse.get_pos()[0]), calc_pixel_to_game_coords(y=pygame.mouse.get_pos()[1]))))
            
            for instance in physics_object.instancelist:
                if instance.check_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) == True:
                    set_selected_obj_name = instance
#           new_obj = physics_object(name='new_obj', startposx=calc_pixel_to_game_coords(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])[0] ,startposy=calc_pixel_to_game_coords(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])[1] , massa=2 * 10 , useParachute=False, useAirRes=False, useSolarSys=True, startvelx=-20)


    #clear screen
    screen.fill((0, 0, 0))

    #reload selected of
    selected_obj = set_selected_obj(set_selected_obj_name)

    #create/update setting objects [[menu1["setting name", value],["setting2 name", value]...], 
    #                               [menu2["setting name", value]],
    #                               ...
    #                               ]
    object_settings = [[["Naam",selected_obj.name],["Massa",selected_obj.m],["Oppervlakte",selected_obj.opp],["StartHoogte", selected_obj.startposy],["PosX", selected_obj.posx],["Hoogte", selected_obj.posy],["Velocity x", selected_obj.vel[0]],["Velocity Y", selected_obj.vel[1]],["Luchtdruk",selected_obj.Luchtdruk]],
                        [["Fres", sqrt(selected_obj.Fres[0]**2 + selected_obj.Fres[1]**2)], ["Fz", selected_obj.Fz[1]], ["Flucht",sqrt(selected_obj.Flucht[0]**2 + selected_obj.Flucht[1]**2)]],
                        []]

    undersettings = [[["Width", simfieldsizex],["Height", simfieldsizey]],
                     [["IRL time", TotalIRLTime]],
                     [["Arrow F size", Fmultiplier]]]

    #menu blocks
    #setting menu
    #simfield
    simFieldX1 = 10
    simFieldY1 = 10
    simFieldX2 = screen.get_width() / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
    simFieldY2 = 10 + screen.get_height()  / (screenlayout[0][1] + screenlayout[1][1]) * screenlayout[0][1]

    #right
    rightMenuX1 = 20 + (screen.get_width() - 20) / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
    rightMenuY1 = 10
    rightMenuX2 = rightMenuX1 - 10 + (screen.get_width() - 20) / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[2][0]
    rightMenuY2 = screen.get_height() - 10

    #under
    underMenuX1 = 10
    underMenuY1 = 20 + screen.get_height()  / (screenlayout[0][1] + screenlayout[1][1]) * screenlayout[0][1]
    underMenuX2 = screen.get_width() / (screenlayout[0][0] + screenlayout[2][0]) * screenlayout[0][0]
    underMenuY2 = screen.get_height() - 10

    

    create_rectangle((simFieldX1, simFieldY1),(simFieldX2, simFieldY2))
    create_menu((rightMenuX1, rightMenuY1), (rightMenuX2, rightMenuY2), divisions=[3, 2], names=['Object', 'Krachten'], isVertical=True, settings=object_settings)
    create_menu((underMenuX1, underMenuY1), (underMenuX2, underMenuY2), isVertical=False, divisions=[1,2,1], names=["Grafiek", "Tijd", "Settings"], settings=undersettings)

    #update menus
    pygame.display.flip()
    #manager.draw_ui(screen)




    #draw gravity pixels
    if GravtityPixelsEnabled == True:
        
        maxGrav = 10e29
        gravDivisions = 50

        for divisionx in range(gravDivisions):
            for divisiony in range(gravDivisions):
                currentGrav = 0.0
                
                divisionX1 = (simFieldX2 - simFieldX1) / gravDivisions * (divisionx) - 1
                divisionX2 = (simFieldX2 - simFieldX1) / gravDivisions * (divisionx +  1)
                divisionY1 = (simFieldY2 - simFieldY1) / gravDivisions * (divisiony) - 1
                divisionY2 = (simFieldY2 - simFieldY1) / gravDivisions * (divisiony + 1)
                
                pixelSimX = calc_pixel_to_game_coords(x=(divisionX2 + divisionX1) / 2)
                pixelSimY = calc_pixel_to_game_coords(y=(divisionY2 + divisionY1) / 2 )
                
                for instance in physics_object.instancelist:
                    currentGrav = currentGrav + (instance.m**2 * G) / ((instance.posx - pixelSimX)**2 + (instance.posy - pixelSimY)**2 + 0.0001)

                grav = currentGrav / maxGrav

                pixelcolor = (round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)))

                screen.fill(pixelcolor, ((10 + divisionX1, 10 + divisionY1), (divisionX2 - divisionX1, 10 + divisionY2)))      


    #counts total simulation steps
    TotalSteps = TotalSteps + 1
 
    #calculate new object state for every physics obj
    [instance.update() for instance in physics_object.instancelist]

    #draw an arrow 

    [instance.draw_vel_arrow() for instance in physics_object.instancelist]

    for instance in physics_object.instancelist:
        if instance == selected_obj:
                instance.draw_force_arrows(enabledArrows, enabledArrowsColors)

    #draw the object icon on top to the screen and display its force vectors
    [instance.display_object() for instance in physics_object.instancelist]

    #draw the entire picture to the screen
    pygame.display.update()

    #calculate simulation time
    EndTime = time.time()

    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)

