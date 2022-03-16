from time import time, sleep
import time
from matplotlib import pyplot as plt
import math
import os

#Settings
#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 10
#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 100

#Zwaartekracht
Zw = -9.81

#setup simulation
TotalIRLTime = 0
id = 1
TotalSteps = 0

class object():

    #s = positie (hoogte)
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    def __init__(self, name, massa=80, hoogte=0, oppervlak=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000):
        global id
        
        #setup object
        self.name = name
        self.id = id
        id = id + 1
        self.m = massa
        self.s = hoogte
        self.opp = oppervlak
        self.drag = drag

        self.useParachute = useParachute
        self.parachuteOpp = parachuteOpp
        self.parachuteDrag = parachuteDrag
        self.parachuteDeployHeight = parachuteDeployHeight
        self.parachuteDeployTime = parachuteDeployTime

        self.v = 0
        self.parachuteStep = 0.00
        self.pasts = []
        self.pastv = []
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

        if self.s < self.parachuteDeployHeight and self.useParachute == True: 
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
        Luchtdruk = calc_luchtdruk(self.s, Zw, Temp=4)
        Flucht = calc_flucht(Luchtdruk, self.v, valopp, valdrag)


        #Tel alle krachten bij elkaar  op
        Fres = (Fz + Flucht)
        
        #Tel Fres op bij de snelheid en deel door massa a = F/m
        self.v = self.v + (Fres / StepsPerSec / self.m)

        #Verander de positie met de snelheid, als een object niet op de grond ligt
        if self.s > 0:
            self.s = self.s + (self.v / StepsPerSec)
            print("Current Height: " + str(round(self.s, 2)) + f"{'Current Speed: '  + str(round(self.v, 2)) + 'm/s':>40}" + f"{'Current Fres Per Sec: '  + str(round(Fres, 2)) + 'n':>40}" + f"{'Flucht Per Sec: ' + str(round(Flucht, 2)) + 'n':>40}" + f"{'Tijd in Sim: ' + str(round(TotalSteps / StepsPerSec, 2)):>30}" + f"{'IRL Tijd: ' + str(round(TotalIRLTime, 2)) + 's':>20}")

        #Als een object op de grond ligt beweegt het object niet verder naar beneden
        if self.s <= 0:
            self.s = 0
            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s" + "          " + "Finished Sim in: " + str(round(TotalIRLTime, 2)))
            
            #maak st-grafiek 
            plot_data("hoogte",self.name, self.paststep, self.pasts, 'Tijd (sec)', 'Hoogte (m)')

            #maak vt-grafiek
            plot_data("snelheid", self.name, self.paststep, self.pastv, "Tijd (sec)", "Snelheid (m/s)")

            #Als het object geland is stopt het programma
            exit()

        #save data voor grafiek
        self.pasts.append(self.s)
        self.pastv.append(self.v)
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

def update():
    global TotalSteps
    global TotalIRLTime

    #telt totaal aantal stappen in simulatie
    TotalSteps = TotalSteps + 1
    
    #bereken later hoe lang de berekening kostte
    StartTime = time.time()

    Baumgartner.update()

    #bereken later hoe lang de berekening kostte
    EndTime = time.time()

    #sqrt(()^2) zorgt dat er geen negatieve sleep time kan komen 
    sleep(math.sqrt((1.00 / StepsPerSec / SpeedMultiplier - (EndTime - StartTime)) ** 2))

    #berekend echte tijd
    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)


#object settings
Baumgartner = object(name='Baumgartner',massa=80, hoogte=39045, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000)


#Runt het programma tot "exit()"
while True:
    update()


