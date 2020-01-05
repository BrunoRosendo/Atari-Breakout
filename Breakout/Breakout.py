from IPython import get_ipython             # clears variables before running
get_ipython().magic('reset -sf')

import random
import pygame
pygame.mixer.pre_init(44100, -16, 1, 512)   # reduces audio size
pygame.init()

winw = 1200                                 # window setup and sprites
winh = 700
blockw = 105
blockh = 28
playerw = 180
playerh = 25
radius = 11

balli = pygame.image.load('ball.png')
balli = pygame.transform.scale(balli, (2*radius, 2*radius))
win = pygame.display.set_mode((winw, winh))
pygame.display.set_caption("Atari Breakout")
softbrick = pygame.image.load('softbrick.png')
softbrick = pygame.transform.scale(softbrick, (blockw, blockh))
tough = pygame.image.load('tough.png')
tough = pygame.transform.scale(tough, (blockw, blockh))
ballbricki = pygame.image.load('ballbrick.png')
ballbricki = pygame.transform.scale(ballbricki, (blockw, blockh))
brickimg = [softbrick, tough]
bati = [pygame.image.load('bat1.png'), pygame.image.load('bat2.png'), pygame.image.load('bat3.png')]
bati = [pygame.transform.scale(x, (playerw, playerh)) for x in bati]
hpi = pygame.image.load('hp.png')
hpi = pygame.transform.scale(hpi, (30, 30))
background = pygame.image.load('background.jpg')
background = pygame.transform.scale(background, (winw, winh))
start = pygame.image.load('start.png')
start = pygame.transform.scale(start, (winw, winh))

music = pygame.mixer.music.load('music.wav')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
wall = pygame.mixer.Sound('wall.wav')
pygame.mixer.Sound.set_volume(wall, 0.3)
hit = pygame.mixer.Sound('hit.wav')
pygame.mixer.Sound.set_volume(hit, 0.3)
lost = pygame.mixer.Sound('lost.wav')
pygame.mixer.Sound.set_volume(lost, 0.25)
levelup = pygame.mixer.Sound('level.wav')

font = pygame.font.SysFont('comicsans', 40, True)
bigfont = pygame.font.SysFont('comicsans', 100, True)
clock = pygame.time.Clock()

def fstates():                  # function to put all ball states to false
    for ball in balls:
        ball.state1 = False
        ball.state2 = False
        ball.state3 = False
        ball.state4 = False

class player(object):                       # class which defines the player
    def __init__(self):      # always starts in the bottom middle of the screen
        self.x = winw // 2 - playerh // 2
        self.y = winh - winh // 10
        self.vel = 35
        self.counter = 0
        self.hp = 3
        
    def draw(self, win):                    # draws the player
        if self.counter >= 9:
            self.counter = 0
        win.blit(bati[self.counter // 3], (self.x, self.y))
        self.counter += 1
        hp = font.render(str(self.hp), 1, (255, 255, 255))
        win.blit(hp, (self.x + 100, self.y + 35))
        win.blit(hpi, (self.x + 60, self.y + 32))
        

class ball(object):                         # creates the first ball of the level
    def __init__(self, player, x, y, first = False):  # starts in control of the player if first
        if first:
            self.x = player.x + playerw // 2 - radius
            self.y = player.y - playerh
        else:
            self.x = x
            self.y = y
        self.first = first
        self.vel = 14
        self.state1 = False
        self.state2 = False
        self.state3 = False
        self.state4 = False
        self.counter = 0
            
    def draw(self, win):                         # draws the ball
        win.blit(balli, (self.x, self.y))
    
    def state(self, bat):                        # changes the ball's direction according to its state
        if self.state1:                          # also changes the ball's state
            self.x += self.vel
            self.y -= self.vel
            if self.x + 2*radius >= winw:
                wall.play()
                self.state1 = False
                self.state2 = True
            elif self.y <= 0:
                wall.play()
                self.state1 = False
                self.state4 = True
        elif self.state2:
            self.x -= self.vel
            self.y -= self.vel
            if self.x <= 0:
                wall.play()
                self.state2 = False
                self.state1 = True
            elif self.y <= 0:
                wall.play()
                self.state2 = False
                self.state3 = True
        elif self.state3:
            self.x -= self.vel
            self.y += self.vel
            if self.x <= 0:
                wall.play()
                self.state3 = False
                self.state4 = True
            elif self.y + 2*radius >= bat.y and self.y <= bat.y + playerh // 2:
                if bat.x + playerw >= self.x >= bat.x + playerw - 25:
                    wall.play()
                    self.state3 = False
                    self.state1 = True
                elif self.x > bat.x and self.x < bat.x + playerw:
                    wall.play()
                    self.state3 = False
                    self.state2 = True
        elif self.state4:
            self.x += self.vel
            self.y += self.vel
            if self.x + 2*radius >= winw:
                wall.play()
                self.state4 = False
                self.state3 = True
            elif self.y + 2*radius >= bat.y and self.y <= bat.y + playerh // 2:
                if bat.x - 5 <= self.x <= bat.x + 15:
                    wall.play()
                    self.state4 = False
                    self.state2 = True
                elif self.x > bat.x and self.x < bat.x + playerw:
                    wall.play()
                    self.state4 = False
                    self.state1 = True
    
    def pop(self, bricks):                                      # detects  all kinds of bricks and pops them/creates a new ball
        for brick in bricks:
            if self.x <= brick.x + blockw and self.x + 2*radius >= brick.x and \
               self.y + 2*radius >= brick.y and self.y <= brick.y + blockh:
                   if brick.toughness == 0 and self.counter == 0:
                       bricks.pop(bricks.index(brick))
                       wall.play()
                   elif self.counter == 0:
                       brick.toughness -= 1
                   wall.play()
                   if brick.ball and self.counter == 0:
                       self.counter = 17
                       newball = ball(bat, brick.x, brick.y)
                       num = random.randint(0, 1)
                       if self.state3:
                           newball.state3 = True
                       elif self.state4:
                           newball.state4 = True
                       elif num == 0:
                           newball.state1 = True
                       else:
                           newball.state2 = True
                       balls.append(newball)
                   if self.state1:
                       if self.x <= brick.x:
                           self.state1 = False
                           self.state2 = True
                       else:
                           self.state1 = False
                           self.state4 = True
                   elif self.state2:
                       if self.x >= brick.x + blockw - 10:
                           self.state2 = False
                           self.state1 = True
                       else:
                           self.state2 = False
                           self.state3 = True
                   elif self.state3:
                       if self.x >= brick.x + blockw - 10:
                           self.state3 = False
                           self.state4 = True
                       else:
                           self.state3 = False
                           self.state2 = True
                   elif self.state4:
                       if self.x <= brick.x:
                           self.state4 = False
                           self.state3 = True
                       else:
                           self.state4 = False
                           self.state1 = True
            else:
                if self.counter > 0:
                    self.counter -= 1

class brick(object):                              # creates a brick of given toughness (max 1)
    def __init__(self, x, y, toughness):
        self.x = x
        self.y = y
        self.toughness = toughness
        self.ball = False
    def draw(self, win):
        win.blit(brickimg[self.toughness], (self.x, self.y))

class ballbrick(object):                        # brick which creates a new ball when popped
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.toughness = 0
        self.ball = True
    def draw(self, win):
        win.blit(ballbricki, (self.x, self.y))


run = False
stop = True

def redraw():                              # redraw the window
    win.blit(background, (0, 0))
    bat.draw(win)
    for ball in balls:
        ball.draw(win)
    for brick in bricks:                    
        brick.draw(win)
    pygame.display.update()


def intro():                        # shown at the start and end of the level
    global run, bricks, level1, level2, level3, level4, level5, balls, fball, bat, stop
    intro = True
    stop = True
    while intro:
        clock.tick(35)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro = False
                run = False
        win.blit(start, (0, 0))
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if 500 + 200 > mouse[0] > 500 and 220 + 100 > mouse[1] > 220:           # buttons of quit and play
            pygame.draw.rect(win, (0, 210, 50), (500, 220, 200, 100))
            if click[0] == 1:
                intro = False
                run = True
                bricks = []
                for y in [50, 100, 150, 200, 250]:               # creates the matrix of lv1
                    for x in range(32, winw - 80, 130):
                        bricks.append(brick(x, y, 0))
                level1 = True
                level2 = False
                level3 = False
                level4 = False
                level5 = False
                bat = player()
                balls = [ball(bat, 0, 0, True)]
                fball = balls[0]
        else:
            pygame.draw.rect(win, (0, 150, 60), (500, 220, 200, 100))
        if 500 + 200 > mouse[0] > 500 and 370 + 100 > mouse[1] > 370:
            if click[0] == 1:
                intro = False
                run = False
            pygame.draw.rect(win, (0, 210, 50), (500, 370, 200, 100))
        else:
            pygame.draw.rect(win, (0, 150, 60), (500, 370, 200, 100))
        play = bigfont.render('Play', 1, (255, 255, 255))
        win.blit(play, (520, 240))
        qu = bigfont.render('Quit', 1, (255, 255, 255))
        win.blit(qu, (510, 390))
        pygame.display.update()

intro()
    
while run:                                  # main loop
    clock.tick(35)
    pygame.mouse.set_visible(0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
#    if keys[pygame.K_LSHIFT]:           # debugging tool
#        bricks = []
    if keys[pygame.K_LEFT] and bat.x > 27:   # control of the bat
        bat.x -= bat.vel
    if keys[pygame.K_RIGHT] and bat.x < winw - playerw - 30:
        bat.x += bat.vel
    if stop:                                # before clicking space
        fball = balls[0]
        fball.x = bat.x + playerw // 2 - radius
        fball.y = bat.y - playerh
        if keys[pygame.K_SPACE]:
            stop = False
            fball.state1 = True
    for bal in balls:
        if bal.y > winh:                       # when the ball goes out
            if len(balls) == 1:
                if bat.hp > 1:
                    hit.play()
                bat.hp -= 1
                pygame.time.delay(100)
                stop = True
                fstates()
                if bat.hp == 0:                          # player loses the game
                    pygame.mixer.music.set_volume(0)
                    lost.play()
                    pygame.time.delay(2000)
                    print('You lost')
                    run = False
            else:
                balls.pop(balls.index(bal))
    for bal in balls:
        bal.state(bat)
        bal.pop(bricks)
    if level1:
        if bricks == []:                         # conditions to check if the player ended the level
            level1 = False                       # also creates the matrix of the next level
            level2 = True
            stop = True
            fstates()
            levelup.play()
            pygame.time.delay(1000)
            balls = [ball(bat, 0, 0, True)]
            fball = balls[0]
            for y in [100, 250]:
                for x in range(50, winw - 100, 125):
                    bricks.append(brick(x, y, 0))
            for x in range(50, winw - 100, 125):
                bricks.append(brick(x, 175, 1))
    elif level2:
        if bricks == []:
            level2 = False
            level3 = True
            stop = True
            fstates()
            levelup.play()
            pygame.time.delay(1000)
            balls = [ball(bat, 0, 0, True)]
            fball = balls[0]
            for y in range(60, 480, 60):
                bricks.append(brick(200, y, 1))
                bricks.append(brick(winw - 300, y, 1))
            bricks.append(ballbrick(550, 60))
            bricks.append(ballbrick(550, 250))
            bricks.append(ballbrick(550, 420))
    elif level3:
        if bricks == []:
            level3 = False
            level4 = True
            stop = True
            fstates()
            levelup.play()
            pygame.time.delay(1000)
            balls = [ball(bat, 0, 0, True)]
            fball = balls[0]
            for x in range(400, winw - blockw, 5 + blockw):
                for y in range(40, 150, blockh + 5):
                    bricks.append(brick(x, y, 1))
            for x in range(5, winw - 600, 5 + blockw):
                for y in range(280, 390, blockh + 5):
                    bricks.append(brick(x, y, 0))
            bricks[15] = ballbrick(bricks[15].x, bricks[15].y)
            bricks[40] = ballbrick(bricks[40].x, bricks[40].y)
    elif level4:
        if bricks == []:
            level4 = False
            level5 = True
            stop = True
            fstates()
            levelup.play()
            pygame.time.delay(1000)
            balls = [ball(bat, 0, 0, True)]
            fball = balls[0]
            for x in range(winw - blockw, winw - 4* blockw - 25, -blockw - 5):
                bricks.append(brick(x, 40, 0))
            for x in range(winw - 3*blockw-10, winw - 7* blockw-25, -blockw-5):
                bricks.append(brick(x, 45+blockh, 0))
            for x in range(winw - 5*blockw-20, winw - 9* blockw-25, -blockw-5):
                bricks.append(brick(x, 50+2*blockh, 0))
            for x in range(0, 3*blockw+25, blockw+5):
                bricks.append(brick(x, 50 + 5*blockh, 1))
            for x in range(2*blockw + 10, 5*blockw+25, blockw + 5):
                bricks.append(brick(x, 50 + 6*blockh, 1))
            for x in range(4*blockw + 20, 7*blockw+25, blockw + 5):
                bricks.append(brick(x, 50 + 7*blockh, 1))
            for x in range(winw - blockw, winw - 4* blockw - 25, -blockw - 5):
                bricks.append(brick(x, 40 + 10*blockh, 0))
            for x in range(winw - 3*blockw-10, winw - 7* blockw-25, -blockw-5):
                bricks.append(brick(x, 45+11*blockh, 0))
            for x in range(winw - 5*blockw-20, winw - 9* blockw-25, -blockw-5):
                bricks.append(brick(x, 50+12*blockh, 0))
            for x, y in [(0, 0), (winw-blockw, 60+3*blockh), (0,  60 + 8*blockh)]:
                bricks.append(ballbrick(x, y))
    elif level5:
        if bricks==[]:
            levelup.play()
            pygame.time.delay(1000)
            pygame.mouse.set_visible(1)
            intro()
    redraw()

pygame.quit()
