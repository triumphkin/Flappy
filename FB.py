import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
SKY_BLUE = (135, 206, 235)
DARKER_GREEN = (25, 160, 60)

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

class Bird:
    def __init__(self):
        self.x = WINDOW_WIDTH // 3
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.size = 30
        self.angle = 0
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.angle = 30  # Tilt up when flapping
    
    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update angle based on velocity
        if self.velocity < 0:
            self.angle = min(30, self.angle + 2)
        else:
            self.angle = max(-70, self.angle - 2)
    
    def draw(self):
        # Draw the bird body (red circle)
        pygame.draw.circle(screen, RED, (self.x, int(self.y)), self.size // 2)
        
        # Draw the beak (triangle)
        beak_points = []
        angle_rad = math.radians(self.angle)
        beak_length = self.size // 2
        
        # Calculate beak points based on rotation
        beak_center_x = self.x + math.cos(angle_rad) * (self.size // 3)
        beak_center_y = self.y + math.sin(angle_rad) * (self.size // 3)
        
        # Create triangle points for beak
        beak_points = [
            (beak_center_x + math.cos(angle_rad) * beak_length,
             beak_center_y + math.sin(angle_rad) * beak_length),
            (beak_center_x + math.cos(angle_rad + 2.6) * (beak_length // 2),
             beak_center_y + math.sin(angle_rad + 2.6) * (beak_length // 2)),
            (beak_center_x + math.cos(angle_rad - 2.6) * (beak_length // 2),
             beak_center_y + math.sin(angle_rad - 2.6) * (beak_length // 2))
        ]
        
        pygame.draw.polygon(screen, (255, 165, 0), beak_points)  # Orange beak
        
        # Draw the eye
        eye_x = self.x + math.cos(angle_rad - 0.5) * (self.size // 3)
        eye_y = self.y + math.sin(angle_rad - 0.5) * (self.size // 3)
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 5)
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 3)

class Pipe:
    def __init__(self):
        self.x = WINDOW_WIDTH
        self.gap_y = random.randint(PIPE_GAP, WINDOW_HEIGHT - PIPE_GAP)
        self.width = 80
        
    def move(self):
        self.x -= PIPE_SPEED
    
    def draw(self):
        # Top pipe
        self.draw_pipe_section(0, self.gap_y - PIPE_GAP // 2, True)
        # Bottom pipe
        self.draw_pipe_section(self.gap_y + PIPE_GAP // 2, WINDOW_HEIGHT, False)
    
    def draw_pipe_section(self, start_y, end_y, is_top):
        pipe_body_color = GREEN
        pipe_edge_color = DARKER_GREEN
        
        # Main pipe body
        pipe_rect = pygame.Rect(self.x, start_y, self.width, end_y - start_y)
        pygame.draw.rect(screen, pipe_body_color, pipe_rect)
        
        # Pipe edge (lip)
        lip_height = 30
        lip_extend = 10
        
        if is_top:
            lip_rect = pygame.Rect(self.x - lip_extend, end_y - lip_height, 
                                 self.width + lip_extend * 2, lip_height)
        else:
            lip_rect = pygame.Rect(self.x - lip_extend, start_y, 
                                 self.width + lip_extend * 2, lip_height)
            
        pygame.draw.rect(screen, pipe_edge_color, lip_rect)
        
        # Add highlights and shadows
        highlight_width = 10
        pygame.draw.rect(screen, DARKER_GREEN, 
                        (self.x + self.width - highlight_width, start_y, 
                         highlight_width, end_y - start_y))

def check_collision(bird, pipe):
    bird_rect = pygame.Rect(bird.x - bird.size // 2, bird.y - bird.size // 2, 
                           bird.size, bird.size)
    
    # Top pipe
    top_pipe = pygame.Rect(pipe.x, 0, pipe.width, pipe.gap_y - PIPE_GAP // 2)
    # Bottom pipe
    bottom_pipe = pygame.Rect(pipe.x, pipe.gap_y + PIPE_GAP // 2, pipe.width,
                             WINDOW_HEIGHT - (pipe.gap_y + PIPE_GAP // 2))
    
    return (bird_rect.colliderect(top_pipe) or 
            bird_rect.colliderect(bottom_pipe) or 
            bird.y < 0 or 
            bird.y > WINDOW_HEIGHT)

def main():
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    font = pygame.font.Font(None, 36)
    game_over = False
    
    # Background elements
    cloud_positions = [(random.randint(0, WINDOW_WIDTH), 
                       random.randint(50, WINDOW_HEIGHT-100)) 
                      for _ in range(3)]

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Reset game
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe = current_time
                        game_over = False
                    else:
                        bird.flap()

        if not game_over:
            # Update game objects
            bird.move()
            
            # Add new pipes
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = current_time
            
            # Update pipes
            for pipe in pipes:
                pipe.move()
                
                # Score when passing pipes
                if pipe.x + pipe.width < bird.x and pipe.x + pipe.width > bird.x - PIPE_SPEED:
                    score += 1

            # Remove off-screen pipes
            pipes = [pipe for pipe in pipes if pipe.x + pipe.width > 0]

            # Check collisions
            for pipe in pipes:
                if check_collision(bird, pipe):
                    game_over = True

        # Draw everything
        screen.fill(SKY_BLUE)
        
        # Draw clouds
        for cloud_pos in cloud_positions:
            pygame.draw.circle(screen, WHITE, cloud_pos, 20)
            pygame.draw.circle(screen, WHITE, (cloud_pos[0] - 15, cloud_pos[1]), 15)
            pygame.draw.circle(screen, WHITE, (cloud_pos[0] + 15, cloud_pos[1]), 15)
        
        for pipe in pipes:
            pipe.draw()
            
        bird.draw()
        
        # Draw score
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render('Game Over! Press SPACE to restart', True, BLACK)
            screen.blit(game_over_text, 
                       (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 
                        WINDOW_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()