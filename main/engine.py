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

#create objects
Baumgartner = PhysicsObject(name='Baumgartner',startposy=39045, startposx=200, startvelx=100, massa=80, opp=2, drag=0.7, useParachute=True, parachuteOpp=42.6, parachuteDrag=1.75, parachuteDeployTime=5, parachuteDeployHeight=3000, icon='skydiving')

# sun = PhysicsObject(name='sun', startposy=simfieldsizey / 2, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, useAirRes=False, useSolarSys=True)
# sun2 = PhysicsObject(name='sun2', startposy=simfieldsizey / 4 * 3, startposx=simfieldsizex / 2, massa=4e30 , useParachute=False, startvelx=30000, useAirRes=False, useSolarSys=True, icon='sun')

# mercury = PhysicsObject(name='mercury', startposy=sun.startpos[1], startposx=sun.startpos[0] - 0.58e11, massa=3.285E23 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=47480)

# venus = PhysicsObject(name='venus', startposy=sun.startpos[1], startposx=sun.startpos[0] - 1.08e11, massa=4.867E24 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=35020)

# earth = PhysicsObject(name='earth', startposy=sun.startpos[1], startposx=sun.startpos[0] - 1.6e11, massa=5.97219e24, useParachute=False, useAirRes=False, startvelx=0, startvely=29780, useSolarSys=True)

# moon = PhysicsObject(name='moon', startposy=earth.startpos[1], startposx=earth.startpos[0] - 3.844e9, massa=7.34767309e22 , useParachute=False, useAirRes=False, useSolarSys=True, startvely=earth.vel[1], startvelx=1000)

# mars = PhysicsObject(name='mars', startposy=sun.startpos[1], startposx=sun.startpos[0] - 2.28e11, massa=6.39E23, useParachute=False, useAirRes=False, startvelx=0, startvely=24130, useSolarSys=True)

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

    #reload selected of
    selected_obj = set_selected_obj(set_selected_obj_name)



    #event loop
    for event in pygame.event.get():

        #reset the spring force for every object
        for instance in PhysicsObject.instancelist:
            instance.setSpring((0, 0))

        #stop the program if someone exits
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(str(pygame.mouse.get_pos()) + str((calc_pixel_to_game_coords(pygame.mouse.get_pos()[0]), calc_pixel_to_game_coords(y=pygame.mouse.get_pos()[1]))))

            #setup for draw arrow creation
            last_mous_clickpos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            selected_an_obj = False
            mousePressed = True
            last_click_selected_obj = False
            mouseHoldLength = 0

            #if you click on an object select that object
            for instance in PhysicsObject.instancelist:
                if instance.check_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) == True:
                    set_selected_obj_name = instance
                    selected_obj = set_selected_obj(set_selected_obj_name)

                    selected_an_obj = True
                    
                    last_click_selected_obj = True
            
            #set the start of the arrow if a player drags in an open space (or on an object)
            click_arrow_start = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        if event.type == pygame.MOUSEBUTTONUP:
            mousePressed = False

    #check if someone is pulling on an object
    if last_click_selected_obj == True and mouseHoldLength > 0.3:
        drawSpringArrow = True
    else:
        drawSpringArrow = False
    
    #draw an arrow when somone drags the screen
    if mousePressed == True:
        mouseHoldLength = mouseHoldLength + time_delta
        print(mouseHoldLength)

        last_mous_pos = pygame.mouse.get_pos()
        click_arrow_end = pygame.mouse.get_pos()
        if drawSpringArrow:
            click_arrow_start = (selected_obj.objectX + 10, selected_obj.objectY + 10)

    #draw set the spring force for an object if it is pulled on
    if drawSpringArrow:
        click_arrow_start = (selected_obj.objectX + 10, selected_obj.objectY + 10)

        springlengthX = calc_pixel_to_game_coords(click_arrow_start[0]) - calc_pixel_to_game_coords(click_arrow_end[0]) 
        springlengthY =  calc_pixel_to_game_coords(click_arrow_end[1]) - calc_pixel_to_game_coords(click_arrow_start[1]) 
        NewFspring = [springlengthX * -clickSpringConstant * springMultiplier, springlengthY * -clickSpringConstant * springMultiplier]
        for instance in PhysicsObject.instancelist:
            if instance == selected_obj:
                instance.setSpring(NewFspring)
        

    #clear screen
    screen.fill((0, 0, 0))

    #menu settings
    object_settings = [{"Naam" : selected_obj.name, "Massa": selected_obj.m, "Oppervlakte" : selected_obj.opp, "StartHoogte" : selected_obj.startposy, "PosX" : selected_obj.posx, "Hoogte" : selected_obj.posy, "Velocity x":  selected_obj.vel[0], "Velocity Y": selected_obj.vel[1], "Luchtdruk": selected_obj.Luchtdruk},
                        {"Fres": sqrt(selected_obj.Fres[0]**2 + selected_obj.Fres[1]**2), "Fz" : selected_obj.Fz[1], "Flucht" : sqrt(selected_obj.Flucht[0]**2 + selected_obj.Flucht[1]**2)},
                        {}]

    undersettings = [{"Width" : simfieldsizex, "Height": simfieldsizey},
                     {"IRL time": TotalIRLTime, "In Sim Time": str(round(TotalSteps / StepsPerSec / 3600)) + "Uur"},
                     {"Arrow F size" : Fmultiplier, "Arrow Vel size": Velmultiplier}]


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

    
    #draw the menu's
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
        #divide the simfield in a x and y grid
        for divisionx in range(gravDivisions):
            for divisiony in range(gravDivisions):
                currentGrav = 0.0
                
                #calculate the coordintes of the current region
                divisionX1 = (simFieldX2 - simFieldX1) / gravDivisions * (divisionx) - 1
                divisionX2 = (simFieldX2 - simFieldX1) / gravDivisions * (divisionx +  1)
                divisionY1 = (simFieldY2 - simFieldY1) / gravDivisions * (divisiony) - 1
                divisionY2 = (simFieldY2 - simFieldY1) / gravDivisions * (divisiony + 1)
                
                #calculate the centre of the current block in the grid
                pixelSimX = calc_pixel_to_game_coords(x=(divisionX2 + divisionX1) / 2)
                pixelSimY = calc_pixel_to_game_coords(y=(divisionY2 + divisionY1) / 2 )
                
                #calculate the gravity
                for instance in PhysicsObject.instancelist:
                    currentGrav = currentGrav + (instance.m**2 * G) / ((instance.pos[0] - pixelSimX)**2 + (instance.pos[1] - pixelSimY)**2 + 0.0001)
                grav = currentGrav / maxGrav

                #set the color
                pixelcolor = (round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)), round(clamp(grav*255, 0, 255)))
                #apply to the screen (this function makes it lag)
                screen.fill(pixelcolor, ((10 + divisionX1, 10 + divisionY1), (divisionX2 - divisionX1, 10 + divisionY2)))      


    #counts total simulation steps
    TotalSteps = TotalSteps + 1
 
    #calculate new object state for every physics obj
    [instance.update() for instance in PhysicsObject.instancelist]

    #draw the velocity arrows behind the objects
    [instance.draw_vel_arrow() for instance in PhysicsObject.instancelist]

    #draw the force arrow if an object is selected
    for instance in PhysicsObject.instancelist:
        if instance == selected_obj:
                instance.draw_force_arrows(enabledArrows, enabledArrowsColors)

    #draw new obj arrow
    if drawSpringArrow:
        create_arrow(click_arrow_start, click_arrow_end)
    elif mousePressed == True and drawSpringArrow != True:
        create_arrow(click_arrow_start, click_arrow_end)
        
    #draw the object icon on top to the screen and display its force vectors
    [instance.display_object() for instance in PhysicsObject.instancelist]

    #draw the entire picture to the screen
    pygame.display.update()

    #calculate simulation time
    EndTime = time.time()

    TotalIRLTime = TotalIRLTime + (time.time() - StartTime)

