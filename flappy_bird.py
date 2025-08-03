import pygame
import neat
import time
import os
import random
pygame.font.init()
pygame.mixer.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bg.png")))

SCORE_FONT = pygame.font.Font(os.path.join("assets", "flappy_bird_font.TTF"), size=70)
GEN_FONT = pygame.font.SysFont("Arial", 50, bold = True)
BIRD_COUNT_FONT = pygame.font.SysFont("Arial", 50, bold = True)

SCORE_SOUND = pygame.mixer.Sound(os.path.join("assets", "score_sound.mp3"))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        
        if displacement >= 16: # Limit the maximum downward displacement (cannot go faster than terminal velocity)
            displacement = 16
        if displacement < 0: # Make the bird go up a little faster
            displacement -= 2
            
        self.y = self.y + displacement
        
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION # Rotates bird fully upwards when going up
        else:
            if self.tilt > -90:
                    self.tilt -= self.ROT_VEL # Rotates bird downwards when falling
                    
    def draw(self, win):
        self.img_count += 1
        
        # This is to move the bird's wings up and down to create an animation effect
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # When the bird is falling nose down, stop flapping wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2 # Set img_count to 10 so that when the bird jumps back up, it won't flap its wings immediately
        
        # Rotates the bird image based on the center, taken from stackoverflow
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)    
        win.blit(rotated_image, new_rect.topleft) # Follows screen.blit(background, (x, y)) where (x, y) is the top-left corner of the image
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

class Pipe:
    GAP = 200
    VEL = 5 # Speed of the pipe moving left (bird doesn't move, pipes do)

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # Flip the pipe image upside down
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False # To check if the bird has passed the pipe
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(50, 450) # Random height for the top pipe
        self.top = self.height - self.PIPE_TOP.get_height() # Top pipe's y-coordinate
        self.bottom = self.height + self.GAP # Bottom pipe's y-coordinate
        
    def move(self):
        self.x -= self.VEL
        
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
    def collide(self, bird): # Method to check collision with the bird using masks for pixel perfect collision detection
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y)) # how far away the top left corners of the bird image and top pipe are from each other
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # how far away the top left corners of the bird image and bottom pipe are from each other
        
        # Check for overlap between the bird's mask and the pipes' masks. If yes, return (x,y), if no, return None
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)
        
        if top_point or bottom_point: # If there is a point of overlap, it means the bird has collided with the pipe
            return True
        return False
    

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH # Second base image to create a continuous effect
        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0: # If the first base image has moved off the screen, reset its position
            self.x1 = self.WIDTH + self.x2
        
        if self.x2 + self.WIDTH < 0: # If the second base image has moved off the screen, reset its position. The two images essentially create a loop, when they go off the screen they reset to the right side of the screen
            self.x2 = self.WIDTH + self.x1

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

    
    
generation = 0  # GLobal variable to keep track of the generation number

def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = SCORE_FONT.render(str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - text.get_width() - 220, 70)) # Display score at the top right corner

    # Display generation at top left
    gen_text = GEN_FONT.render(f"Gen: {generation}", 1, (255, 255, 255))
    win.blit(gen_text, (10, 30))

    # Display bird count under generation
    bird_count_text = BIRD_COUNT_FONT.render(f"Birds: {len(birds)}", 1, (255, 255, 255))
    win.blit(bird_count_text, (10, 90))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    global generation
    generation += 1
    nets = []
    ge = []
    birds = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config) # Create a neural network for each genome
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0 # Initialize fitness for each genome
        ge.append(g) # Store the genome for each bird
        
        
    
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    run = True
    
    

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break # If there are no birds left, exit the loop
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1 # Increase fitness for each frame the bird stays alive
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))) #
        
            if output[0] > 0.5:
                bird.jump()
        
        add_pipe = False
        removed_pipes = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1 # If the bird collides with the pipe, reduce its fitness
                    birds.pop(x)
                    nets.pop(x) # Remove the neural network for the bird that collided
                    ge.pop(x)
                
                if not pipe.passed and pipe.x < bird.x: # If the bird has passed the pipe, set passed to True
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # If the pipe has moved off the screen, remove it
                removed_pipes.append(pipe)
            
            pipe.move()
            
        if add_pipe:
            score += 1
            SCORE_SOUND.play() # Play sound when score increases
            for g in ge:
                g.fitness += 5 # Increase fitness for each bird that passes a pipe
            pipes.append(Pipe(600))
                
        for r in removed_pipes:
            pipes.remove(r)
            
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: #   If the bird goes off the screen, remove it
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
            
        base.move()
        draw_window(win, birds, pipes, base, score)

def run(config_path):
    global generation
    generation = 0

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    
    population.add_reporter(neat.StdOutReporter(True)) # Prints the progress of the NEAT algorithm
    
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    winner = population.run(main, 50) # Run the NEAT algorithm for 50 generations
    
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-neat.txt")
    run(config_path)