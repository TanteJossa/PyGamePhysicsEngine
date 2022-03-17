from screen.create import create_arrow
from settings.settings import *
from physics.calc import *
import pygame

#CLASSES
#physics
class PhysicsObject():
    #
    #s = positie (hoogte)
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    instancelist = []

    def __init__(self, name, startposx=200, startposy=39045, massa=80, startvelx=0.0, startvely=0.0, colboxX=16, colboxY=16, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000, useAirRes=True, useSolarSys=False, icon=None):
        global id

        PhysicsObject.instancelist.append(self)
        
        #setup object
        self.name = name
        self.id = id
        id = id + 1
        self.m = massa
        self.pos = [startposx, startposy]
        self.startpos = [startposx, startposy]
        self.opp = opp
        self.drag = drag
        self.Fres = [0, 0]
        self.Fzw = [0, 0]
        self.Fz = [0, 0]
        self.Fspring = [0, 0]
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
    
    def setSpring(self, spring=[0, 0]):
        self.Fspring = spring

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
        self.pos[0] = self.pos[0] + (self.vel[0] / StepsPerSec)

        if self.pos[1] > 0:
            self.pos[1] = self.pos[1] + (self.vel[1] / StepsPerSec)
        elif self.pos[1] < 0:
            self.pos[1] = 0
          
        self.calc_onscreen_pos()

  
    def calc_onscreen_pos(self):
        global  simFieldX1
        global  simFieldY1
        global  simFieldX2    
        global  simFieldY2
        global  simfieldsizex
        global  simfieldsizey

        self.objectY = 10 + (simFieldY2 - simFieldY1) * ((simfieldsizey - self.pos[1]) / simfieldsizey)
        self.objectX = 10 + (simFieldX2 - simFieldX1) * (self.pos[0] / simfieldsizex)
        return (self.objectX, self.objectY)
      
    
    def display_object(self):
        global TotalSteps
        global StepsPerSec

        self.calc_onscreen_pos()

        self.calc_pos()

        if self.icon == 'skydiving':
            if self.pos[1] < self.parachuteDeployHeight:
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
        if self.pos[1] < self.parachuteDeployHeight and self.useParachute == True: 
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
          self.Luchtdruk = calc_luchtdruk(self.pos[1], Zw, Temp=4)
          self.Flucht = (calc_flucht(self.Luchtdruk, v=self.vel[0], A=self.opp, drag=self.drag), calc_flucht(self.Luchtdruk, v=self.vel[1], A=self.opp, drag=self.drag))
        else:
          self.Flucht = (0, 0)

        self.Fzw = (0, 0)

        if self.useSolarSys == True:
            #calc zw
            for instance in PhysicsObject.instancelist:
                if not instance.id == self.id:
                    gravity = calc_gravity(self, instance)
                    self.Fzw = (self.Fzw[0] + gravity[0], self.Fzw[1] + gravity[1])

        #Tel alle krachten bij elkaar  op
        self.Fres = (self.Fz[0] + self.Flucht[0] + self.Fzw[0] + self.Fspring[0], self.Fz[1] + self.Flucht[1] + self.Fzw[1] + self.Fspring[1])
        
        #Tel Fres op bij de snelheid en deel door massa a = F/m
        self.vel = (self.vel[0] + (self.Fres[0] / StepsPerSec / self.m), self.vel[1] + (self.Fres[1] / StepsPerSec / self.m))
        
        #apply forces and calculate pos
        self.calc_pos()
        
        #print("Current Height: " + str(round(self.pos[1], 2)) + f"{'Current Speed: '  + str(round(float(self.vel[0]), 2)) + 'm/s':>30}" + f"{'Current Fres Per Sec: '  + str(round(float(self.Fres[0]), 2)) + 'n':>40}" + f"{'Flucht Per Sec: ' + str(round(float(self.Flucht[0]), 2)) + 'n':>40}" + f"{'Tijd in Sim: ' + str(round(TotalSteps / StepsPerSec, 2)):>30}" + f"{'IRL Tijd: ' + str(round(TotalIRLTime, 2)) + 's':>20}")
        
        #Als een object op de grond ligt beweegt het object niet verder naar beneden
#        if self.pos[1] <= 0:
#            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s" + "          " + "Finished Sim in: " + str(round(TotalIRLTime, 2)))
            
            #maak st-grafiek 
#            plot_data("hoogte",self.name, self.paststep, self.pasty, 'Tijd (sec)', 'Hoogte (m)')

            #maak vt-grafiek
#            plot_data("snelheid", self.name, self.paststep, self.pastvely, "Tijd (sec)", "Snelheid (m/s)")

        #save data voor grafiek
        self.pastx.append(self.pos[0])
        self.pasty.append(self.pos[1])
        self.pastvelx.append(self.vel[0])
        self.pastvely.append(self.vel[1])
        self.paststep.append(TotalSteps / StepsPerSec)
