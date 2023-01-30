from pygame import *
from pygame import mixer
import pickle
from os import path

win_width = 1000
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption('Platformer')

hell = transform.scale(image.load('background.jpg'), (win_width, win_height))
restart_img = image.load('restart.png')
start_img = image.load('start_btn.png')

#font = font.SysFont('Bauhaus 93', 70)
blue = (0,0,255)
size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 2

mixer.init()
mixer.music.load('castle.mp3')
mixer.music.set_volume(0.1)
mixer.music.play(-1)

#def draw_text(text, font, text_col, x, y):
    #img = font.render(text, True, text_col)
    #window.blit(img(x, y))


def reset_level(level):
    player.reset(0,600)
    skelet_enemy_group1.empty()
    exit_group.empty()  
    bullets.empty()
    #load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)   
    return world    

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		window.blit(self.image, self.rect)

		return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)
        self.direction = 0
    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        
        if game_over == 0:
        #get keypresses
            keys = key.get_pressed()
            if keys[K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -17
                self.jumped = True
            if keys[K_SPACE] == False:
                self.jumped = False
            if keys[K_LALT] and self.gun == 0:
                player.shoot()
                self.gun = self.counter_gun
            if self.gun > 0: 
                self.gun -= 1
            if keys[K_LEFT]:
                dx -= 3
                self.counter += 1
                self.direction = -1
            if keys[K_RIGHT]:
                dx += 3
                self.counter += 1
                self.direction = 1
                
            if keys[K_LEFT] == False and keys[K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.image_right[self.index]
                if self.direction == -1:
                    self.image = self.image_left[self.index]     
                    
                    
            #handle animation
            if self.counter > walk_cooldown:
                self.counter = 0	
                self.index += 1
                if self.jumped == False:
                    if self.index >= len(self.image_right):
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.image_right[self.index]
                    if self.direction == -1:
                        self.image = self.image_left[self.index]
                        
                # elif self.vel_y != 10:
                #     if self.index >= len(self.image_jump_right):
                #         self.index = 0
                #     if self.direction == 1:
                #         self.image = self.image_jump_right[self.index]
                #     if self.direction == -1:
                #         self.image = self.image_jump_left[self.index]
            #add gravit 

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y        
            
            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom -self.rect.top
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.in_air = False
            if sprite.spritecollide(self, skelet_enemy_group1, False):
                game_over = -1    
            if sprite.spritecollide(self, spike_group, False):
                game_over = -1
            if sprite.spritecollide(self, exit_group, False):
                game_over = 1
            
            
            #check for collision        
            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy       
            if self.rect.bottom > win_height:
                self.rect.bottom = win_height
            dy = 0


        elif game_over == -1:
            #draw_text('GAME OVER!', font,blue, (win_width // 2) - 140, win_height // 2)
            if self.dead == 0:
                self.dead = -1  
                self.image = self.dead_image
                x = self.rect.x
                y = self.rect.y 
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y+40
            
        
        window.blit(self.image, (self.rect.x, self.rect.y))
        draw.rect(window, (255,255,255), self.rect, -1)
        return game_over
    def reset(self, x, y):
        self.image_right = []
        self.image_left = []
        #self.image_jump_right = []
        #self.image_jump_left = []
        self.dead = 0
        self.index = 0
        self.counter = 0
        for num in range(1, 8):
            
            img_right = image.load(f'skelet{num}.png')
            img_right = transform.scale(img_right, (48,48))
            img_left = transform.flip(img_right, True, False)
            self.image_right.append(img_right)
            self.image_left.append(img_left)

        self.dead_image  = image.load('dead.png')
        #self.dead_image = transform.scale(dead_img,(50,50))
        self.image = self.image_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.gun = 0
        self.counter_gun = 240
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullets.add(bullet)


class Bullet(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        img = image.load('sword.png')
        self.image = transform.scale(img, (35,25))
        self.rect = self.image.get_rect()
        self.rect.top = y + 10
        self.rect.left = x +10
        self.rect.right = x
        self.speedy = 10
        self.direction = player.direction

    def update(self):
        self.rect.x += self.speedy
        for tile in world.tile_list:
            if Rect.colliderect(self.rect, tile[1]):
                self.kill()
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.right < 0:
            self.kill()
        if self.direction == -1:
            self.speedy = -10
            self.rect.right = self.rect.right
            img = image.load('sword1.png')
            self.image = transform.scale(img, (35,25))


            
class World():
    def __init__(self, data):
        self.tile_list = []
        dirt_png = image.load('dirt.png')
        grass_png = image.load('grass.png')
        platform_png = image.load('platform_x.png')
        exit_png = image.load('exit.png')
        row_count = 0
        for row in data:
            col_count = -1
            for tile in row:
                if tile == 1:
                    img = transform.scale(dirt_png, (size, size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * size 
                    img_rect.y = row_count * size 
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    skelet_enemy1 = Enemy(col_count * size, row_count * size+ 10)
                    skelet_enemy_group1.add(skelet_enemy1)
                if tile == 2:
                    img = transform.scale(grass_png, (size, size ))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * size 
                    img_rect.y = row_count * size 
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    exit = Exit(col_count * size, row_count * size )
                    exit_group.add(exit)
                col_count += 1
            row_count += 1
    def draw(self):
            for tile in self.tile_list:
                window.blit(tile[0], tile[1])
                draw.rect(window,(255,255,255), tile[1], -1)
                
class Enemy(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image_right1 = []
        self.image_left1 = []
        
        self.index1 = 0
        for num1 in range(1, 5):
            img_right = image.load(f'enemy{num1}.png')
            img_right = transform.scale(img_right, (40,40))
            img_left = transform.flip(img_right, True, False)
            self.image_right1.append(img_right)
            self.image_left1.append(img_left)
        self.image = self.image_right1[self.index1]
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        
        self.direction1 = 0
    def update(self):
        walk_cooldown = 5
        self.rect.x += self.move_direction
        
        self.move_counter += 1
        self.counter1 = 0
        
        if abs(self.move_counter) > 100:
            self.move_direction *= -1
            self.move_counter *= -1
            
            
            
            #ПЫТАЮСЬ СДЕЛАТЬ АНИМАЦИЮ
            if self.move_direction == -1:
                self.direction1 = -1
                self.index1 +=1
            elif self.move_direction == 1:
                self.direction = 1
                self.index1 +=1
            if self.direction1 > walk_cooldown:
                self.direction1 = 0	
                self.index1 += 1
                if self.index1 >= len(self.image_right1):
                    self.index1 = 0
                if self.direction1== 1:
                    self.image = self.image_right1[self.index1]
                if self.direction1 == -1:
                    self.image = self.image_left1[self.index1]
                    
                    
                    
class Exit(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        img = image.load('exit.png')
        self.image = transform.scale(img, (50,50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
def draw_grid():
    for line in range(0, 20):
        draw.line(window, (255,255,255), (0, line * size), (win_width, line * size), 0)
        draw.line(window, (255,255,255), (line * size ,0), (line * size, win_height), 0)
        


player = Player(0, 600)
skelet_enemy_group1 = sprite.Group()
skelet_enemy_group2 = sprite.Group()
spike_group = sprite.Group()
exit_group = sprite.Group()
restart_button = Button(400,250, restart_img)
start_button = Button(350,250, start_img)
bullets = sprite.Group()

timer = time.Clock()
FPS = 60

if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)        




run = True
while run:
    timer.tick(60)
    window.blit(hell, (0, 0))
    if main_menu == True:
        #if exit_button.draw():
            #run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()
        game_over = player.update(game_over)
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                #draw_text('YOU WIN!', font,blue, (win_width // 2) - 140, win_height // 2)
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
        if game_over == 0:
            skelet_enemy_group1.update()
        skelet_enemy_group1.draw(window)
        exit_group.draw(window)
        spike_group.draw(window)
        bullets.draw(window)
        bullets.update()
        hits = sprite.groupcollide(skelet_enemy_group1, bullets, True, True)
        draw_grid()
    display.update()
    #Eto grupa a ne tupl
    for e in event.get():
        if e.type == QUIT:
            run = False