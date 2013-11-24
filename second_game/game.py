import os
import sys
from random import randint

try:
    from sdl2 import *
    import sdl2.ext as sdl2ext
except ImportError:
    import traceback
    traceback.print_exc()
    sys.exit(1)


WHITE = sdl2ext.Color(255, 255, 255)


class SoftwareRenderer(sdl2ext.SoftwareSpriteRenderer):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2ext.fill(self.surface, sdl2ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)


class Player(sdl2ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai


class Score(sdl2ext.Entity):
    def __init__(self, world, sprite):
        self.sprite = sprite


class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False
        self.score = 0


class TrackingAIController(sdl2ext.Applicator):
    def __init__(self, miny, maxy):
        super(TrackingAIController, self).__init__()
        self.componenttypes = (PlayerData, Velocity, sdl2ext.Sprite)
        self.miny = miny
        self.maxy = maxy
        self.ball = None

    def process(self, world, componentsets):
        for pdata, vel, sprite in componentsets:
            if not pdata.ai:
                continue

            centery = sprite.y + sprite.size[1] // 2
            if self.ball.velocity.vx < 0:
                # ball is moving away from the AI
                if centery < self.maxy // 2:
                    vel.vy = 3
                elif centery > self.maxy // 2:
                    vel.vy = -3
                else:
                    vel.vy = 0
            else:
                bcentery = self.ball.sprite.y + self.ball.sprite.size[1] // 2
                if bcentery < centery:
                    vel.vy = -3
                elif bcentery > centery:
                    vel.vy = 3
                else:
                    vel.vy = 0


class MovementSystem(sdl2ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = (Velocity, sdl2ext.Sprite)
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight
            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


class Ball(sdl2ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()


class CollisionSystem(sdl2ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy, ball_pos_x, ball_pos_y):
        super(CollisionSystem, self).__init__()
        self.componenttypes = (Velocity, sdl2ext.Sprite)
        self.ball = None
        self.ball_pos_x = ball_pos_x
        self.ball_pos_y = ball_pos_y
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.player1 = None
        self.player2 = None

    def _overlap(self, item):
        pos, sprite = item[0], item[1]
        if sprite == self.ball.sprite:
            return False

        left, top, right, bottom = sprite.area
        bleft, btop, bright, bbottom = self.ball.sprite.area

        return bleft < right and bright > left and \
            btop < bottom and bbottom > top

    def _reset_position(self):
        random = randint(1, 2)
        if random == 1:
            random_speed = 3
        else:
            random_speed = -3

        self.ball.sprite.position = self.ball_pos_x, self.ball_pos_y
        self.ball.velocity.vx = random_speed
        self.ball.velocity.vy = 0

    def _score(self):
        if self.ball.sprite.x <= self.minx:
            self.player1.playerdata.score += 1
        else:
            self.player2.playerdata.score += 1

    def process(self, world, componentsets):
        collitems = [comp for comp in componentsets if self._overlap(comp)]
        if len(collitems) != 0:
            self.ball.velocity.vx = -self.ball.velocity.vx

            sprite = collitems[0][1]
            ballcentery = self.ball.sprite.y + self.ball.sprite.size[1] // 2
            halfheight = sprite.size[1] // 2
            stepsize = halfheight // 10
            degrees = 0.7
            paddlecentery = sprite.y + halfheight
            if ballcentery < paddlecentery:
                factor = (paddlecentery - ballcentery) // stepsize
                self.ball.velocity.vy = -int(round(factor * degrees))
            elif ballcentery > paddlecentery:
                factor = (ballcentery - paddlecentery) // stepsize
                self.ball.velocity.vy = int(round(factor * degrees))
            else:
                self.ball.velocity.vy = - self.ball.velocity.vy

        if self.ball.sprite.y <= self.miny or \
                self.ball.sprite.y + self.ball.sprite.size[1] >= self.maxy:
            self.ball.velocity.vy = - self.ball.velocity.vy

        if self.ball.sprite.x <= self.minx or \
                self.ball.sprite.x + self.ball.sprite.size[0] >= self.maxx:
            self._score()
            self._reset_position()


def run():
    # print sdl2ext.get_image_formats()
    # return
    sdl2ext.init()
    window = sdl2ext.Window("The Pong Game", size=(800, 600))
    window.show()

    world = sdl2ext.World()

    factory = sdl2ext.SpriteFactory(sdl2ext.SOFTWARE)
    sp_ball = factory.from_color(WHITE, size=(20, 20))
    sp_paddle1 = factory.from_color(WHITE, size=(20, 100))
    sp_paddle2 = factory.from_color(WHITE, size=(20, 100))


    movement = MovementSystem(0, 0, 800, 600)
    collision = CollisionSystem(0, 0, 800, 600, 390, 290)
    aicontroller = TrackingAIController(0, 600)

    spriterenderer = SoftwareRenderer(window)

    world.add_system(aicontroller)
    world.add_system(movement)
    world.add_system(collision)
    world.add_system(spriterenderer)

    player1 = Player(world, sp_paddle1, 0, 250)
    player2 = Player(world, sp_paddle2, 780, 250, True)

    ball = Ball(world, sp_ball, 390, 290)
    ball.velocity.vx = -3

    collision.ball = ball
    aicontroller.ball = ball

    collision.player1 = player1
    collision.player2 = player2

    running = True
    while running:
        events = sdl2ext.get_events()
        for event in events:
            if event.type == SDL_QUIT:
                running = False
                break
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.sym == SDLK_UP:
                    player1.velocity.vy = -3
                elif event.key.keysym.sym == SDLK_DOWN:
                    player1.velocity.vy = 3
            elif event.type == SDL_KEYUP:
                if event.key.keysym.sym in (SDLK_UP, SDLK_DOWN):
                    player1.velocity.vy = 0
        SDL_Delay(10)
        world.process()
    return 0

if __name__ == "__main__":
    sys.exit(run())