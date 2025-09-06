from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time


# Game state
class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3


# Power-up types
class PowerUpType:
    MAGNET = 0
    SHIELD = 1
    SPEED_BOOST = 2
    DOUBLE_JUMP = 3
    COIN_MULTIPLIER = 4
    FLYING = 5  # Add this new power-up


# Add near other global variables
last_time = time.time()
delta_time = 0



# Player class
class Player:


    def __init__(self):
        self.x = 0 # Lane position (-1, 0, 1 for left, center, right)
        self.y = 0 # Forward position
        self.z = 20 # Height (for jumping)
        self.target_x = 0 # Target lane for smooth movement
        self.lane = 0 # Current lane (-1, 0, 1)
        self.jumping = False
        self.sliding = False
        self.jump_velocity = 0
        self.slide_timer = 0
        self.turning = False
        self.turn_direction = 0 # -1 for left, 1 for right

        # Power-up states
        self.magnet_timer = 0
        self.shield_timer = 0
        self.speed_boost_timer = 0
        self.double_jump_timer = 0
        self.coin_multiplier_timer = 0
        self.flying_timer = 0  # Add flying timer
        self.can_double_jump = False
        self.has_double_jumped = False
        
        # Flying animation variables
        self.flying_height_offset = 0
        self.flying_animation_timer = 0



    def update(self):
            


            # Smooth lane movement
            if abs(self.x - self.target_x) > 1:
                if self.x < self.target_x:
                    self.x += 2
                else:
                    self.x -= 2
            else:
                self.x = self.target_x



            # Flying mode with smooth transition
            if self.flying_timer > 0:
                self.flying_timer -= 1
                self.flying_animation_timer += 1
                
                # Target flying height
                target_height = 200
                self.flying_height_offset = math.sin(self.flying_animation_timer * 0.1) * 25
                target_z = target_height + self.flying_height_offset
                
                # Smooth transition to flying height
                if self.z < target_z:
                    self.z = min(self.z + 5, target_z)  # Ascend smoothly
                else:
                    self.z = target_z
                    
                # Disable jumping and sliding while flying
                self.jumping = False
                self.sliding = False
                self.jump_velocity = 0
                


            else:
                # Normal ground-based movement
                self.flying_height_offset = 0
                self.flying_animation_timer = 0
                
                # Smooth descent when flying ends
                if self.z > 20 and not self.jumping:
                    self.z = max(20, self.z - 8)  # Descend smoothly at 8 units per frame
                
                # Jumping physics (only when not flying)
                if self.jumping:
                    self.z += self.jump_velocity
                    self.jump_velocity -= 0.5
                    if self.z <= 20:
                        self.z = 20
                        self.jumping = False
                        self.jump_velocity = 0
                        self.has_double_jumped = False # Reset double jump

                # Sliding (only when not flying)
                if self.sliding:
                    self.slide_timer -= 1
                    if self.slide_timer <= 0:
                        self.sliding = False



            # Update other power-up timers
            if self.magnet_timer > 0:
                self.magnet_timer -= 1
            if self.shield_timer > 0:
                self.shield_timer -= 1
            if self.speed_boost_timer > 0:
                self.speed_boost_timer -= 1
            if self.double_jump_timer > 0:
                self.double_jump_timer -= 1
                self.can_double_jump = True
            else:
                self.can_double_jump = False
            if self.coin_multiplier_timer > 0:
                self.coin_multiplier_timer -= 1



    def jump(self):
        # Can't jump while flying
        if self.flying_timer > 0:
            return


        if not self.jumping and not self.sliding:
            self.jumping = True
            self.jump_velocity = 25
        elif self.jumping and self.can_double_jump and not self.has_double_jumped:
            # Double jump
            self.jump_velocity = 50
            self.has_double_jumped = True


    def slide(self):
        # Can't slide while flying
        if self.flying_timer > 0:
            return
            
        if not self.jumping and not self.sliding:
            self.sliding = True
            self.slide_timer = 180



    def move_left(self):
        if not self.turning and self.lane > -1:
            self.lane -= 1
            self.target_x = self.lane * 100



    def move_right(self):
        if not self.turning and self.lane < 1:
            self.lane += 1
            self.target_x = self.lane * 100


    def activate_power_up(self, power_up_type):
        if power_up_type == PowerUpType.MAGNET:
            self.magnet_timer = 600 # 10 seconds at 60 FPS
        elif power_up_type == PowerUpType.SHIELD:
            self.shield_timer = 600 # 10 seconds
        elif power_up_type == PowerUpType.SPEED_BOOST:
            self.speed_boost_timer = 480 # 8 seconds
        elif power_up_type == PowerUpType.DOUBLE_JUMP:
            self.double_jump_timer = 900 # 15 seconds
        elif power_up_type == PowerUpType.COIN_MULTIPLIER:
            self.coin_multiplier_timer = 600 # 10 seconds
        elif power_up_type == PowerUpType.FLYING:
            self.flying_timer = 1200  # 20 seconds
            # Cancel other movement states when starting to fly
            self.jumping = False
            self.sliding = False
            self.jump_velocity = 0






class ChasingEnemy:
    def __init__(self):
        self.x = 0  # Lane position
        self.y = -300  # Start far behind player
        self.z = 20  # Ground level
        self.speed = 1.5  # Base chase speed
        self.target_x = 0  # Target lane position
        self.active = True
        self.caught_player = False
        self.pursuit_mode = False  # Activated after first life lost
        
        # Animation variables
        self.animation_timer = 0
        self.glowing_intensity = 0
        
    def update(self):
        if not self.active:
            return
            
        # Update animation
        self.animation_timer += 1
        self.glowing_intensity = (math.sin(self.animation_timer * 0.2) + 1) * 0.5
        
        # Only start moving if pursuit mode is activated
        if self.pursuit_mode:
            # Calculate distance to player
            distance_to_player = distance - self.y
            
            # Adjust speed based on distance
            if distance_to_player > 100:
                self.speed = 2.5  # Speed up if far behind
            elif distance_to_player < 30:
                self.speed = 1.0  # Slow down when close
            else:
                self.speed = 2.0  # Normal pursuit speed
            
            # Move forward
            self.y += self.speed * delta_time * 60
            
            # Follow player's lane with some delay
            if random.randint(1, 30) == 1:  # Update target occasionally
                self.target_x = player.lane * 100
                
            # Smooth lane movement
            if abs(self.x - self.target_x) > 2:
                if self.x < self.target_x:
                    self.x += 3
                else:
                    self.x -= 3
            else:
                self.x = self.target_x
    
    def activate_pursuit(self):
        """Start chasing after first life lost"""
        self.pursuit_mode = True
        self.y = max(self.y, distance - 150)  # Move closer
        
    def rush_attack(self):
        """Rush forward for immediate catch after second life lost"""
        self.y = distance - 30  # Move very close
        self.speed = 5.0  # Fast approach
        
    def check_collision(self):
        if not self.active or not self.pursuit_mode:
            return False
            
        # Check if enemy caught the player
        if (abs(self.x - player.x) < 40 and 
            abs(self.y - distance) < 40):
            self.caught_player = True
            return True
        return False
        
    def reset(self):
        self.x = 0
        self.y = -300
        self.speed = 1.5
        self.active = True
        self.caught_player = False
        self.pursuit_mode = False
        self.animation_timer = 0







# Obstacle class
class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x  # Lane position
        self.y = y  # Forward position
        self.type = obstacle_type  # 'low', 'high', 'gap'
        self.active = True



# Coin class
class Coin:
    def __init__(self, x, y, z=30):
        self.x = x
        self.y = y
        self.z = z
        self.rotation = 0
        self.collected = False



# Power-up class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.z = 30
        self.type = power_type
        self.rotation = 0
        self.collected = False
        self.float_offset = 0


# Game variables
player = Player()
obstacles = []
coins = []
power_ups = []
game_state = GameState.MENU
score = 0
speed = 1.5
distance = 0
coins_collected = 0
game_over_reason = ""
player_lives = 5
last_speed_increase_score = 0  # Track when we last increased speed

# Add these global variables near your other game variables
chasing_enemy = None
last_life_lost_time = None
life_lost_count = 0
enemy_pursuit_active = False

# Initialize the enemy
chasing_enemy = ChasingEnemy()




# Camera variables
camera_distance = 150
camera_height = 80
camera_angle = 0



# Track generation
track_length = 0
next_obstacle_distance = 100
next_powerup_distance = 800



# Power-up names for display
power_up_names = {
    PowerUpType.MAGNET: "MAGNET",
    PowerUpType.SHIELD: "SHIELD",
    PowerUpType.SPEED_BOOST: "SPEED BOOST",
    PowerUpType.DOUBLE_JUMP: "DOUBLE JUMP",
    PowerUpType.COIN_MULTIPLIER: "COIN MULTIPLIER",
    PowerUpType.FLYING: "FLYING MODE"
}





def reset_game():
    global player, obstacles, coins, power_ups, score, speed, distance, coins_collected, game_state
    global track_length, next_obstacle_distance, next_powerup_distance, player_lives, last_speed_increase_score
    global chasing_enemy, last_life_lost_time, life_lost_count
    
    player = Player()
    obstacles = []
    coins = []
    power_ups = []
    score = 0
    speed = 3
    distance = 0
    coins_collected = 0
    game_state = GameState.PLAYING
    track_length = 0
    next_obstacle_distance = 100
    next_powerup_distance = 800
    player_lives = 5
    last_speed_increase_score = 0
    
    # Reset enemy tracking
    chasing_enemy.reset()
    last_life_lost_time = None
    life_lost_count = 0




def generate_track():
    global track_length, next_obstacle_distance, next_powerup_distance

    # Generate obstacles
    if distance > next_obstacle_distance:
        lane = random.randint(-1, 1)
        obstacle_type = random.choice(['low', 'high', 'gap'])
        obstacles.append(Obstacle(lane * 100, distance + 1200, obstacle_type))
        next_obstacle_distance = distance + random.randint(400, 700)

        # Generate coins around obstacles
        for i in range(3):
            coin_lane = random.randint(-1, 1)
            if coin_lane * 100 != lane * 100:
                coins.append(Coin(coin_lane * 100, distance + 800 + i * 150))

    # Generate power-ups (less frequent than obstacles)
    if distance > next_powerup_distance:
        lane = random.randint(-1, 1)
        power_type = random.randint(0, 5)  # Change from 4 to 5 to include flying
        power_ups.append(PowerUp(lane * 100, distance + 1000, power_type))
        next_powerup_distance = distance + random.randint(800, 1500)






def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def draw_player():
    glPushMatrix()
    glTranslatef(player.x, distance + player.y, player.z)

    # Flying trail effect
    if player.flying_timer > 0:
        glColor4f(0.5, 0.8, 1.0, 0.3)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw multiple spheres for trail effect
        for i in range(3):
            glPushMatrix()
            glTranslatef(0, -i * 20, -i * 5)
            glutSolidSphere(30 - i * 5, 12, 12)
            glPopMatrix()
            
        glDisable(GL_BLEND)
    
    # Shield effect
    if player.shield_timer > 0:
        glColor4f(0.5, 0.5, 1.0, 0.3)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glutSolidSphere(35, 16, 16)
        glDisable(GL_BLEND)
    
    # Animation variables
    walk_cycle = (distance * 0.1) % (2 * math.pi)
    arm_swing = math.sin(walk_cycle) * 15
    leg_swing = math.sin(walk_cycle) * 10

    # Flying pose adjustments
    if player.flying_timer > 0:
        glRotatef(-15, 1, 0, 0)  # Slight forward tilt when flying
        arm_swing = math.sin(walk_cycle * 0.5) * 30  # Slower, wider arm movement
        leg_swing = 0  # No leg movement while flying
    elif player.sliding:
        glTranslatef(0, 0, -30)
        glRotatef(60, 1, 0, 0)
    
   
    
    # Player body - change color based on power-ups
    if player.speed_boost_timer > 0:
        glColor3f(1.0, 0.5, 0.0)  # Orange when speed boosted
    elif player.magnet_timer > 0:
        glColor3f(1.0, 0.0, 1.0)  # Magenta when magnet active
    else:
        glColor3f(0.1, 0.5, 1.0)  # Normal blue
    
    glutSolidCube(25)
    
    # Player head
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glColor3f(1.0, 0.8, 0.6)
    glutSolidCube(12)
    
    # Eyes
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(-3, -5, 1)
    glutSolidCube(1.5)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(3, -5, 1)
    glutSolidCube(1.5)
    glPopMatrix()
    glPopMatrix()
    
    # Arms with animation
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(15 * side, 0, 3)
        if not player.sliding:
            glRotatef(arm_swing * side, 1, 0, 0)
        glColor3f(1.0, 0.8, 0.6)
        
        # Upper arm
        glPushMatrix()
        glTranslatef(0, 0, -6)
        glScalef(0.4, 0.4, 1.0)
        glutSolidCube(12)
        glPopMatrix()
        
        # Lower arm
        glTranslatef(0, 0, -15)
        glRotatef(-30, 1, 0, 0)
        glPushMatrix()
        glTranslatef(0, 0, -6)
        glScalef(0.3, 0.3, 0.8)
        glutSolidCube(12)
        glPopMatrix()
        
        # Hand
        glTranslatef(0, 0, -12)
        glColor3f(1.0, 0.7, 0.5)
        glutSolidCube(4)
        glPopMatrix()
    

    # Legs with animation
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(6 * side, 0, -15)
        if not player.sliding and not player.jumping:
            glRotatef(leg_swing * side, 1, 0, 0)
        glColor3f(0.2, 0.2, 0.8)
        
        # Upper leg
        glPushMatrix()
        glTranslatef(0, 0, -8)
        glScalef(0.5, 0.5, 1.2)
        glutSolidCube(12)
        glPopMatrix()
        
        # Lower leg
        glTranslatef(0, 0, -20)
        if not player.sliding:
            glRotatef(20, 1, 0, 0)
        glPushMatrix()
        glTranslatef(0, 0, -8)
        glScalef(0.4, 0.4, 1.0)
        glutSolidCube(12)
        glPopMatrix()
        
        # Foot
        glTranslatef(0, 0, -16)
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, -4, 0)
        glScalef(0.6, 1.2, 0.3)
        glutSolidCube(10)
        glPopMatrix()
        glPopMatrix()
    
    glPopMatrix()




def draw_track():
    # Draw the main track
    glColor3f(0.6, 0.4, 0.2)
    for i in range(int(distance - 500), int(distance + 1000), 100):
        glBegin(GL_QUADS)
        glVertex3f(-150, i, 0)
        glVertex3f(150, i, 0)
        glVertex3f(150, i + 100, 0)
        glVertex3f(-150, i + 100, 0)
        glEnd()
    
    # Draw lane dividers
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(3)
    for i in range(int(distance - 500), int(distance + 1000), 20):
        glBegin(GL_LINES)
        glVertex3f(-50, i, 1)
        glVertex3f(-50, i + 10, 1)
        glVertex3f(50, i, 1)
        glVertex3f(50, i + 10, 1)
        glEnd()




def draw_obstacles():
    for obstacle in obstacles:
        if obstacle.active and abs(obstacle.y - distance) < 600:
            glPushMatrix()
            glTranslatef(obstacle.x, obstacle.y, 0)
            
            if obstacle.type == 'low':
                glColor3f(0.5, 0.3, 0.1)
                glPushMatrix()
                glTranslatef(0, 0, 70)
                glScalef(2, 0.4, 1.2)
                glutSolidCube(60)
                glPopMatrix()
                
                glPushMatrix()
                glTranslatef(-60, 0, 50)
                glScalef(0.4, 0.4, 2.5)
                glutSolidCube(60)
                glPopMatrix()
                
                glPushMatrix()
                glTranslatef(60, 0, 50)
                glScalef(0.4, 0.4, 2.5)
                glutSolidCube(60)
                glPopMatrix()
                
                glColor3f(0.1, 0.1, 0.1)
                glBegin(GL_QUADS)
                glVertex3f(-50, -20, 0)
                glVertex3f(50, -20, 0)
                glVertex3f(50, 20, 0)
                glVertex3f(-50, 20, 0)
                glEnd()
                
            
            elif obstacle.type == 'high':
                glColor3f(0.7, 0.2, 0.1)
                glTranslatef(0, 0, 50)  # Lowered from 60 to 50
                glScalef(1.5, 0.4, 1.8)  # Reduced scale values
                glutSolidCube(50)  # Smaller cube size
                
            elif obstacle.type == 'gap':
                glColor3f(0.0, 0.0, 0.0)
                glBegin(GL_QUADS)
                glVertex3f(-80, -50, -20)
                glVertex3f(80, -50, -20)
                glVertex3f(80, 50, -20)
                glVertex3f(-80, 50, -20)
                glEnd()
                
                glColor3f(0.2, 0.1, 0.0)
                glBegin(GL_QUADS)
                glVertex3f(-80, -50, -20)
                glVertex3f(80, -50, -20)
                glVertex3f(80, -50, 0)
                glVertex3f(-80, -50, 0)
                
                glVertex3f(-80, 50, -20)
                glVertex3f(80, 50, -20)
                glVertex3f(80, 50, 0)
                glVertex3f(-80, 50, 0)
                
                glVertex3f(-80, -50, -20)
                glVertex3f(-80, 50, -20)
                glVertex3f(-80, 50, 0)
                glVertex3f(-80, -50, 0)
                
                glVertex3f(80, -50, -20)
                glVertex3f(80, 50, -20)
                glVertex3f(80, 50, 0)
                glVertex3f(80, -50, 0)
                glEnd()
                
                glColor3f(1.0, 0.0, 0.0)
                for i in range(-60, 80, 20):
                    glPushMatrix()
                    glTranslatef(i, -55, 5)
                    glRotatef(45, 0, 0, 1)
                    glutSolidCube(8)
                    glPopMatrix()
                    
                    glPushMatrix()
                    glTranslatef(i, 55, 5)
                    glRotatef(45, 0, 0, 1)
                    glutSolidCube(8)
                    glPopMatrix()
            
            glPopMatrix()





def draw_chasing_enemy():
    if not chasing_enemy.active or not chasing_enemy.pursuit_mode or abs(chasing_enemy.y - distance) > 600:
        return
        
    glPushMatrix()
    glTranslatef(chasing_enemy.x, chasing_enemy.y, chasing_enemy.z)
    
    # Pulsing glow effect
    glow = 0.3 + chasing_enemy.glowing_intensity * 0.4
    glColor4f(1.0, 0.2 * glow, 0.0, 0.8)
    
    # Enable blending for glow effect
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw outer glow
    glutSolidSphere(45, 12, 12)
    
    # Main body (darker red)
    glColor3f(0.8, 0.1, 0.1)
    glutSolidCube(35)
    
    # Eyes (glowing yellow)
    glColor3f(1.0, 1.0, 0.2)
    glPushMatrix()
    glTranslatef(-8, -15, 8)
    glutSolidSphere(3, 6, 6)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(8, -15, 8)
    glutSolidSphere(3, 6, 6)
    glPopMatrix()
    
    glDisable(GL_BLEND)
    glPopMatrix()






def draw_coins():
    for coin in coins:
        if not coin.collected and abs(coin.y - distance) < 600:
            # Magnet effect - attract coins to player
            if player.magnet_timer > 0:
                dx = player.x - coin.x
                dy = (distance + player.y) - coin.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 200:  # Magnet range
                    coin.x += dx * 0.15
                    coin.y += dy * 0.15
            
            glPushMatrix()
            glTranslatef(coin.x, coin.y, coin.z)
            glRotatef(coin.rotation, 0, 0, 1)
            
            # Glowing effect for coin multiplier
            if player.coin_multiplier_timer > 0:
                glColor3f(1, 1, 0.5)
            else:
                glColor3f(1, 1, 0)
            
            quadric = gluNewQuadric()
            gluCylinder(quadric, 15, 15, 5, 8, 2)
            
            glPopMatrix()
            coin.rotation = (coin.rotation + 2) % 360



def draw_power_ups():
    for power_up in power_ups:
        if not power_up.collected and abs(power_up.y - distance) < 600:
            glPushMatrix()
            
            # Floating animation
            power_up.float_offset = math.sin(time.time() * 3) * 10
            glTranslatef(power_up.x, power_up.y, power_up.z + power_up.float_offset)
            glRotatef(power_up.rotation, 0, 1, 0)

            # Different colors and shapes for different power-ups
            if power_up.type == PowerUpType.MAGNET:
                glColor3f(1.0, 0.0, 1.0)  # Magenta
                glutSolidTorus(5, 15, 8, 16)
            elif power_up.type == PowerUpType.SHIELD:
                glColor3f(0.0, 1.0, 1.0)  # Cyan
                glPushMatrix()
                glRotatef(45, 1, 1, 0)
                glutSolidCube(20)
                glPopMatrix()
            elif power_up.type == PowerUpType.SPEED_BOOST:
                glColor3f(1.0, 0.5, 0.0)  # Orange
                glScalef(0.5, 2.0, 0.5)
                glutSolidCube(20)
            elif power_up.type == PowerUpType.DOUBLE_JUMP:
                glColor3f(0.0, 1.0, 0.0)  # Green
                glutSolidCube(15)
                glTranslatef(0, 0, 20)
                glutSolidCube(10)
            elif power_up.type == PowerUpType.COIN_MULTIPLIER:
                glColor3f(1.0, 1.0, 0.0)  # Yellow
                for i in range(5):
                    glPushMatrix()
                    glRotatef(i * 72, 0, 0, 1)
                    glTranslatef(0, 15, 0)
                    glutSolidCube(8)
                    glPopMatrix()
            elif power_up.type == PowerUpType.FLYING:
                # Flying power-up - Light blue with wing-like shape
                glColor3f(0.5, 0.8, 1.0)  # Light blue
                
                # Main body
                glutSolidSphere(12, 8, 8)
                
                # Wing animation
                wing_angle = math.sin(time.time() * 8) * 30  # Fast wing flapping
                
                # Left wing
                glPushMatrix()
                glTranslatef(-15, 0, 0)
                glRotatef(wing_angle, 0, 0, 1)
                glScalef(2.0, 0.3, 0.1)
                glutSolidCube(15)
                glPopMatrix()
                
                # Right wing
                glPushMatrix()
                glTranslatef(15, 0, 0)
                glRotatef(-wing_angle, 0, 0, 1)
                glScalef(2.0, 0.3, 0.1)
                glutSolidCube(15)
                glPopMatrix()
                
            glPopMatrix()
            power_up.rotation = (power_up.rotation + 3) % 360




def draw_environment():
    # Draw temple walls on sides
    glColor3f(0.4, 0.3, 0.2)
    for i in range(int(distance - 500), int(distance + 1000), 200):
        # Left wall
        glPushMatrix()
        glTranslatef(-300, i, 50)
        glScalef(1, 4, 2)
        glutSolidCube(50)
        glPopMatrix()
        
        # Right wall
        glPushMatrix()
        glTranslatef(300, i, 50)
        glScalef(1, 4, 2)
        glutSolidCube(50)
        glPopMatrix()
    
    # Draw temple pillars
    glColor3f(0.5, 0.4, 0.3)
    for i in range(int(distance - 500), int(distance + 1000), 400):
        for side in [-200, 200]:
            glPushMatrix()
            glTranslatef(side, i, 80)
            gluCylinder(gluNewQuadric(), 20, 20, 160, 8, 8)
            glPopMatrix()



def check_collisions():
    global game_state, game_over_reason, player_lives, score, coins_collected
    global last_life_lost_time, life_lost_count, chasing_enemy
    
    current_time = time.time()
    
    # Check obstacle collisions (unless shield is active OR flying)
    if player.shield_timer <= 0 and player.flying_timer <= 0:
        for obstacle in obstacles:
            if obstacle.active:
                if (abs(obstacle.x - player.x) < 50 and
                    abs(obstacle.y - (player.y + distance)) < 50):
                    collision_happened = False
                    
                    if obstacle.type == 'low' and not player.sliding:
                        collision_happened = True
                        game_over_reason = "Hit low barrier! Should have slid!"
                    elif obstacle.type == 'low' and player.sliding and player.z > 25:
                        collision_happened = True
                        game_over_reason = "Didn't slide low enough!"
                    elif obstacle.type == 'high' and player.z < 70:
                        collision_happened = True
                        game_over_reason = "Hit high barrier! Should have jumped higher!"
                    elif obstacle.type == 'gap' and player.z < 30:
                        collision_happened = True
                        game_over_reason = "Fell in gap! Should have jumped!"
                    
                    if collision_happened:
                        player_lives -= 1
                        obstacle.active = False
                        
                        # ENEMY CHASING LOGIC
                        if last_life_lost_time is None:
                            # First life lost - activate enemy pursuit
                            life_lost_count = 1
                            last_life_lost_time = current_time
                            chasing_enemy.activate_pursuit()
                            print("Guardian awakened! It's now hunting you...")
                            
                        elif (current_time - last_life_lost_time) <= 20:
                            # Second life lost within 20 seconds
                            life_lost_count += 1
                            if life_lost_count >= 2:
                                chasing_enemy.rush_attack()
                                # Enemy catches player, causing additional life loss
                                player_lives -= 1
                                print("Guardian caught you due to repeated mistakes!")
                                game_over_reason = "Caught by Guardian for repeated failures!"
                                
                                # Reset tracking
                                life_lost_count = 0
                                last_life_lost_time = None
                        else:
                            # More than 20 seconds passed, reset counter
                            life_lost_count = 1
                            last_life_lost_time = current_time
                            chasing_enemy.activate_pursuit()
                        
                        if player_lives <= 0:
                            game_state = GameState.GAME_OVER
                        else:
                            if life_lost_count < 2:
                                game_over_reason = f"Life lost! {player_lives} lives remaining - Guardian approaches!"
                            
                        player.jumping = False
                        player.sliding = False
                        player.z = 20
                        
                    else:
                        obstacle.active = False
                        # Bonus points for successfully avoiding obstacles
                        if obstacle.type == 'low' and player.sliding:
                            score += 150
                            print("Nice slide! +150 points")
                        elif obstacle.type == 'high' and player.z > 60:
                            score += 200
                            print("Great jump! +200 points")
                        elif obstacle.type == 'gap' and player.z > 30:
                            score += 250
                            print("Perfect gap jump! +250 points")
    


    # Check if enemy caught player (separate from obstacle collisions, but not while flying)
    if chasing_enemy.check_collision() and player.shield_timer <= 0 and player.flying_timer <= 0:
        player_lives -= 1
        if player_lives <= 0:
            game_state = GameState.GAME_OVER
            game_over_reason = "Caught by the Ancient Guardian!"
        else:
            game_over_reason = f"Guardian touched you! {player_lives} lives remaining"
            chasing_enemy.y -= 80  # Push enemy back after catch
    


    # Auto-collect all nearby coins while flying
    if player.flying_timer > 0:
        for coin in coins:
            if (not coin.collected and 
                abs(coin.y - distance) < 300):  # Larger collection range when flying
                coin.collected = True
                coins_collected += 1
                
                coin_value = 10
                if player.coin_multiplier_timer > 0:
                    coin_value = 30
                score += coin_value
    else:
        # Normal coin collection (existing code)
        for coin in coins:
            if (not coin.collected and
                abs(coin.x - player.x) < 40 and
                abs(coin.y - (player.y + distance)) < 40 and
                abs(coin.z - player.z) < 40):
                coin.collected = True
                coins_collected += 1
                
                coin_value = 10
                if player.coin_multiplier_timer > 0:
                    coin_value = 30
                score += coin_value
    
    # Check power-up collection
    for power_up in power_ups:
        if (not power_up.collected and
            abs(power_up.x - player.x) < 40 and
            abs(power_up.y - (player.y + distance)) < 40 and
            abs(power_up.z + power_up.float_offset - player.z) < 40):
            power_up.collected = True
            player.activate_power_up(power_up.type)
            score += 50





def update_game():
    global distance, speed, score, last_speed_increase_score
    global last_life_lost_time, life_lost_count
    
    if game_state == GameState.PLAYING:
        current_time = time.time()
        
        # Reset life lost tracking if 20 seconds passed without second life lost
        if (last_life_lost_time is not None and 
            (current_time - last_life_lost_time) > 20 and 
            life_lost_count < 2):
            life_lost_count = 0
            last_life_lost_time = None
            print("Guardian's pursuit cooled down...")
        
        # Update player
        player.update()
        
        # Update chasing enemy
        chasing_enemy.update()
        
        # Calculate current speed with power-up effects
        current_speed = speed
        if player.speed_boost_timer > 0:
            current_speed *= 2.0
        
        # Move forward - FRAME RATE INDEPENDENT
        distance += current_speed * delta_time * 60
        score += 0.2
        
        # Speed increase based on score (every 2500 points)
        score_milestones = int(score // 2500)
        last_milestones = int(last_speed_increase_score // 2500)
        if score_milestones > last_milestones:
            speed += 0.1
            speed = min(speed, 8.0)
            last_speed_increase_score = score
        
        # Generate new track sections
        generate_track()
        
        # Check collisions
        check_collisions()
        
        # Remove old objects
        obstacles[:] = [obs for obs in obstacles if obs.y > distance - 1200]
        coins[:] = [coin for coin in coins if coin.y > distance - 1200]
        power_ups[:] = [pu for pu in power_ups if pu.y > distance - 1200]






def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 1.25, 1, 2000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Third-person camera
    cam_x = player.x
    cam_y = distance - camera_distance
    cam_z = player.z + camera_height
    
    look_x = player.x
    look_y = distance + 50
    look_z = player.z + 10
    
    gluLookAt(cam_x, cam_y, cam_z,
              look_x, look_y, look_z,
              0, 0, 1)



def draw_power_up_status():
    """Draw active power-up indicators"""
    y_offset = 580

    if player.magnet_timer > 0:
        glColor3f(1.0, 0.0, 1.0)
        draw_text(10, y_offset, f"MAGNET: {player.magnet_timer // 60 + 1}s")
        y_offset -= 25

    if player.shield_timer > 0:
        glColor3f(0.0, 1.0, 1.0)
        draw_text(10, y_offset, f"SHIELD: {player.shield_timer // 60 + 1}s")
        y_offset -= 25

    if player.speed_boost_timer > 0:
        glColor3f(1.0, 0.5, 0.0)
        draw_text(10, y_offset, f"SPEED BOOST: {player.speed_boost_timer // 60 + 1}s")
        y_offset -= 25

    if player.double_jump_timer > 0:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(10, y_offset, f"DOUBLE JUMP: {player.double_jump_timer // 60 + 1}s")
        y_offset -= 25

    if player.coin_multiplier_timer > 0:
        glColor3f(1.0, 1.0, 0.0)
        draw_text(10, y_offset, f"COIN x3: {player.coin_multiplier_timer // 60 + 1}s")
        y_offset -= 25

    if player.flying_timer > 0:
        glColor3f(0.5, 0.8, 1.0)
        draw_text(10, y_offset, f"FLYING: {player.flying_timer // 60 + 1}s")
        y_offset -= 25








def keyboardListener(key, x, y):
    global game_state
    
    if game_state == GameState.MENU:
        if key == b' ':
            reset_game()
    elif game_state == GameState.PLAYING:
        if key == b'a':
            player.move_left()
        elif key == b'd':
            player.move_right()
        elif key == b'w':
            player.jump()
        elif key == b's':
            player.slide()
        elif key == b'p':
            game_state = GameState.PAUSED  # Pause the game
    elif game_state == GameState.PAUSED:  # ADD THIS SECTION
        if key == b'p':
            game_state = GameState.PLAYING  # Resume the game
        elif key == b'q':
            game_state = GameState.MENU
    elif game_state == GameState.GAME_OVER:
        if key == b'r':
            reset_game()
        elif key == b'q':
            game_state = GameState.MENU




def specialKeyListener(key, x, y):
    if game_state == GameState.PLAYING:
        if key == GLUT_KEY_LEFT:
            player.move_left()
        elif key == GLUT_KEY_RIGHT:
            player.move_right()
        elif key == GLUT_KEY_UP:
            player.jump()
        elif key == GLUT_KEY_DOWN:
            player.slide()



def mouseListener(button, state, x, y):
    if state == GLUT_DOWN:
        if game_state == GameState.MENU:
            if button == GLUT_LEFT_BUTTON:
                reset_game()
        elif game_state == GameState.PLAYING:
            if button == GLUT_LEFT_BUTTON:
                player.jump()
            elif button == GLUT_RIGHT_BUTTON:
                player.slide()



def idle():
    global delta_time, last_time
    
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    
    if game_state == GameState.PLAYING:
        update_game()
    glutPostRedisplay()




def showScreen():
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    


    if game_state == GameState.MENU:



        # Menu screen
        glClearColor(0.1, 0.1, 0.2, 1.0)
        draw_text(300, 600, "TEMPLE RUN 3D - ENHANCED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 550, "Press SPACE or Click to Start")
        
        draw_text(300, 500, "Controls:")
        draw_text(320, 470, "A/D or Left/Right Arrow: Move lanes")
        draw_text(320, 440, "W or Up Arrow: Jump")
        draw_text(320, 410, "S or Down Arrow: Slide")
        draw_text(320, 380, "Left Click: Jump")
        draw_text(320, 350, "Right Click: Slide")
        
        # Power-ups section
        draw_text(300, 300, "Power-ups:")
        draw_text(320, 270, "Magnet (Purple): Attracts coins")
        draw_text(320, 240, "Shield (Cyan): Temporary invincibility")
        draw_text(320, 210, "Speed Boost (Orange): Double speed")
        draw_text(320, 180, "Double Jump (Green): Jump twice")
        draw_text(320, 150, "Coin Multiplier (Yellow): Triple coin value")
        draw_text(320, 120, "Flying Mode (Light Blue): Fly high & auto-collect coins")
        
        # Game mechanics info
        draw_text(300, 90, "Guardian Enemy:")
        draw_text(320, 60, "Awakens after first mistake - avoid repeated failures!")
        
        draw_text(300, 30, "Speed increases by 0.1 every 2500 points!")
        draw_text(300, 10, "Bonus points for going through obstacles correctly!")






    elif game_state == GameState.PLAYING:
        glClearColor(0.3, 0.5, 0.8, 1.0)
        setup_camera()
        
        # Draw game world
        draw_track()
        draw_environment()
        draw_obstacles()
        draw_coins()
        draw_power_ups()

        # Draw chasing enemy
        draw_chasing_enemy()
        
        # Draw player
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        draw_player()
        glDisable(GL_BLEND)
        
        # Draw UI
        glColor3f(1, 1, 1)
        draw_text(10, 770, f"Score: {int(score)}")
        draw_text(10, 740, f"Distance: {int(distance)}m")
        draw_text(10, 710, f"Coins: {coins_collected}")
        draw_text(10, 680, f"Speed: {speed:.1f}")
        draw_text(10, 650, f"Lives: {player_lives}")
        
        # Show next speed increase progress
        next_milestone = ((int(score // 2500) + 1) * 2500)
        points_needed = next_milestone - int(score)
        draw_text(10, 620, f"Next speed boost: {points_needed} points")
        
        # Draw power-up status
        draw_power_up_status()
        

        # Show life loss message if applicable
        if "lives remaining" in game_over_reason:
            glColor3f(1, 0, 0)
            draw_text(300, 400, game_over_reason, GLUT_BITMAP_HELVETICA_18)


            # Show enemy warning if active and close
        if (chasing_enemy.pursuit_mode and 
            last_life_lost_time is not None):
            time_remaining = 20 - (time.time() - last_life_lost_time)
            if time_remaining > 0 and life_lost_count >= 1:
                glColor3f(1, 0, 0)
                draw_text(10, 590, f"Guardian Alert! Avoid mistakes: {time_remaining:.1f}s")
                
            enemy_distance = distance - chasing_enemy.y
            if enemy_distance < 200:
                if enemy_distance < 50:
                    glColor3f(1, 0, 0)  # Red when very close
                else:
                    glColor3f(1, 1, 0)  # Yellow when close
                draw_text(10, 565, f"Guardian Distance: {int(enemy_distance)}m")
        
        # Show life loss message if applicable
        if "lives remaining" in game_over_reason:
            glColor3f(1, 0, 0)
            draw_text(300, 400, game_over_reason, GLUT_BITMAP_HELVETICA_18)
            

        glColor3f(1, 1, 1)
        draw_text(10, 20, "P - Pause")

        
    elif game_state == GameState.GAME_OVER:
        glClearColor(0.2, 0.1, 0.1, 1.0)
        draw_text(350, 550, "GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(300, 500, game_over_reason)
        draw_text(300, 450, f"Final Score: {int(score)}")
        draw_text(300, 420, f"Distance: {int(distance)}m")
        draw_text(300, 390, f"Coins Collected: {coins_collected}")
        draw_text(300, 360, f"Final Speed: {speed:.1f}")
        draw_text(300, 330, f"Speed Milestones Reached: {int(score // 5000)}")
        draw_text(300, 300, f"Lives Used: {5 - player_lives}")
        draw_text(300, 250, "Press R to Restart")
        draw_text(300, 220, "Press Q for Main Menu")


    elif game_state == GameState.PAUSED:
        # Keep displaying the game scene but with pause overlay
        setup_camera()
        draw_track()
        draw_environment()
        draw_obstacles()
        draw_coins()
        draw_power_ups()
        draw_player()
        
        
        draw_text(400, 400, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 350, "Press P to Resume")
        draw_text(350, 320, "Press Q for Main Menu")
    
    glutSwapBuffers()




def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Temple Run 3D - Enhanced")
    
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    print("Temple Run 3D Enhanced - Controls:")
    print("A/D or Arrow Keys: Change lanes")
    print("W or Up Arrow: Jump")
    print("S or Down Arrow: Slide")
    print("Left Click: Jump")
    print("Right Click: Slide")
    print("P: Pause (during game)")
    print("R: Restart (when game over)")
    print("Q: Main menu (when game over)")
    print("\nPower-ups:")
    print("- Magnet (Purple): Attracts nearby coins")
    print("- Shield (Cyan): Temporary invincibility")
    print("- Speed Boost (Orange): Double movement speed")
    print("- Double Jump (Green): Ability to jump twice")
    print("- Coin Multiplier (Yellow): Triple coin value")
    print("\nSpeed increases by 0.1 every 5000 points!")
    
    glutMainLoop()

    

if __name__ == "__main__":
    main()