"""
a doodle jump game base pygame package
created by Gilad Aharoni, 3/2022
"""
import pygame
import os
import random

pygame.font.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("doodDle jump")
BACKGROUND_COLOR = (255, 200, 255)
PLATFORM_C = (255, 0, 0)
PLATFORM = pygame.Rect(WIDTH / 2 - 5, 0, 10, HEIGHT)
FPS = 60
VEL = 5
ALIEN = pygame.image.load('C:\\Users\\gilad\\PycharmProjects\\doodle jump\\character.png')
TRA_ALIEN = pygame.transform.scale(ALIEN, (40, 55))


# the main component of the game.
class Level:
    def __init__(self):
        self.doodle = Doodle()
        self.score = ScoreBoard()
        self.platforms = Platform_Collection()
        self.game_over = False

    def draw(self):
        WIN.fill(BACKGROUND_COLOR)
        self.platforms.draw()
        self.doodle.draw()
        self.score.draw()

    def update(self):
        self.platforms.update(self.doodle, self.score)
        self.doodle.update(pygame.key.get_pressed())
        if self.doodle.position.y > HEIGHT or self.score.current_score > 50:
            self.game_over = True


# winning or losing screen
class InfoScreen:
    def __init__(self, caption: str):
        self.back_color = (0, 162, 255)
        self.title = pygame.font.Font('Bangers-Regular.ttf', 100).render(caption, True, (0, 0, 0))
        self.position = pygame.Rect(0 + WIDTH / 4, 0 + HEIGHT / 3, 3 * WIDTH / 4, 2 * HEIGHT / 3)
        # self.position.width = 175
        # self.position.height = 50

    def draw(self):
        WIN.fill(self.back_color)
        WIN.blit(self.title, self.position)


# score counter and display component
class ScoreBoard:
    def __init__(self):
        self.position = pygame.Rect(0, 0, 0, 0)
        self.position.width = 175
        self.position.height = 50
        self.current_score = 0
        self.color = (0, 0, 255)
        self.font = pygame.font.Font('Bangers-Regular.ttf', 50)

    def draw(self):
        # pygame.draw.rect(WIN, self.color, self.position)
        drawn = self.font.render("Score: " + str(self.current_score), True, (0, 0, 0))
        WIN.blit(drawn, self.position)

    def increase(self):
        self.current_score = self.current_score + 1


# the basic platform class, turn black where it is touched.
class Platform:
    def __init__(self, number):
        self.position = pygame.Rect(number, 300, 450, 250)
        self.color = (255, 0, 0)
        self.position.width = 100
        self.position.height = 30
        self.has_been_touch = False

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.position)

    def update(self):
        self.position.y = self.position.y + 1

    def check_collision(self, doodle):
        if doodle.get_position()[1] in range(self.position.y, self.position.y + 20) and \
                doodle.get_position()[0] in range(self.position.x, self.position.x + self.position.width):
            doodle.re_jump()
            return True
        return False


# abstract platform for additions like extra points, life points etc.
class Loaded_Platform(Platform):
    def __init__(self, number):
        super().__init__(number)
        self.avatar = None

    def draw(self):
        # need to draw the monster on the platform
        pass

    def update(self):
        self.avatar.y = self.avatar.y + 1

    def check_collision(self, doodle):
        if super().check_collision(doodle) and super().has_been_touch == False:
            doodle.re_jump()


# a platform that also moves horizontaly.
class Mover(Platform):
    def __init__(self, number):
        super().__init__(random.randrange(0, WIDTH))
        self.direction = True

    def update(self):
        super().update()
        if self.position.x + self.position.width == WIDTH and self.direction:
            self.direction = False
        if self.position.x - 1 == 0 and not self.direction:
            self.direction = True
        if self.direction:
            self.position.x = self.position.x + 1
        else:
            self.position.x = self.position.x - 1


# platform that dissolved by touche
class Dissolve(Platform):
    def __init__(self, number):
        super().__init__(number)
        self.has_been_touch = False

    def check_collision(self, doodle):
        if self.has_been_touch:
            return False
        else:
            if super().check_collision(doodle):
                self.has_been_touch = True
                return True
            return False

    def draw(self):
        if self.has_been_touch:
            return
        else:
            super().draw()


# create variations of platforms by the current score.
class PlatformMaker:
    def __init__(self):
        self.dictionary = {1: Platform, 2: Mover, 3: Dissolve}

    def create_platform(self, score_board: int) -> Platform:
        if score_board in range(0, 10):
            return self.dictionary.get(1)(random.randrange(0, WIDTH - 100, 20))
        if score_board in range(10, 20):
            d = random.choices([1, 2, 3], [0.9, 0.05, 0.05])
            return self.dictionary.get(d[0])(random.randrange(0, WIDTH - 100, 20))
        if score_board in range(20, 40):
            d = random.choices([1, 2, 3], [0.5, 0.25, 0.25])
            return self.dictionary.get(d[0])(random.randrange(0, WIDTH - 100, 20))
        if score_board in range(40, 55):
            d = random.choices([1, 2, 3], [0.3, 0.35, 0.35])
            return self.dictionary.get(d[0])(random.randrange(0, WIDTH - 100, 20))
        if score_board > 55:
            d = random.choices([1, 2, 3], [0, 0.5, 0.5])
            return self.dictionary.get(d[0])(random.randrange(0, WIDTH - 100, 20))


# group of the active platforms on the screen
class Platform_Collection:
    def __init__(self):
        self.collection = []
        self.clock_space = 0
        self.maker = PlatformMaker()
        for i in range(1, 10, 1):
            p = self.maker.create_platform(0)
            p.position.y = i * 90
            self.collection.append(p)

    def update(self, doodle, score: ScoreBoard):
        if self.clock_space > 0:
            self.clock_space = self.clock_space + 1
        if self.clock_space == 25:
            d = self.maker.create_platform(score.current_score)
            d.position.y = -20
            self.collection.append(d)
        for p in self.collection:
            if p.check_collision(doodle):
                p.color = (0, 0, 0)
                doodle.re_jump()
                if not p.has_been_touch:
                    p.has_been_touch = True
                    score.increase()
            p.update()
            if p.position.y > HEIGHT:
                self.collection.remove(p)
                self.clock_space = 1

    def draw(self):
        for platform in self.collection:
            platform.draw()


# the player
class Doodle:
    def __init__(self):
        self.position = pygame.Rect(430, 300, 450, 250)
        self.clock = 0

    def update(self, keys_pressed):
        self.jump()
        if keys_pressed[pygame.K_RIGHT]:
            self.position.x = (self.position.x + VEL) % WIDTH
        if keys_pressed[pygame.K_LEFT]:
            self.position.x = (self.position.x - VEL) % WIDTH
        # something with automatic jumps and notice platforms

    def draw(self):
        WIN.blit(TRA_ALIEN, (self.position.x, self.position.y))

    def get_position(self):
        return [self.position.x + 20, self.position.y + 55]

    def jump(self):

        # need to figure out the perfect quad theorem
        if self.clock < 40:
            self.position.y = self.position.y - 4
        else:
            self.position.y = self.position.y + 3
        self.clock = self.clock + 1

    def re_jump(self):
        self.clock = 0


def main():
    my_level = Level()
    clock = pygame.time.Clock()
    run = True
    # main animation loop
    while not my_level.game_over and run:
        # set the fps of the game
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        my_level.draw()
        pygame.display.update()
        my_level.update()
    if not run:
        pygame.quit()
    else:
        if my_level.score.current_score > 55:
            finish = InfoScreen("You Win!")
        else:
            finish = InfoScreen("You lose :(")
        while run:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            finish.draw()
            pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
