import pygame
import sys
import random
import neat
import os


cliff_images = {
        'top': 'imgs/Cliff1.png',
        'middle': 'imgs/Cliff3.png'
    }
class Character:
    def __init__(self, image_paths, position):
        self.images = {state: pygame.image.load(path).convert_alpha() for state, path in image_paths.items()}
        self.original_position = position
        self.position = position
        self.state = 'standing'
        self.velocity = 20  # Increased jump velocity for more noticeable effect
        self.angle = 0  # Initial angle of rotation
        self.total_flips = 0



    def draw(self, screen, collide):
        if not collide:
            rotated_image = pygame.transform.rotate(self.images[self.state], -self.angle)
            # Correct the position offset caused by rotation
            new_rect = rotated_image.get_rect(center=self.images[self.state].get_rect(topleft=self.position).center)
            screen.blit(rotated_image, new_rect.topleft)


    def jump(self):
        if self.state == 'standing':  # Ensure jump only from standing
            self.state = 'straight'  # Change the state to 'jumping'
            self.velocity_x = 2  # Horizontal velocity to move forward
            self.velocity_y = -10  # Initial upward velocity for the jump

    def tuck(self):
        if self.state == 'straight':  # Ensure tuck only if in straight
            self.state = 'tuck'

    def release_tuck(self):
        if self.state == 'tuck':  # Ensure we go back to straight only if we were tucking
            self.state = 'straight'

    def update(self, jump):
        if jump and self.position[1] < 41:
            # Apply horizontal and vertical velocities to position
            self.position = (self.position[0] + self.velocity_x, self.position[1] + self.velocity_y)
            # Apply gravity to vertical velocity
            self.velocity_y += 0.5
            if self.position[0] < 50:
                self.velocity_x += 0.5 # Gravity effect, incrementally reducing upward velocity
      

        

    def finalize_flip_count(self):
        # Calculate total half flips based purely on rotation
        self.total_flips = round(abs(self.angle) / 180)
        if self.total_flips % 2 == 0:
            self.total_flips /= 2
        else:
            self.total_flips -= 1
            self.total_flips /= 2
            self.total_flips += 0.5




    def update2(self):
        # Automatically apply gravity if not standing
        if self.state != 'standing':
            self.position = (self.position[0], self.position[1] + 20)
        # Reset to standing position if diver goes below original position


    def rotate(self):
        if self.state == 'straight':
            self.angle += 0.6  # Slow rotation in straight position
        elif self.state == 'tuck':
            self.angle += 30  # Fast rotation in tuck position
        # Ensure the angle wraps around 360 degrees
        # self.angle %= 360

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.images[self.state])





class Cliff:
    """
    Represents the scrolling cliffs of the game, moving vertically upward.
    """
    VEL = 0.7  # Speed at which the cliff scrolls upwards

    def __init__(self, image_paths, x, screen_height):
        """
        Initialize the cliff sections.
        :param image_paths: dictionary of paths to cliff images (top, middle)
        :param x: int, horizontal position to start drawing cliffs
        :param screen_height: int, the height of the game screen
        """
        self.images = {part: pygame.image.load(path).convert_alpha() for part, path in image_paths.items()}
        self.x = x
        self.y2 = self.images['top'].get_height()
        self.screen_height = screen_height
        self.y = 70  # Start the cliffs just off the bottom of the screen
        self.current_section = 'top'
        self.middle_fixed = False  # Control if the middle section is fixed
        self.moving = False
        self.y2 = 0

    def move(self):
        """
        Move the cliff images upward by decreasing the y position.

        """

        if not self.middle_fixed and self.moving:
            self.y -= self.VEL
            

            # Check if we need to switch from the top to the middle section
            if self.current_section == 'top' and self.y + self.images['top'].get_height() < self.screen_height:
                self.current_section = 'middle'
                # Set the middle cliff to start exactly at the point where the top cliff ends
                # The y-coordinate is set to the point where the top cliff ends
                self.y = 0
                

            # Fix the middle section in place when it reaches the bottom of the screen
            if self.current_section == 'middle' and self.y < self.screen_height - self.images['middle'].get_height():
                self.middle_fixed = True
                self.y = self.screen_height - self.images['middle'].get_height()
               
               

    def draw(self, win):
        """
        Draw the cliff section to the game window.
        """
        win.blit(self.images[self.current_section], (self.x, self.y))

    def start_moving(self):
        """
        Start the cliff moving upward.
        """
        self.moving = True
    
class Base(Cliff):
    Vel = 0.8
    def __init__(self, imgs):
        self.imgs = imgs
        self.height = self.imgs[0].get_height()
        self.y = 1550 - self.height


    def move(self, fixed, curr_section):

        if fixed or curr_section == 'standing':
            return
        else:
            self.y -= self.Vel

    def draw(self, win):
        win.blit(self.imgs[0], (0, self.y))



    def collide(self, diver):
        """Check for collision between the base and the diver using masks."""
        # Get the mask from the diver's image
        diver_mask = diver.get_mask()

        # Create a mask for the base image
        base_mask = pygame.mask.from_surface(self.imgs[0])

        # Calculate offset between the diver and the base
        offset = (100 - diver.position[0], self.y - diver.position[1] + 130)  # Assumes diver has x and y attributes

        # Check for collision at the offset
        point_of_collision = diver_mask.overlap(base_mask, offset)
        
        # Return True if collision detected, False otherwise
        return point_of_collision is not None
    
    def animate_splash(self, angle, win, bg_color, cliff):
        angle %= 360
    # Assuming angle divisions are meant to control the intensity of the splash
        if 0 <= angle < 5 or 355 < angle <= 360 or 175 < angle < 185:
            num_frames = 2  # Minimal splash
        elif 5 <= angle < 55 or 305 < angle <= 355 or 140 < angle < 175 or 185 <= angle < 220:
            num_frames = 3  # Small splash
        elif 55 <= angle < 80 or 285 < angle <= 305 or 100 < angle < 140 or 220 <= angle < 260:
            num_frames = 4  # Medium splash
        else:
            num_frames = 5  # Large splash # Most frames for the most dramatic splash

        for i in range(num_frames):
            if i < len(self.imgs):  # Check to avoid index out of range
                win.blit(self.imgs[i], (0, self.y))
                pygame.display.update()
                pygame.time.wait(100)  # Wait 100 ms between frames
                if i == num_frames - 1:
                    for j in range(num_frames - 1, -1, -1):
                        if i < len(self.imgs):  # Check to avoid index out of range
                            win.fill(bg_color)
                            cliff.draw(win)
                            win.blit(self.imgs[j], (0, self.y))
                            pygame.display.update()
                            pygame.time.wait(100)
        





def handle(divers, ge, cliff, base, screen, bg_color, collide, total_angle, landed, runn):
    for x, diver in enumerate(divers):
            if collide and not landed:
                runn = False
                angle_difference = abs(diver.angle - total_angle)
                # base.animate_splash(diver.angle, screen, bg_color, cliff)
                landed = True
                diver.finalize_flip_count()
                print(f"diver angleeeeeeeeeeeeee {diver.angle}")
                print(diver.state)
                if diver.state == 'Straight':
                    ge[x].fitness += 0.1
                else:
                    ge[x].fitness -= 0.1
                if angle_difference > 0 and angle_difference <= 90:
                    ge[x].fitness += 1000 / angle_difference  # High reward for nearly perfect alignment
                elif angle_difference > 90:
                    ge[x].fitness += 100 / angle_difference  # High reward for nearly perfect alignment
                else:
                    ge[x].fitness += 200
               
    return runn

            




        


def fitness(genomes, config):
    nets = []
    ge = []
    divers = []
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    bg_color = (135, 206, 235)  # Sky blue background
    pygame.display.set_caption("Stickman Cliff Diving")
    image_paths = {
        'standing': 'imgs/Standing.png',
        'straight': 'imgs/Entry2.png',
        'tuck': 'imgs/Tuck.png'
    }

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        divers.append(Character(image_paths, (90, 40)))
        g.fitness = 0.001 if g.fitness is None else g.fitness
        ge.append(g)



    flip_requirement = random.choice([x * 0.5 for x in range(1, 10)])  # Generates numbers from 0.5 to 7.0 in steps of 0.5
    total_angle = flip_requirement * 360


    Base_images = []
    
    Base_images1 = [
    pygame.image.load(f'imgs/Base{i}.png').convert_alpha() for i in range(0, 5)
    ]
   
    for Base_image in Base_images1:
        width = Base_image.get_width()
        height = Base_image.get_height()

        # Increase the height
        new_height = height + 100
        new_width = width + 450
        Base_image = pygame.transform.scale(Base_image, (new_width, new_height))
        Base_images.append(Base_image)
        


    
    # Paths for images for different states
    
    
    cliff = Cliff(cliff_images, 0, screen.get_height())


    base = Base(Base_images)
    

    running = True
    runn = True
    space_pressed = False
    initial_press = True  # Flag to check if it's the first press of the space key
    jump = False




    font = pygame.font.Font(None, 36)

    landed = False

    while running:
        for event in pygame.event.get():
     
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for x, diver in enumerate(divers):
            diver.jump()
            
            jump = True
    
            




            inputs = [total_angle, diver.angle, (diver.position[1] - base.y)]
            output = nets[x].activate(inputs)
            decision = output.index(max(output))
            if decision == 0:
                diver.tuck()
            if decision == 1:
                diver.release_tuck()
            
 
   
            diver.update(jump)  # Update character state and position
            diver.rotate()
            collide = base.collide(diver)
            cliff.start_moving()


            cliff.move()
            if cliff.middle_fixed:
                diver.update2()
            base.move(cliff.middle_fixed, diver.state)
            runn = handle(divers, ge, cliff, base, screen, bg_color, collide, total_angle, landed, runn)

            

      
        screen.fill(bg_color)
        for diver in divers:
            diver.draw(screen, collide)


       



        cliff.draw(screen)
        base.draw(screen)
        
        text_surface = font.render(f"Flips: {flip_requirement}", True, (255, 255, 255))
        screen.blit(text_surface, (400, 10))
        
        
        pygame.display.update()
        clock.tick(30)
        if not runn:
            break
        
    for x, diver in enumerate(divers):
        print(f"angle wanted is {total_angle}\n\n")
        print(f"TOTALLL ISSSS {diver.angle}\n\n")
        print(f"fitness is: {ge[x].fitness}")
       
    





            
        









def run(config_path):
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-27')

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(1))

    winner = p.run(fitness,100)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_feedforward.txt")
    run(config_path)