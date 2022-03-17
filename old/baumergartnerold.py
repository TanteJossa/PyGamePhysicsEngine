from time import time, sleep

class object():
    #s = positie
    #v = snelheid
    #m = massa
    #Fres = kracht die wordt uitgeoefend op een object in deze TimeStep

    def __init__(self):
        self.v = 0.00
        self.s = 0.00
        self.m = 1.00

    def set_s(self, s):
        self.s = s
        return self.s

    def get_s(self):
        return self.s

    def set_v(self, v):
        self.v = v
        return self.v

    def get_v(self):
        return self.v

    def set_m(self, m):
        self.m = m
        return self.m

    def get_m(self):
        return self.m

    def update(self):
        global Zw
        global StepsPerSec
        global TotalSteps
        global SpeedMultiplier

        #Fz = Zw * m
        Fz = Zw * self.m

        #Tel alle krachten bij elkaar  op
        Fres = Fz

        #Tel Fres op bij de snelheid
        self.v = self.v + (Fres / StepsPerSec / self.m)

        #Verander de positie met de snelheid, als een object niet op de grond ligt
        if self.s > 0:
            self.s = self.s + (self.v / StepsPerSec)
            print("Current Height: " + str(round(self.s, 2)) + f"{'Current Speed: '  + str(round(self.v, 2)) + 'm/s':>50}" + f"{'Current Fres per Sec: '  + str(round(Fres, 2)) + 'n':>50}")

        #Als een object op de grond ligt beweegt het object niet verder naar beneden
        if self.s <= 0:
            self.s = 0
            print("Landed after: " + str(round(TotalSteps / StepsPerSec, 2)) + "s")
            
            #Als het object geland is stopt het programma
            exit()

def update():
    global TotalSteps
    global SpeedMultiplier

    TotalSteps = TotalSteps + 1

    Baumgartner.update()
    sleep(1.00 / StepsPerSec / SpeedMultiplier)

#Houdt bij hoelang Baumgartner aan het vallen was
TotalSteps = 0

#In hoeveel aparte berekeningen de animatie wordt opgedeeld per seconde
StepsPerSec = 30

#Hoeveel gesimuleerde secondes in een echte seconde voorkomen
SpeedMultiplier = 100


#Zwaartekracht
Zw = -9.81

Baumgartner = object()
Baumgartner.set_s(39045.00)
Baumgartner.set_m(80)

while True:
    update()

