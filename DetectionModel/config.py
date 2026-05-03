class Config:
    '''Only contains the physics variables'''
    DEBUG_MODE = False
    VISUAL_MODE = False
    FRAME_SKIP = 4
    THRESHOLD = 0.01
    HAND_TRACK = [
            (0,1),(1,2),(2,3),(3,4), # Thumb
            (0,5),(5,6),(6,7),(7,8), # Index
            (0,9),(9,10),(10,11),(11,12), # Middle
            (0,13),(13,14),(14,15),(15,16), # Ring
            (0,17),(17,18),(18,19),(19,20) # Pinky
    ]
    EMA_ALFA = 0.3