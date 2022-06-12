import pygame,sys,random,time
pygame.init()
clock=pygame.time.Clock()

width=850
height=500

class player1(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((width//70,140))
        self.image.fill("red")
        self.rect=self.image.get_rect(midleft=(5,height//2))
        self.speed=12
        
    def userinput(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.y>0:
            self.rect.y-=self.speed
        if keys[pygame.K_s] and self.rect.bottomleft[1]<height:
            self.rect.y+=self.speed
            
    def update(self):
        self.userinput()
        
class player2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((width//70,140))
        self.image.fill("yellow")
        self.rect=self.image.get_rect(midright=(width-5,height//2))
        self.speed=12
        
    def userinput(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.y>0:
            self.rect.y-=self.speed
        if keys[pygame.K_DOWN] and self.rect.bottomleft[1]<height:
            self.rect.y+=self.speed
            
    def update(self):
        self.userinput()
        
class ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface((20,20))
        self.rect=self.image.get_rect(x=width//2,y=height//2)
        pygame.draw.circle(self.image, "green", (10,10),10)
        self.speedx=7*random.choice((-1,1))
        self.speedy=7*random.choice((-1,1))
        
    def collision(self):
        if self.rect.top<=0:
            self.rect.top=0
            self.speedy*=-1
        if self.rect.bottom>=height:
            self.rect.bottom=height
            self.speedy*=-1
        
    def update(self):
        self.collision()
        self.rect.x+=self.speedx
        self.rect.y+=self.speedy
        
class mirror(pygame.sprite.Sprite):
    def __init__(self,direc,pos,collisions=0):
        pygame.sprite.Sprite.__init__(self)
        self.direc=direc
        self.pos=pos
        self.collisions=collisions
        if(self.direc=='v'):
            self.image=pygame.Surface((3,height))
            self.rect=self.image.get_rect(center=(pos,height//2))
        else:
            self.image=pygame.Surface((width,3))
            self.rect=self.image.get_rect(center=(width//2,pos))
        self.color="light blue"
        self.image.fill(self.color)
        
    def color_change(self):
        if self.collisions==0:
            self.color="light blue"
        elif self.collisions==1:
            self.color="orange"
        else:
            self.color="red"
    
    def update(self):
        self.color_change()
        self.image.fill(self.color)
        
class mirror_image(pygame.sprite.Sprite):
    def __init__(self,loc):
        pygame.sprite.Sprite.__init__(self)
        self.loc=loc
        self.image=pygame.Surface((20,20))
        self.rect=self.image.get_rect(center=loc)
        pygame.draw.circle(self.image, "blue",(10,10),10,3)
        
class level:
    def __init__(self,screen,mirrors,state):
        self.screen=screen
        self.mirrors=mirrors
        self.state=state
        self.pong_sound=pygame.mixer.Sound('pong.wav')
        self.p1_score=0
        self.p2_score=0
        self.score_time=False
        self.game_font=pygame.font.Font('freesansbold.ttf',32)
        self.over=False
        self.setup()
            
    def setup(self):
        self.player1_grp=pygame.sprite.GroupSingle()
        self.player2_grp=pygame.sprite.GroupSingle()
        self.ball_grp=pygame.sprite.GroupSingle()
        self.mirror_grp=pygame.sprite.Group(self.mirrors)
        self.mirror_image_grp=pygame.sprite.Group()
        self.player1_grp.add(player1())
        self.player2_grp.add(player2())
        self.ball_grp.add(ball())
        
    def collision(self):
        p1=self.player1_grp.sprite
        p2=self.player2_grp.sprite
        b=self.ball_grp.sprite
        m=self.mirror_grp.sprites()
        if p2.rect.colliderect(b.rect):
            if abs(b.rect.right - p2.rect.left)<10:
                b.speedx*=-1
            elif abs(b.rect.bottom-p2.rect.top)<10 and b.speedy>0:
                b.speedy*=-1
            elif abs(b.rect.top-p2.rect.bottom)<10 and b.speedy<0:
                b.speedy*=-1
            pygame.mixer.Sound.play(self.pong_sound)
        if p1.rect.colliderect(b.rect):
            if abs(b.rect.left - p1.rect.right)<10:
                b.speedx*=-1
            elif abs(b.rect.bottom-p1.rect.top)<10 and b.speedy>0:
                b.speedy*=-1
            elif abs(b.rect.top-p1.rect.bottom)<10 and b.speedy<0:
                b.speedy*=-1
            pygame.mixer.Sound.play(self.pong_sound)
        for spt in m:
            if spt.rect.colliderect(b.rect):
                spt.collisions+=1
                pygame.mixer.Sound.play(self.pong_sound)
                if spt.direc=='h':
                    if spt.collisions>2:
                        b.speedx*=-1
                        spt.collisions=0
                        if b.speedy>0: b.rect.y+=20
                        else: b.rect.y-=20
                    else:
                        b.speedy*=-1
                else: 
                    if spt.collisions>2:
                        b.speedy*=-1
                        spt.collisions=0
                        if b.speedx>0: b.rect.x+=20
                        else: b.rect.x-=20
                    else:
                        b.speedx*=-1
                
    def reflect(self):
        m=self.mirror_grp.sprites()
        b=self.ball_grp.sprite
        mi=self.mirror_image_grp
        mi.empty()
        for spt in m:
            if spt.direc=='h':
                mi.add(mirror_image((b.rect.centerx,2*spt.pos-b.rect.centery)))
            else:
                mi.add(mirror_image((2*spt.pos-b.rect.centerx,b.rect.centery)))
                
    def opponent_movement(self):
        p1=self.player1_grp.sprite
        b=self.ball_grp.sprite
        if p1.rect.top<b.rect.y:
            p1.rect.top+=p1.speed
        if p1.rect.bottom>b.rect.y:
            p1.rect.bottom-=p1.speed
        if p1.rect.top<=0:
            p1.rect.top=0
        if p1.rect.bottom>=height:
            p1.rect.bottom=height
            
    def score(self):
        b=self.ball_grp.sprite
        if b.rect.left<=0:
            self.p2_score+=1
            self.score_time=pygame.time.get_ticks()
        elif b.rect.right>=width:
            self.p1_score+=1
            self.score_time=pygame.time.get_ticks()
        score_1=self.game_font.render(f'{self.p1_score}',False,'red')
        score_2=self.game_font.render(f'{self.p2_score}',False,'yellow')
        self.screen.blit(score_1, (10,10))
        self.screen.blit(score_2, (width-30,10))
        
        exit_but=pygame.transform.scale(pygame.image.load("but 3.png").convert_alpha(),(50,30))
        exit_rect=exit_but.get_rect(center=(width//2,height-20))
        self.screen.blit(exit_but,exit_rect)
        font=pygame.font.Font('freesansbold.ttf',100)
        if exit_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.over=True
        elif self.p1_score==10 and self.state==1:
            txt=font.render('You lost!',False,'red')
            self.screen.blit(txt, txt.get_rect(center=(width//2,height//2)))
            self.over=True
            pygame.display.update()
            time.sleep(2)
        elif self.p2_score==10 and self.state==1:
            self.font.render('You won!',False,'green')
            self.screen.blit(txt, txt.get_rect(center=(width//2,height//2)))
            self.over=True
            pygame.display.update()
            time.sleep(2)
        elif self.p1_score==10 and self.state==2:
            txt=font.render('Red won!',False,'red')
            self.screen.blit(txt,txt.get_rect(center=(width//2,height//2)))
            self.over=True
            pygame.display.update()
            time.sleep(2)
        elif self.p2_score==10 and self.state==2:
            txt=font.render('Yellow won!',False,'yellow')
            self.screen.blit(txt, txt.get_rect(center=(width//2,height//2)))
            self.over=True
            pygame.display.update()
            time.sleep(2)
            
    def restart_ball(self):
        b=self.ball_grp.sprite
        current_time=pygame.time.get_ticks()
        b.rect.center=(width//2,height//2)
        if current_time-self.score_time<700:
            number_three=self.game_font.render('3',False,'white')
            self.screen.blit(number_three,(width//2-10,height//2+20))
        if 700<current_time-self.score_time<1400:
            number_two=self.game_font.render('2',False,'white')
            self.screen.blit(number_two,(width//2-10,height//2+20))
        if 1400<current_time-self.score_time<2100:
            number_one=self.game_font.render('1',False,'white')
            self.screen.blit(number_one,(width/2-20,height/2+20))

        if current_time-self.score_time<2100:
            b.speedx,b.speedy=0,0
        else:
            b.speedx=7*random.choice((1,-1))
            b.speedy=7*random.choice((1,-1))
            self.score_time=None
        
            
    def run(self):
        self.collision()
        self.reflect()
        if self.state==2: self.player1_grp.update()
        else: self.opponent_movement()
        self.player2_grp.update()
        self.ball_grp.update()
        self.mirror_grp.update()
        self.score()
        if self.score_time: self.restart_ball()
        self.player1_grp.draw(self.screen)
        self.player2_grp.draw(self.screen)
        self.mirror_grp.draw(self.screen)
        self.mirror_image_grp.draw(self.screen)
        self.ball_grp.draw(self.screen)

            
class game():
    def __init__(self):
        self.screen=pygame.display.set_mode((width,height))
        self.button_sound=pygame.mixer.Sound('button.wav')
        self.setup()
        self.run()
        
    def start(self):
        pos=pygame.mouse.get_pos()
        
        if not self.state:
            if self.rectpl_1.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectpl_1.inflate(6, 6))
                if not self.hover1:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover1=True
                if pygame.mouse.get_pressed()[0]:
                    self.state=1
                    time.sleep(0.3)
            elif self.rectpl_2.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectpl_2.inflate(6, 6))
                if not self.hover1:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover1=True
                if pygame.mouse.get_pressed()[0]:
                    self.state=2
                    time.sleep(0.3)
            else: self.hover1=False
            self.screen.blit(self.play_1,self.rectpl_1)
            self.screen.blit(self.play_2,self.rectpl_2)
            
        elif not self.lvl:
            if self.rectrm_1.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectrm_1.inflate(6, 6))
                if not self.hover2:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover2=True
                if pygame.mouse.get_pressed()[0]:
                    self.level=level(self.screen,[],self.state)
                    self.lvl=1
            elif self.rectrm_2.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectrm_2.inflate(6, 6))
                if not self.hover2:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover2=True
                if pygame.mouse.get_pressed()[0]:
                    self.level=level(self.screen,[mirror('v',350)],self.state)
                    self.lvl=1
            elif self.rectrm_3.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectrm_3.inflate(6, 6))
                if not self.hover2:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover2=True
                if pygame.mouse.get_pressed()[0]:
                    self.level=level(self.screen,[mirror('v',350),mirror('v',500)],self.state)
                    self.lvl=1
            elif self.rectrm_4.collidepoint(pos):
                pygame.draw.rect(self.screen,'green',self.rectrm_4.inflate(6, 6))
                if not self.hover2:
                    pygame.mixer.Sound.play(self.button_sound)
                    self.hover2=True
                if pygame.mouse.get_pressed()[0]:
                    self.level=level(self.screen,[mirror('v',500),mirror('h',300)],self.state)
                    self.lvl=1
            else: self.hover2=False
            self.screen.blit(self.room_1,self.rectrm_1)
            self.screen.blit(self.room_2,self.rectrm_2)
            self.screen.blit(self.room_3,self.rectrm_3)
            self.screen.blit(self.room_4,self.rectrm_4)
            
        else:
            self.screen.fill('black')
            self.level.run()
            if self.level.over:
                self.lvl=0
            
    def setup(self):
        self.state=0
        self.lvl=0
        self.hover1=False
        self.hover2=False
        self.play_1=pygame.transform.scale(pygame.image.load("but 1.png").convert_alpha(),(200,120))
        self.play_2=pygame.transform.scale(pygame.image.load("but 2.png").convert_alpha(),(200,120))
        self.rectpl_1=self.play_1.get_rect(center=(250,height//2))
        self.rectpl_2=self.play_2.get_rect(center=(600,height//2))
        self.room_1=pygame.transform.scale(pygame.image.load("but 4.png").convert_alpha(),(150,90))
        self.room_2=pygame.transform.scale(pygame.image.load("but 5.png").convert_alpha(),(150,90))
        self.room_3=pygame.transform.scale(pygame.image.load("but 6.png").convert_alpha(),(150,90))
        self.room_4=pygame.transform.scale(pygame.image.load("but 7.png").convert_alpha(),(150,90))
        self.rectrm_1=self.room_1.get_rect(center=(125,height//2))
        self.rectrm_2=self.room_2.get_rect(center=(325,height//2))
        self.rectrm_3=self.room_3.get_rect(center=(525,height//2))
        self.rectrm_4=self.room_4.get_rect(center=(725,height//2))
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill('black')
            self.start()
            pygame.display.update()
            clock.tick(60)
            
game()
