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
screen = pygame.display.set_mode((screenX, screenY))

#SETTINGS
#initialize button gui 
#manager = pygame_gui.UIManager((screenX, screenY))
clock = pygame.time.Clock()

#physics
#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 30
#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 1

#Zwaartekracht
Zw = -9.81

#pijl grootte multiplier hoe kleiner hoe groter de pijlen
Fmultiplier = 10

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


#CLASSES
#physics
class physics_object():
    #
    #s = positie (hoogte)
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    instancelist = []

    def __init__(self, name, startposx=200, startposy=39045, massa=80, startvelx=10.0, startvely=0.0, colboxX=16, colboxY=16, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000):
        global id
        
        physics_object.instancelist.append(self)
        
        #setup object
        self.name = name
        self.id = id
        id = id + 1
        self.m = massa
        self.posy = startposy
        self.posx = startposx
        self.opp = opp
        self.drag = drag
        self.Fres = (0, 0)
        self.startposy = startposy
        self.objectY = 10 +  400 * ((self.startposy - self.posy) / self.startposy)
        self.objectX = 10 + 100 * (1 / (TotalSteps + 1) / StepsPerSec)

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
        
 
    def draw_arrows(self, enabledArrows=[], enabledArrowsColors=[]):
        global Fmultiplier

        begin=(self.objectX + self.colboxX / 2, self.objectY  + self.colboxY / 2)

        arrowNumber = 0
        for item in enabledArrows:
            Fresend=(self.objectX + getattr(self, item)[0] / Fmultiplier + self.colboxX / 2, self.objectY - getattr(self, item)[1] / Fmultiplier + self.colboxY / 2)
            create_arrow(begin=begin,end=Fresend,text=str(item),color=enabledArrowsColors[arrowNumber])
            arrowNumber = arrowNumber + 1


    def calc_pos(self):
        #Verander de positie met de snelheid, als een object niet op de grond ligt
        self.posx = self.posx + (self.vel[0] / StepsPerSec)

        if self.posy > 0:
            self.posy = self.posy + (self.vel[1] / StepsPerSec)
        elif self.posy < 0:
            self.posy = 0

        self.objectY = 10 + 400 * ((self.startposy - self.posy) / self.startposy)
        self.objectX = 10 + 700 * (self.posx / 39045)

    def display_object(self):
        global TotalSteps
        global StepsPerSec
        
        #draw an arrow 
        enabledArrows = ("Fz","Flucht", "Fres")
        enabledArrowsColors = (black, liteblue, blue)
        self.draw_arrows(enabledArrows, enabledArrowsColors)
        
        self.calc_pos()
        if self.posy < self.parachuteDeployHeight:
            self.objectImg = pygame.image.load('parachute.png')
        else:
            self.objectImg = pygame.image.load('skydiving.png')

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
        self.Luchtdruk = calc_luchtdruk(self.posy, Zw, Temp=4)
        self.Flucht = (-1 * calc_flucht(self.Luchtdruk, v2=self.vel[0]**2, A=valopp, drag=valdrag), calc_flucht(self.Luchtdruk, v2=self.vel[1]**2, A=valopp, drag=valdrag))
#        print(self.Flucht)

        #Tel alle krachten bij elkaar  op
        self.Fres = (self.Fz[0] + self.Flucht[0] , self.Fz[1] + self.Flucht[1])
        
        #Tel Fres op bij de snelheid en deel door massa a = F/m
        self.vel = (self.vel[0] + (self.Fres[0] / StepsPerSec / self.m), self.vel[1] + (self.Fres[1] / StepsPerSec / self.m))

        #apply forces and calculate pos
        self.calc_pos()
        
        #print("Current Height: " + str(round(self.posy, 2)) + f"{'Current Speed: '  + str(round(float(self.vel[0]), 2)) + 'm/s':>40}" + f"{'Current Fres Per Sec: '  + str(round(float(self.Fres[0]), 2)) + 'n':>40}" + f"{'Flucht Per Sec: ' + str(round(float(self.Flucht[0]), 2)) + 'n':>40}" + f"{'Tijd in Sim: ' + str(round(TotalSteps / StepsPerSec, 2)):>30}" + f"{'IRL Tijd: ' + str(round(TotalIRLTime, 2)) + 's':>20}")
        
        #Als een object op de grond ligt beweegt het object niet verder naar beneden
        if self.posy <= 0:
            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s" + "          " + "Finished Sim in: " + str(round(TotalIRLTime, 2)))
            
            #maak st-grafiek 
            plot_data("hoogte",self.name, self.paststep, self.pasty, 'Tijd (sec)', 'Hoogte (m)')

            #maak vt-grafiek
            plot_data("snelheid", self.name, self.paststep, self.pastvely, "Tijd (sec)", "Snelheid (m/s)")

        #save data voor grafiek
        self.pastx.append(self.posx)
        self.pasty.append(self.posy)
        self.pastvelx.append(self.vel[0])
        self.pastvely.append(self.vel[1])
        self.paststep.append(TotalSteps / StepsPerSec)


#FUNCTIONS
#GUI
#texts
def create_text(text='text',Centre=(screenX / 2, screenY / 2), color=liteblue,font=fontfreesan, antialias=True):
    text = font.render(text, antialias, color)
    textRect = text.get_rect()
    textRect.center = (Centre[0], Centre[1])
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
def create_arrow(begin=(100, 100), end=(200, 400), width=5, arrow_size=None, color=blue, text=None, textColor=None, textfont=fontfreesan):
    angle = degrees(atan((end[1]-begin[1]) / (end[0]-begin[0] + 0.000001)))
    length = sqrt((end[0]-begin[0])**2 + (end[1]-begin[1])**2)
    rotatexoffset = width / 2 * cos(radians(90 - angle))
    rotateyoffset = width / 2 * sin(radians(90 - angle))

    if arrow_size == None:
        arrow_length = width
    else:
        arrow_length = arrow_size

    if end[0] - begin[0] >= 0 and end[1] - begin[1] >= 0 or end[0] - begin[0] >= 0 and end[1] - begin[1] < 0:
        textpos = (begin[0] + (length / 2) * cos(radians(angle)) + 10 + textfont.size(text)[0] / 2, begin[1] + (length / 2) * sin(radians(angle)) - 5 - textfont.size(text)[1] / 2)
        vertecies = [(begin[0] + rotatexoffset, begin[1] - rotateyoffset), 
                    (begin[0] + (length - arrow_length) * cos(radians(angle)) + rotatexoffset, begin[1] + (length - arrow_length) * sin(radians(angle)) - rotateyoffset),
                    (begin[0] + (length - arrow_length) * cos(radians(angle)) + 2 * rotatexoffset, begin[1] + (length - arrow_length) * sin(radians(angle)) - 2 * rotateyoffset),
                    (end[0], end[1]),
                    (begin[0] + (length - arrow_length) * cos(radians(angle)) - 2 * rotatexoffset, begin[1] + (length - arrow_length) * sin(radians(angle)) + 2 * rotateyoffset),
                    (begin[0] + (length - arrow_length) * cos(radians(angle)) - rotatexoffset, begin[1] + (length - arrow_length) * sin(radians(angle)) + rotateyoffset),
                    (begin[0] - rotatexoffset, begin[1] + rotateyoffset)
                    ]

    elif end[0] - begin[0] < 0 and end[1] - begin[1] >= 0 or  end[0] - begin[0] < 0 and end[1] - begin[1] < 0:
        textpos = (begin[0] - (length / 2) * cos(radians(angle)) + 10 + textfont.size(text)[0] / 2, begin[1] - (length / 2) * sin(radians(angle)) - 5 - textfont.size(text)[1] / 2)
        vertecies = [(begin[0] + rotatexoffset, begin[1] - rotateyoffset), 
                    (begin[0] - (length - arrow_length) * cos(radians(angle)) + rotatexoffset, begin[1] - (length - arrow_length) * sin(radians(angle)) - rotateyoffset),
                    (begin[0] - (length - arrow_length) * cos(radians(angle)) + 2 * rotatexoffset, begin[1] - (length - arrow_length) * sin(radians(angle)) - 2 * rotateyoffset),
                    (end[0], end[1]),
                    (begin[0] - (length - arrow_length) * cos(radians(angle)) - 2 * rotatexoffset, begin[1] - (length - arrow_length) * sin(radians(angle)) + 2 * rotateyoffset),
                    (begin[0] - (length - arrow_length) * cos(radians(angle)) - rotatexoffset, begin[1] - (length - arrow_length) * sin(radians(angle)) + rotateyoffset),
                    (begin[0] - rotatexoffset, begin[1] + rotateyoffset)
                    ]

#    for i in vertecies:
#        print(i)
    if textColor == None:
        textColor = color

    if not text == None:
        create_text(text, textpos, textColor)

    pygame.draw.polygon(screen, color, vertecies)

#create menu with values or settings/buttons
def create_menu(leftup=(10, 10), rightdown=(100, 100), color1=gray, color2=litegray, color3=litergray, color4=liteblue, divisions=[1], names=['name'], isVertical=True, nameSize=30, settingValues=None, Font='freesansbold.ttf', fontTitelSize=20, fontSettingSize=15, settings=[[["Hoogte", "10"]],[],[]]):
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

            reached_bottom = 0
            setting_row_count = 0
            
            for setting in settings[divisioncount]:
                if leftup[1] + totalSpace + nameSize + setting_row_count * 30 + 10 <= totalSpace + space: 
                    create_setting(pos=(leftup[0] + 80 + reached_bottom * 120, leftup[1] + totalSpace + nameSize + 15 + setting_row_count * 25), name=setting[0], value=setting[1])
                    setting_row_count = setting_row_count + 1
                else:
                    reached_bottom = reached_bottom + 1
                    setting_row_count = 0

            totalSpace = totalSpace + space

        elif isVertical == False:
            space = (rightdown[0] - leftup[0] - (len(divisions) * 5) + 10) * (divisions[divisioncount] / totalDivNumber)
            create_rectangle((leftup[0] + totalSpace, leftup[1] + 5),(leftup[0] + totalSpace + space - 5, rightdown[1] - 5), color2)
            create_rectangle((leftup[0] + totalSpace + 3, leftup[1] + 8),(leftup[0] + totalSpace + space - 8, leftup[1] + nameSize), color3)
            create_text(str(names[divisioncount]), ((rightdown[0] + totalSpace + space + rightdown[0] + totalSpace) / 2 - (rightdown[0] - leftup[0]),  leftup[1] + 8 + nameSize / 2 - 4), color4, font=menuFont)

            totalSpace = totalSpace + space

        divisioncount = divisioncount + 1

#create setting display with
def create_setting(pos, name, value=None):
    create_text(str(name) + ": ",Centre=pos)
    if isinstance(value,(int, float)):
        create_text(str(f"{round(value, 2):>10}"), (pos[0] + 100, pos[1]), white)
    elif not value == None: 
        create_text(f"{str(value):>10}", (pos[0] + 100, pos[1]), white)
    else:
        create_text("None", (pos[0] + 100, pos[1]), white)


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


#create Baumgartner
Baumgartner = physics_object(name='Baumgartner',startposy=39045, startposx=200, startvelx=100, massa=80, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000)

#game loop
running = True
clock = pygame.time.Clock()

#initialize phisics objects
[instance.update() for instance in physics_object.instancelist]

#create buttons
#play = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
#                                             text='play',
#                                             manager=manager)

#run gui till the program is quitted
while running:
    #setup for frame time calculation
    StartTime = time.time()
    time_delta = clock.tick(60)/1000.0

    #event loop
    for event in pygame.event.get():
        #stop the program if someone exits
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())


#        if event.type == pygame_gui.UI_BUTTON_PRESSED:
#            if event.ui_element == play:
#                print('Hello World!')

    #    manager.process_events(event)

    #manager.update(time_delta)


    #clear screen
    screen.fill((0, 0, 0))

    #reload selected of
    selected_obj = set_selected_obj(Baumgartner)

    #create/update setting objects [[menu1["setting name", value],["setting2 name", value]...], 
    #                               [menu2["setting name", value]],
    #                               ...
    #                               ]
    object_settings = [[["Naam",selected_obj.name],["Massa",selected_obj.m],["Oppervlakte",selected_obj.opp],["StartHoogte", selected_obj.startposy],["PosX", selected_obj.posx],["Hoogte", selected_obj.posy],["Velocity x", selected_obj.vel[0]],["Velocity Y", selected_obj.vel[1]],["Luchtdruk",selected_obj.Luchtdruk]],
                        [["Fres", sqrt(selected_obj.Fres[0]**2 + selected_obj.Fres[1]**2)], ["Fz", selected_obj.Fz[1]], ["Flucht",sqrt(selected_obj.Flucht[0]**2 + selected_obj.Flucht[1]**2)]],
                        []]

    #menu blocks
    create_rectangle((10, 10),(710, 430))

    #setting menu
    create_menu((720, 10), (1190, 590), divisions=[3, 2], names=['Object', 'Krachten'], isVertical=True, settings=object_settings)
    create_menu((10, 440), (710, 590), isVertical=False, divisions=[1,2,1], names=["Grafiek", "Tijd", "Settings"])
    
    #update menus
    pygame.display.flip()
    #manager.draw_ui(screen)

    #counts total simulation steps
    TotalSteps = TotalSteps + 1
 
    #calculate new object state for every physics obj
    [instance.update() for instance in physics_object.instancelist]
    #draw the object to the screen and display its force vectors
    [instance.display_object() for instance in physics_object.instancelist]

    #draw the entire picture to the screen
    pygame.display.update()

    #calculate simulation time
    EndTime = time.time()

    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)

