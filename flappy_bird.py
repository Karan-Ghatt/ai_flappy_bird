# aI bot that plays flappy bird
# making game too

import pygame
import neat
import time
import os
import random
pygame.font.init()

# import all images and configuring them to the size of window
WIN_WIDTH = 500
WIN_HIEGHT = 800

GEN = 0

# loading the images used to make the bird animation
# scalex2 used to make the image larger
# list index; birdimage1 = etc.
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]


PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("Arial", 45)

class Bird:
    IMGS = BIRD_IMAGES
    # Game constants
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # Start position of bird
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # method for jumping animation/movement

    def jump(self):
        # negative velocity bcs top left of window is origin (0,0);
        # to move up = negative velocity
        # to move up = positive velocity
        self.vel = -10.5
        # tick count keeps track of when we last jumped/number of jumps
        self.tick_count = 0
        # height keeps track of bird origin
        self.height = self.y

    # method used for all movement animation
    # to be used in game loop so we can call bird object in loop and use this method
    # to calculate the position of the bird and, where it should be going
    def move(self):
        # a game frame/move has occured - how many moves since last jump
        self.tick_count += 1
        # dispacement (d) is how many pixles to move image up/down in this frame
        # equation: based on current birds velocity, how much movement
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # velocity bounds/terminal velocity
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        # new y position
        self.y = self.y + d

        # angle of bird
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2


        # Tilt function - rotates image around center of image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=
                                     (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # method used for collision detection between objects
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        # If bird has passed by pip
        self.passed = False
        self.set_height()

    # method used to define height of pipe
    def set_height(self):
        self.height = random.randrange(40, 400)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # method for moving the pipes
    def move(self):
        self.x -= self.VEL

    # drawing pipes
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        # mask for top/bottom pipe
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # calculating if masks overlap - gets first point of overlap of
        # bottom mask and bottom offer, if no collision then function returns None
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # if returned value is not None therefore a collision has occurred
        if t_point or b_point:
            #print("boom")
            return True
        #print("gg")
        return False


## class for background base to move base
class Base:
    VEL = 5
    WIDTH = BASE_IMAGE.get_width()
    IMG = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds, pipes, base, score, generations, no_birds):
    win.blit(BG_IMAGE, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    # adding score to output window
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # adding generation to output window
    text = STAT_FONT.render("Gen: " + str(generations), 1, (255,255,255))
    win.blit(text, (10, 10))

    # adding alive bird count to output window
    text = STAT_FONT.render("Birds: " + str(no_birds), 1, (255,255,255))
    win.blit(text, (10, 50))

    base.draw(win)

    for bird in birds:
        bird.draw(win)
    pygame.display.update()

# The fitness function/main loop function
# When creating a fitness function for use w/ NEAT it must be passed two arguments:
# 'genomes' and 'config'
def main(genomes, config):
    global GEN
    GEN += 1

    # list used to keep track of the neural network, what bird the network is controlling and the
    # fitness of each bird. Three lists used so the index of given network/bird is the same
    # across all lists
    nets = []
    ge = []
    birds = []

    no_birds = 20

    # genomes is passed as a tuple thus _, g used to enumerate through list:
    # (genome_id, genome_object) - we're only concerned w/ genome_object
    for _, g in genomes:
        # setting up network for genome (genome, config_file)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        # setting initial fitness of birds
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HIEGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # function to asses what pipe to consider, will always consider second pipe after
        # passing through the first pipe
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        # if no birds left rest generation
        else:
            run = False
            break

        # function to move birds
        for x, bird in enumerate(birds):
            bird.move()
            # increase fitness value of bird - a little fitness just for being there and
            # living - every second bird stays alive +0.1 to its fitness score
            ge[x].fitness += 0.1

            # activating network - passing bird position, distance of bird from top pipe
            # and bottom pipe
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))

            # output is a list of output neuron values, as only one output neron considered
            # thus only using first element in list.
            if output[0] > 0.5:
                bird.jump()

        rem  = []
        add_pipe = False
        # checking if every pipe collides with every bird
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    # if bird collides with pipe then reduce fairness score and remove it from
                    # tracking lists
                    ge[x].fitness -= 1
                    no_birds -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # generates a new pipe as soon as bird passed through
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        # checks if any bird from all birds hits the ground
        for x, bird in enumerate(birds):
            # also checks if birds are flying off screen
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                # if bird collides with the ground then remove it from tracking lists
                # print("hit the ground")
                no_birds -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN, no_birds)


# important step
# loading in config file to NEAT algo
def run(config_path):
    # how we pass the config file to NEAT
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    # creating population
    p = neat.Population(config)
    # adding stats/metrics output to console window - optional parameters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # The best bird from all our generations
    # i.e (neat.Population(config)).[config_function](Fitness function, number of generations)
    # will call main function x50 and pass it all the genomes and config files, thus generating
    # game for all genomes provided
    # is the genome of the best bird
    winner = p.run(main, 50)

# dunder function used for best use of NEAT algo;
# to let NEAT find config file
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)