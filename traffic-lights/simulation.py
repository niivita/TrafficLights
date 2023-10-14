import pygame
import threading

pygame.init()
simulation = pygame.sprite.Group()





class Main:
    # thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    # thread1.daemon = True
    # thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize TODO: other size?
    screenSize = (1400, 800)

    background = pygame.image.load('background.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("OUR SIMULATION YAY")

    redSignal = pygame.Color.r
    yellowSignal = pygame.Color(255, 255, 0)
    greenSignal = pygame.Color.g
    font = pygame.font.Font(None, 30)

    # thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    # thread2.daemon = True
    # thread2.start()

    pygame.display.init()
    while True:
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         sys.exit()

        screen.blit(background, (0, 0))
        signalTexts = ["", "", "", ""]


        pygame.display.update()



Main()


