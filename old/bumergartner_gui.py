from time import time, sleep
import time
from matplotlib import pyplot as plt
import math
import os
import sys
import pygame
import pygame_gui


#Settings
#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 30
#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 1

#Zwaartekracht
Zw = -9.81



#setup simulation
TotalIRLTime = 0
id = 1
TotalSteps = 0

class object():
    #
    #s = positie (hoogte)
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    def __init__(self, name, massa=80, hoogte=0, opp=2, drag=0.7, startHoogte=39045, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000):
        global id
        
        #setup object
        self.name = name
        self.id = id
        id = id + 1
        self.m = massa
        self.posy = hoogte
        self.posx = 0
        self.opp = opp
        self.drag = drag
        self.startHoogte = startHoogte

        self.useParachute = useParachute
        self.parachuteOpp = parachuteOpp
        self.parachuteDrag = parachuteDrag
        self.parachuteDeployHeight = parachuteDeployHeight
        self.parachuteDeployTime = parachuteDeployTime

        self.vely = 0
        self.velx = 0
        self.parachuteStep = 0.00
        self.pasty = []
        self.pastx = []
        self.pastvely = []
        self.pastvelx = []
        self.paststep = []

    def update(self):
        global Zw
        global StepsPerSec
        global TotalSteps
        global SpeedMultiplier
        global TotalIRLTime

        #Fz = Zw * m
        Fz = Zw * self.m

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
        Luchtdruk = calc_luchtdruk(self.posy, Zw, Temp=4)
        Flucht = calc_flucht(Luchtdruk, self.vely, valopp, valdrag)


        #Tel alle krachten bij elkaar  op
        Fres = (Fz + Flucht)
        
        #Tel Fres op bij de snelheid en deel door massa a = F/m
        self.vely = self.vely + (Fres / StepsPerSec / self.m)

        #Verander de positie met de snelheid, als een object niet op de grond ligt
        if self.posy > 0:
            self.posy = self.posy + (self.vely / StepsPerSec)
            print("Current Height: " + str(round(self.posy, 2)) + f"{'Current Speed: '  + str(round(self.vely, 2)) + 'm/s':>40}" + f"{'Current Fres Per Sec: '  + str(round(Fres, 2)) + 'n':>40}" + f"{'Flucht Per Sec: ' + str(round(Flucht, 2)) + 'n':>40}" + f"{'Tijd in Sim: ' + str(round(TotalSteps / StepsPerSec, 2)):>30}" + f"{'IRL Tijd: ' + str(round(TotalIRLTime, 2)) + 's':>20}")

        #Als een object op de grond ligt beweegt het object niet verder naar beneden
        if self.posy <= 0:
            self.posy = 0
            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s" + "          " + "Finished Sim in: " + str(round(TotalIRLTime, 2)))
            
            #maak st-grafiek 
            plot_data("hoogte",self.name, self.paststep, self.pasty, 'Tijd (sec)', 'Hoogte (m)')

            #maak vt-grafiek
            plot_data("snelheid", self.name, self.paststep, self.pastvely, "Tijd (sec)", "Snelheid (m/s)")

            #Als het object geland is stopt het programma
            exit()

        #save data voor grafiek
        self.pastx.append(self.posx)
        self.pasty.append(self.posy)
        self.pastvelx.append(self.velx)
        self.pastvely.append(self.vely)
        self.paststep.append(TotalSteps / StepsPerSec)

#maakt een grafiek van twee arrays
def plot_data(name, objectName, dataX, dataY, xlabelname, ylabelname):
    plt.figure()
    plt.plot(dataX, dataY)
    plt.ylabel(ylabelname)
    plt.xlabel(xlabelname)
    plt.xlim(left=0)
    plt.grid(which='both')
    plt.savefig(str(name) +  '-' + str(objectName) + '.png')
    os.startfile(str(name) + '-' + str(objectName) + '.png')

# F = 0.5 * v^2 * luchtdruk * A * Cw
def calc_flucht(R, v=0, A=1.5, drag=0.7): 
    Flucht = 0.5 * R * v**2 * A * drag
    return Flucht

# Pa(h) = Pa(0) * E ^(-M * G * H / (R * T)) * 100
# ρ = Pa * M / R * T
def calc_luchtdruk(h, Zw=-9.81, MolMassaLucht=0.0288, Temp=0):
    Pa = 1013.00 * 2.7182818 ** (-MolMassaLucht * -Zw * h / (8.3144598 * (273.15 + Temp))) * 100
    R = (Pa * MolMassaLucht) / (8.3144598 * (273.15 + Temp))
    return R

def update_sim():
    global TotalSteps
    global TotalIRLTime

    #telt totaal aantal stappen in simulatie
    TotalSteps = TotalSteps + 1
    

    Baumgartner.update()


    #sqrt(()^2) zorgt dat er geen negatieve sleep time kan komen 
##    sleep(math.sqrt((1.00 / StepsPerSec / SpeedMultiplier - (EndTime - StartTime)) ** 2))

    #berekend echte tijd




#object settings
Baumgartner = object(name='Baumgartner',massa=80, hoogte=39045, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000)


#initialize game
pygame.init()


#create the screen
screenX = 1200
screenY = 600

screen = pygame.display.set_mode((screenX, screenY))
gui_manager = pygame_gui.UIManager((screenX, screenY))

#caption and icon
pygame.display.set_caption("engine")

#create menu
#hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
#                                            text='Say Hello',
#                                            manager=gui_manager)

#player
objectX = 370
objectY = 480

#colours
white = (255,255,255)
blue = (0,0,255)
liteblue = (100, 100, 255)
green = (0,255,0)
red = (255,0,0)
black = (0,0,0)
gray = (50, 50, 50)
litegray = (100, 100, 100)
litergray = (150, 150, 150)

#text fonts
fontfreesan = pygame.font.Font('freesansbold.ttf', 20)




#objects
def display_object():
    global TotalSteps
    global StepsPerSec

    objectY = 10 +  400 * ((Baumgartner.startHoogte - Baumgartner.posy) / Baumgartner.startHoogte)
    objectX = 10 + 100 * (1 / (TotalSteps + 1) / StepsPerSec)
    create_text(str(round(Baumgartner.posy,2)),(87,50))
#    update_sim()

    if Baumgartner.posy < 3000:
        objectImg = pygame.image.load('parachute.png')
    else:
        objectImg = pygame.image.load('skydiving.png')

    screen.blit(objectImg,(objectX, objectY))
    
#texts
def create_text(text='text',Centre=(screenX / 2, screenY / 2), color=liteblue,font=fontfreesan, antialias=True):
    text = font.render(text, antialias, color)
    textRect = text.get_rect()
    textRect.center = (Centre[0], Centre[1])
    screen.blit(text, textRect)
    return text, textRect

#rectangles
def create_rectangle(leftup=(10, 10), rightdown=(100, 100), color=gray, withheight=None, surface=screen, border_radius= -1, border_top_left_radius= -1, border_top_right_radius= -1, border_bottom_left_radius= -1, border_bottom_right_radius= -1):
    if withheight == None:
        width = rightdown[0] - leftup[0]
        height = rightdown[1] - leftup[1]
    elif withheight != None:
        width = withheight[0]
        height = withheight[1]

    pygame.draw.rect(surface, color, pygame.Rect(leftup[0], leftup[1], width, height),  border_radius= -1, border_top_left_radius= -1, border_top_right_radius= -1, border_bottom_left_radius= -1, border_bottom_right_radius= -1)

def create_menu(leftup=(10, 10), rightdown=(100, 100), color1=gray, color2=litegray, color3=litergray, color4=liteblue, divisions=[1], names=['name'], isVertical=True, nameSize=30, settingValues=None, Font='freesansbold.ttf', fontTitelSize=20, fontSettingSize=15):
    if len(names) != len(divisions):
        print('Every menu should have a name.')
        return

    #check if there is enough space for the menu
    if isVertical == True:
        if rightdown[0] - leftup[0] < 2 * 5 + (len(divisions) - 1) * 5 + 3 * len(divisions) + 40 * len(divisions):
            print('Not enough space.')
            return
    elif isVertical == False:
        if rightdown[1] - leftup[1] < 2 * 5 + (len(divisions) - 1) * 5 + 3 * len(divisions) + 20 * len(divisions):
            print('Not enough space.')
            return

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
            create_text(str(names[divisioncount]), ((leftup[0] + 8 + rightdown[0] - 8) / 2,  (leftup[1] + totalSpace + 3 + leftup[1] + totalSpace + nameSize) / 2), color=color4, font=menuFont)

            if settingValues != None:
                settingNumber = 0
                while settingNumber < len(settingValues):
                    create_text(settingValues[settingNumber][0],(leftup[0] + 30, leftup[1] + totalSpace + 3 + nameSize + 18))

                    settingNumber + 1


            totalSpace = totalSpace + space

        elif isVertical == False:
            space = (rightdown[0] - leftup[0] - (len(divisions) * 5) + 10) * (divisions[divisioncount] / totalDivNumber)
            create_rectangle((leftup[0] + totalSpace, leftup[1] + 5),(leftup[0] + totalSpace + space - 5, rightdown[1] - 5), color2)
            create_rectangle((leftup[0] + totalSpace + 3, leftup[1] + 8),(leftup[0] + totalSpace + space - 8, leftup[1] + nameSize), color3)
            create_text(str(names[divisioncount]), ((rightdown[0] + totalSpace + space + rightdown[0] + totalSpace) / 2 - (rightdown[0] - leftup[0]),  leftup[1] + 8 + nameSize / 2 - 4), color4, font=menuFont)

            totalSpace = totalSpace + space

        divisioncount = divisioncount + 1
    

#game loop
running = True
clock = pygame.time.Clock()

while running:
    #bereken later hoe lang de berekening kostte
    StartTime = time.time()

    time_delta = clock.tick(60)/1000.0


    #RBG = Red, green, blue
    screen.fill((0, 0, 0))

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        gui_manager.process_events(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())

        #gui
#        if event.type == pygame_gui.UI_BUTTON_PRESSED:
#            if event.ui_element == hello_button:
#                print('Hello World!')
            
#        gui_manager

    gui_manager.update(time_delta)

    #menu blocks
    create_rectangle((10, 10), (710, 430))

    #setting menu
    create_menu((720, 10), (1190, 590), divisions=[3, 2], names=['Object', 'Krachten'], isVertical=True)
    create_menu((10, 440), (710, 590), isVertical=False, divisions=[1,2,1], names=["Grafiek", "Tijd", "Settings"], settingValues=[['SettingName', 'displayText']])
    pygame.display.flip()

    create_text(str(Baumgartner.startHoogte),(87,26))


    gui_manager.draw_ui(screen)

    display_object()
    pygame.display.update()

    #bereken later hoe lang de berekening kostte
    EndTime = time.time()

    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)

