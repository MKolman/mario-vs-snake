import pygame


SIRINA_EKRANA = 800
VISINA_EKRANA = 600

MARIO_BARVA = (255, 0, 0)
KACA_BARVA = (0, 255, 0)
OZADJE_BARVA = (200, 200, 255)
PLOSCAD_BARVA = (139, 69, 19)


class Mario(pygame.sprite.Sprite):
    """Igralec, ki skace"""

    def __init__(self, ovire=None):
        """ Konstruktor """
        super().__init__()

        # Stevci za slike
        self.tek_slike = 0
        self.tek_loop = 20
        self.mir_slike = 0
        self.mir_loop = 24
        self.flip = False

        # Ustvari sliko in območje za igralca
        self.sirina = 50
        self.visina = 72
        self.image = pygame.Surface([self.sirina, self.visina], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.images = pygame.image.load("spritesheet.png")
        # self.image.fill(MARIO_BARVA)
        # self.image.blit(self.images, (0, 0), (0, 0, 55, 75))
        self.set_image()

        self.hitrost_x = 0
        self.hitrost_y = 0

        self.ovire = ovire

        self.dvojni_skok = False

    def set_image(self, akcija="mir"):
        self.image.fill((0, 0, 0, 0))
        if akcija == "mir":
            n = self.mir_slike // (self.mir_loop / 4)
            self.image.blit(self.images, (0, 0), (56*n, 169, 56*n+50, 241))
        if akcija == "tek":
            n = self.tek_slike // (self.tek_loop / 4)
            self.image.blit(self.images, (0, 0), (55*n+5, 4, 55*(n+1), 76))
        if akcija == "let":
            self.image.blit(self.images, (0, 0), (2, 248, 52, 320))
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """ Premakni mariota """

        # ======= Smer x =========
        self.rect.x += self.hitrost_x
        # Rob ekrana
        if self.rect.x > SIRINA_EKRANA:
            self.rect.x = 0
        if self.rect.x < 0:
            self.rect.x = SIRINA_EKRANA
        # Ovire
        zadetki = pygame.sprite.spritecollide(self, self.ovire, False)
        for ovira in zadetki:
            if self.hitrost_x > 0:
                # Ce se premikamo desno se postavimo na levo od ovire
                self.rect.right = ovira.rect.left
            elif self.hitrost_x < 0:
                # Ce se premikamo levo se postavimo na desno od ovire
                self.rect.left = ovira.rect.right
        if self.hitrost_x:
            self.flip = False
            if self.hitrost_x < 0:
                self.flip = True
            self.tek_slike += 1
            self.tek_slike %= self.tek_loop
            self.set_image("tek")
        else:
            self.mir_slike += 1
            self.mir_slike %= self.mir_loop
            self.set_image("mir")

        # ======= Smer y =========
        self.gravitacija()
        self.rect.y += self.hitrost_y
        # Rob ekrana
        if self.rect.y > VISINA_EKRANA:
            self.rect.y = 0
        if self.rect.y < 0:
            self.rect.y = VISINA_EKRANA
        # Ovire
        zadetki = pygame.sprite.spritecollide(self, self.ovire, False)
        for ovira in zadetki:
            if self.hitrost_y > 0:
                # Ce se premikamo dol se postavimo na oviro
                self.hitrost_y = 0
                self.rect.bottom = ovira.rect.top
                self.dvojni_skok = False
            elif self.hitrost_y < 0:
                # Ce se premikamo gor se postavimo pod ovire
                self.hitrost_y = 0
                self.rect.top = ovira.rect.bottom
        if self.hitrost_y:
            self.set_image("let")

    def gravitacija(self):
        """ Nastavi gravitacijo """
        if self.hitrost_y == 0:
            self.hitrost_y = 1
        else:
            if self.hitrost_y < 6:
                self.hitrost_y += .35

    def pojdi_levo(self):
        """ Ko pritisne tipko levo """
        self.hitrost_x = -3

    def pojdi_desno(self):
        """ Ko pritisne tipko desno """
        self.hitrost_x = 3

    def stop(self):
        """ Ko spusti tipko levo/desno """
        self.hitrost_x = 0

    def skoci(self):
        """ Ko spusti tipko levo/desno """
        prej = len(pygame.sprite.spritecollide(self, self.ovire, False))
        self.rect.y += 2
        potem = len(pygame.sprite.spritecollide(self, self.ovire, False))
        self.rect.y -= 2
        if potem - prej >= 1:
            self.hitrost_y = -10
        elif not self.dvojni_skok:
            self.hitrost_y = -10
            self.dvojni_skok = True


class KosKace(pygame.sprite.Sprite):
    """ Snake """
    def __init__(self, x, y):
        """ Konstruktor. """
        super().__init__()

        self.velikost = 30
        self.image = pygame.Surface([self.velikost, self.velikost])
        self.image.fill(KACA_BARVA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Kaca(object):
    """ Snake """
    def __init__(self, x=0, y=0, kosi=10):
        # Naredi hranilnike za vse kose kace
        self.deli = pygame.sprite.Group()
        self.deli_sorted = [KosKace(x, y)]
        self.deli.add(self.deli_sorted[0])

        # Doloci smer premikanja kace
        self.smer = (1, 0)
        # Na koliko iteracij se premakne za eno mesto?
        self.hitrost = 5
        self.countdown = 0

        for i in range(kosi):
            self.dodaj_kos()

    def dodaj_kos(self):
        rit = self.deli_sorted[0].rect
        self.deli_sorted.append(KosKace(rit.x, rit.y))
        self.deli.add(self.deli_sorted[-1])

    def update(self):
        self.countdown += 1
        if self.countdown > self.hitrost:
            self.countdown = 0
            self.deli_sorted[-1].rect.x = self.deli_sorted[0].rect.x + \
                self.smer[0] * self.deli_sorted[0].velikost
            self.deli_sorted[-1].rect.x %= SIRINA_EKRANA
            self.deli_sorted[-1].rect.y = self.deli_sorted[0].rect.y + \
                self.smer[1] * self.deli_sorted[0].velikost
            self.deli_sorted[-1].rect.y %= VISINA_EKRANA
            self.deli_sorted = [self.deli_sorted[-1]] + self.deli_sorted[:-1]

    def draw(self, ekran):
        self.deli.draw(ekran)


class Ploscad(pygame.sprite.Sprite):
    """ Ploscada na katero lahko mario skace """

    def __init__(self, sirina, visina):
        """ Konstruktor. """
        super().__init__()

        self.image = pygame.Surface([sirina, visina])
        self.image.fill(PLOSCAD_BARVA)

        self.rect = self.image.get_rect()


class Level(object):
    """ Opisni razred za vse nivoje igre. """

    def __init__(self):
        """ Konstruktor """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(OZADJE_BARVA)

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self):
        """ Create level 1. """

        # Call the parent constructor
        super().__init__()

        # Array with width, height, x, and y of platform
        level = [[210, 70, 500, 500],
                 [210, 70, 200, 400],
                 [210, 70, 600, 300],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Ploscad(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)


def main():
    """ Main program """
    # Naredi ekran
    velikost = [SIRINA_EKRANA, VISINA_EKRANA]
    ekran = pygame.display.set_mode(velikost)
    pygame.display.set_caption("Mario vs Snake")

    # Naredi level
    level = Level_01()

    # sprites = level.platform_list
    sprites = pygame.sprite.Group()

    # Naredi Mariota
    mario = Mario(level.platform_list)
    mario.rect.x = 200
    mario.rect.y = 200
    sprites.add(mario)

    kaca = Kaca()

    ura = pygame.time.Clock()

    konec = False
    while not konec:
        # Naredi vse kar je potrebno glede na uporabnikove pritisnjene tipke
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                konec = True
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    konec = True
                    break
                if event.key == pygame.K_LEFT:
                    mario.pojdi_levo()
                if event.key == pygame.K_RIGHT:
                    mario.pojdi_desno()
                if event.key == pygame.K_UP:
                    mario.skoci()
                if event.key == pygame.K_w:
                    kaca.smer = (0, -1)
                if event.key == pygame.K_s:
                    kaca.smer = (0, 1)
                if event.key == pygame.K_a:
                    kaca.smer = (-1, 0)
                if event.key == pygame.K_d:
                    kaca.smer = (1, 0)
                if event.key == pygame.K_q:
                    kaca.dodaj_kos()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and mario.hitrost_x < 0:
                    mario.stop()
                if event.key == pygame.K_RIGHT and mario.hitrost_x > 0:
                    mario.stop()

        # Pokliči posodabljanje vseh elementov
        level.platform_list.update()
        sprites.update()
        kaca.update()
        # Nariši vse elemente
        level.draw(ekran)
        sprites.draw(ekran)
        kaca.draw(ekran)
        pygame.display.flip()
        # Počakaj za 20 fps
        ura.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
