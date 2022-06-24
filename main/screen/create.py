from math import *

from sqlalchemy import values
from settings.settings import *
from screen.calc import *

#texts
def create_text(text='text',Centre=None, maxcoords=((100, 100), (400, 200)), color=liteblue,font=fontfreesan, antialias=True, outline=None):
    text = str(text)
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

def create_line(coord1 = (100, 100), coord2 = (200,200), color=black, width = 2, text = None, textColor=None):
    pygame.draw.line(screen, color, coord1, coord2, width = width)
    length = hypot(coord2[0]-coord1[0], coord2[1]-coord1[1])
    
    if textColor == None:
        textColor = color
    
    textpos = ((coord1[0] +coord2[0]) / 2 - 10, (coord1[1] +coord2[1]) / 2 - 10)
    
    if text != None:
        create_text(text, textpos, color=textColor)

#give the start and end of an arrow you can set a text that will be in the centre
def create_arrow(begin=(100, 100), end=(200, 400), width=5, arrow_size=None, color=blue, text=None, textColor=None, textfont=fontfreesan, textposoffset=0):
    global screenXYratio
    
    if textColor == None:
        textColor = color    
    
    length = hypot(end[0]-begin[0], end[1]-begin[1])

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
def create_menu(leftup=(10, 10), rightdown=(100, 100), color1=gray, color2=litegray, color3=litergray, color4=liteblue, divisions=[1], names=['name'], isVertical=True, nameSize=30, settingValues=None, Font='freesansbold.ttf', fontTitelSize=20, fontSettingSize=15, settings=[{"Hoogte": "10", 'snelheid': '17'}, {'1' : 1, "2": '2'}]):
    
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

            currentSettingsKeys = list(settings[divisioncount].keys())
            currentSettingsValues = list(settings[divisioncount].values())


            for i in range(len(currentSettingsKeys)):
                if leftup[1] + totalSpace + nameSize + setting_row_count * 30 + 10 <= totalSpace + space: 
                    setting_row_count = setting_row_count + 1
                else:
                    reached_bottom = reached_bottom + 1
                    setting_row_count = 0

                create_text(str(currentSettingsKeys[i]), maxcoords=((leftup[0] + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2, leftup[1] + totalSpace + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                                                        (leftup[0] + (rightdown[0] - leftup[0]) / 4 + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2, leftup[1] + totalSpace + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25)))
                

                valueBox = ((leftup[0] + 10 + reached_bottom * (rightdown[0] - leftup[0]) / 2 + (rightdown[0] - leftup[0] - 30) / 4, leftup[1] + totalSpace + nameSize - 15 + setting_row_count * 25 + reached_bottom * 25), 
                            (leftup[0] + (rightdown[0] - leftup[0] - 20) / 2 + 10 + reached_bottom * (rightdown[0] - leftup[0] - 30) / 2, leftup[1] + totalSpace + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25))

                if isinstance(currentSettingsValues[i],(int, float)):
                    create_text(round(currentSettingsValues[i] * 1.00, 2), maxcoords=valueBox, color=white, outline="right")
                elif not currentSettingsValues[i] == None: 
                    create_text(str(currentSettingsValues[i]), maxcoords=valueBox, color=white, outline="right")
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
            
            currentSettingsKeys = list(settings[divisioncount])
            currentSettingsValues = list(settings[divisioncount].values())
            
            for i in range(len(settings[divisioncount])):
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

                create_text(str(currentSettingsKeys[i]), maxcoords=((leftup[0] + reached_bottom * (totalSpace + space) / 2 + totalSpace, leftup[1] + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                                                        (leftup[0] + reached_bottom * (totalSpace + space) / 2 + totalSpace + space / firstSettingSpacing, leftup[1] + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25)))
                

                valueBox = ((leftup[0] + reached_bottom * (totalSpace + space) + totalSpace + space / firstSettingSpacing, leftup[1] + nameSize - 20 + setting_row_count * 25 + reached_bottom * 25), 
                            (leftup[0] + reached_bottom * (totalSpace + space) + totalSpace + space / secondSettingSpacing - 10, leftup[1] + nameSize + 5 + setting_row_count * 25 + reached_bottom * 25))

                if isinstance(currentSettingsValues[i],(int, float)):
                    create_text(str(round(currentSettingsValues[i] * 1.00, 2)), maxcoords=valueBox, color=white, outline="right")
                elif not currentSettingsValues[i] == None: 
                    create_text(str(currentSettingsValues[i]), maxcoords=valueBox, color=white, outline="right")
                else:
                    create_text("None", maxcoords=valueBox, color=white, outline="right")

            totalSpace = totalSpace + space

        divisioncount = divisioncount + 1
        
def create_circle(center = (100, 100), radius= 100, width=4, color = white):
    pygame.draw.circle(screen, color,  center= center, radius= radius, width=width)     

def create_point(center = (100, 100), radius= 2, width=5, color = white):
    pygame.draw.circle(screen, color,  center= center, radius= radius, width=width)     


