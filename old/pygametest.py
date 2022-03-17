 
from __future__ import division
from flask import Flask
import pygame
import pygame_gui
from pyparsing import col

#initialize game
pygame.init()


#create the screen
screenX = 1200
screenY = 1000

screen = pygame.display.set_mode((screenX, screenY))
gui_manager = pygame_gui.UIManager((screenX, screenY))

#caption and icon
pygame.display.set_caption("engine")

#create menu
hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                            text='Say Hello',
                                            manager=gui_manager)

#player
objectImg = pygame.image.load('object.png')
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

def create_menu(leftup=(10, 10), rightdown=(100, 100), color1=gray, color2=litegray, color3=litergray, color4=liteblue, divisions=[1], names=['name'], isVertical=True, nameSize=30):
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
            create_text(str(names[divisioncount]), ((leftup[0] + 8 + rightdown[0] - 8) / 2,  (leftup[1] + totalSpace + 3 + leftup[1] + totalSpace + nameSize) / 2), color=color4)
            totalSpace = totalSpace + space

        elif isVertical == False:
            space = (rightdown[0] - leftup[0] - (len(divisions) * 5) + 10) * (divisions[divisioncount] / totalDivNumber)
            create_rectangle((leftup[0] + totalSpace, leftup[1] + 5),(leftup[0] + totalSpace + space - 5, rightdown[1] - 5), color2)
            create_rectangle((leftup[0] + totalSpace + 3, leftup[1] + 8),(leftup[0] + totalSpace + space - 8, leftup[1] + nameSize), color3)
            
            create_text(str(names[divisioncount]), ((rightdown[0] + totalSpace + space + rightdown[0] + totalSpace) / 2 - (rightdown[0] - leftup[0]),  leftup[1] + 8 + nameSize / 2 - 4), color4)

            totalSpace = totalSpace + space

        divisioncount = divisioncount + 1
    

#game loop
running = True
clock = pygame.time.Clock()

while running:

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
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == hello_button:
                print('Hello World!')
            
        gui_manager

    gui_manager.update(time_delta)

    #menu blocks
    create_rectangle((10, 10), (710, 430))

    #setting menu
    create_menu((720, 10), (1190, 590), divisions=[3, 2], names=['Object', 'Krachten'], isVertical=True)
    create_menu((10, 440), (710, 590), isVertical=False, divisions=[1,2,1], names=["Grafiek", "Tijd", "Settings"])
    pygame.display.flip()



    gui_manager.draw_ui(screen)

    display_object()
    pygame.display.update()