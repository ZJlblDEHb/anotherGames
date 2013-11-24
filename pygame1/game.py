from __future__ import division

import sys, pygame

pygame.init()

size = width, height = 800, 600
speed = [2, 2]
SPEED_X = 2
black = 0, 0, 0
screen = pygame.display.set_mode(size)


class GameObject(object):
    def __init__(self, sprite, start_pos=(0, 0), destructible=False, is_desk=False):
        self.sprite = sprite
        self.rect = self.sprite.get_rect().move(start_pos)
        self.speed = [0, 0]
        self.destructible = destructible
        self.is_desk = is_desk

    def move(self):
        self.rect = self.rect.move(self.speed)

        if self.rect.right > width:
            self.rect.right = width
        elif self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > height:
            self.rect.bottom = height
        elif self.rect.top < 0:
            self.rect.top = 0


class BouncingGameObject(GameObject):
    def bounce(self):
        if self.rect.right == width or self.rect.left == 0:
            self.speed[0] = -self.speed[0]
        if self.rect.bottom == height or self.rect.top == 0:
            self.speed[1] = -self.speed[1]


class CollidingGameObject(BouncingGameObject):
    def collide(self, objects):
        was_changed = False
        for obj in objects:
            if obj == self:
                continue

            left, top, right, bottom = self.rect.left, self.rect.top, self.rect.right, self.rect.bottom
            o_left, o_top, o_right, o_bottom = obj.rect.left, obj.rect.top, obj.rect.right, obj.rect.bottom

            if right > o_left and left < o_right and top < o_bottom and bottom > o_top and not was_changed:
                was_changed = True
                self.speed[1] = -self.speed[1]
                if obj.is_desk:
                    center = self.rect.centerx
                    o_center = obj.rect.centerx
                    print center, o_center
                    o_width = obj.rect.width
                    if center > o_center:
                        x = SPEED_X * ((center - o_center) / (o_width / 2))
                        print x, center, o_center, o_width
                    elif center < o_center:
                        x = -1 * SPEED_X * (1 - ((center - o_left) / (o_width / 2)))
                        print x, center, o_center, o_width
                    else:
                        x = 0

                    self.speed[0] = x

                # Remove destructible object when collide
                if obj.destructible:
                    objects.remove(obj)


movable_objects = []
display_objects = []
collide_objects = []
bounce_objects = []

ball = CollidingGameObject(pygame.image.load("small_ball.gif"), (80, 560))
ball.speed = speed

movable_objects.append(ball)
display_objects.append(ball)
collide_objects.append(ball)
bounce_objects.append(ball)

desk = GameObject(pygame.image.load("desk.png"), (0, 560), False, True)

# add target blocks
for i in range(width // 40):
    for j in range((height - 300) // 20):
        display_objects.append(GameObject(pygame.image.load("block.png"), (i*40, j*20), True))

movable_objects.append(desk)
display_objects.append(desk)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                desk.speed[0] = -3
            #elif event.key == pygame.K_UP:
            #    ball.speed[1] = -3
            elif event.key == pygame.K_RIGHT:
                desk.speed[0] = 3
            #elif event.key == pygame.K_DOWN:
            #    ball.speed[1] = 3
        elif event.type == pygame.KEYUP:
            desk.speed = [0, 0]

    for obj in movable_objects:
        obj.move()

    for obj in bounce_objects:
        obj.bounce()

    for obj in collide_objects:
        obj.collide(display_objects)

    screen.fill(black)

    for obj in display_objects:
        screen.blit(obj.sprite, obj.rect)

    pygame.display.update()
    pygame.time.delay(10)
