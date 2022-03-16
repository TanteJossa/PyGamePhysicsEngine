import matplotlib as plt
import os
from time import time, sleep
import time
import pygame
from math import *
from physics.physics_object import *
from physics.other import *
from screen.create import *
from screen.calc import *
from settings.settings import *



#create Baumgartner
Baumgartner = PhysicsObject(name='Baumgartner',startposy=39045, startposx=200, startvelx=100, massa=80, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000, icon='skydiving')

# sun = PhysicsObject(name='sun', startposy=simfieldsizey / 2, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, useAirRes=False, useSolarSys=True)
# sun2 = PhysicsObject(name='sun2', startposy=simfieldsizey / 4 * 3, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, startvelx=30000, useAirRes=False, useSolarSys=True, icon='sun')

# mercury = PhysicsObject(name='mercury', startposy=sun.startposy, startposx=sun.startposx - 0.58e11, massa=3.285E23 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=47480)

# venus = PhysicsObject(name='venus', startposy=sun.startposy, startposx=sun.startposx - 1.08e11, massa=4.867E24 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=35020)

# earth = PhysicsObject(name='earth', startposy=sun.startposy, startposx=sun.startposx - 1.6e11, massa=5.97219e24, useParachute=False, useAirRes=False, startvelx=0, startvely=29780, useSolarSys=True)

# moon = PhysicsObject(name='moon', startposy=earth.startposy, startposx=earth.startposx - 3.844e9, massa=7.34767309e22 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=earth.vel[1], startvelx=1000)

# mars = PhysicsObject(name='mars', startposy=sun.startposy, startposx=sun.startposx - 2.28e11, massa=6.39E23, useParachute=False, useAirRes=False, startvelx=0, startvely=24130, useSolarSys=True)

#game loop
running = True
clock = pygame.time.Clock()

#initialize phisics objects
[instance.update() for instance in PhysicsObject.instancelist]

#reload selected of
set_selected_obj_name = Baumgartner

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
            
            for instance in PhysicsObject.instancelist:
                if instance.check_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) == True:
                    set_selected_obj_name = instance
#           new_obj = physics_object(name='new_obj', startposx=calc_pixel_to_game_coords(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])[0] ,startposy=calc_pixel_to_game_coords(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])[1] , massa=2 * 10 , useParachute=False, useAirRes=False, useSolarSys=True, startvelx=-20)


    #clear screen
    screen.fill((0, 0, 0))

    #reload selected of
    selected_obj = set_selected_obj(set_selected_obj_name)

    object_settings = [[["Naam",selected_obj.name],["Massa",selected_obj.m],["Oppervlakte",selected_obj.opp],["StartHoogte", selected_obj.startposy],["PosX", selected_obj.posx],["Hoogte", selected_obj.posy],["Velocity x", selected_obj.vel[0]],["Velocity Y", selected_obj.vel[1]],["Luchtdruk",selected_obj.Luchtdruk]],
                        [["Fres", sqrt(selected_obj.Fres[0]**2 + selected_obj.Fres[1]**2)], ["Fz", selected_obj.Fz[1]], ["Flucht",sqrt(selected_obj.Flucht[0]**2 + selected_obj.Flucht[1]**2)]],
                        []]

    undersettings = [[["Width", simfieldsizex],["Height", simfieldsizey]],
                        [["IRL time", TotalIRLTime], ["In Sim Time", str(round(TotalSteps / StepsPerSec / 3600)) + "Uur"]],
                        [["Arrow F size", Fmultiplier], ["Arrow Vel size", Velmultiplier]]]

    #menu blocks
    #setting menu

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
                
                for instance in PhysicsObject.instancelist:
                    currentGrav = currentGrav + (instance.m**2 * G) / ((instance.posx - pixelSimX)**2 + (instance.posy - pixelSimY)**2 + 0.0001)

                grav = currentGrav / maxGrav

                pixelcolor = (round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)))

                screen.fill(pixelcolor, ((10 + divisionX1, 10 + divisionY1), (divisionX2 - divisionX1, 10 + divisionY2)))      


    #counts total simulation steps
    TotalSteps = TotalSteps + 1
 
    #calculate new object state for every physics obj
    [instance.update() for instance in PhysicsObject.instancelist]

    #draw an arrow 

    [instance.draw_vel_arrow() for instance in PhysicsObject.instancelist]

    for instance in PhysicsObject.instancelist:
        if instance == selected_obj:
                instance.draw_force_arrows(enabledArrows, enabledArrowsColors)

    #draw the object icon on top to the screen and display its force vectors
    [instance.display_object() for instance in PhysicsObject.instancelist]

    #draw the entire picture to the screen
    pygame.display.update()

    #calculate simulation time
    EndTime = time.time()

    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)

