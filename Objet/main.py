ready = False
import time
import cv2
import numpy as np
import screeninfo
from parameters import Parameters 
from image_processor import ImageProcessing  
from display import Display
from video_manager import VideoManager
from ui import UI
from trajectory import Trajectory
from session import Session
import gestion_clavier as gc

class Main:
    def __init__(self, video_file, video_type):
        # Initialisation de tous les objets
        screeninfo.get_monitors()[0] 

        self.param = Parameters()         
        self.sound = False
        self.vid_mana = VideoManager(video_file, self.param, self.sound, video_type)
        self.im_proc = ImageProcessing(self.param, ia=False)
        self.im_proc.update_prev_frame(self.vid_mana.frame)
        self.traj = Trajectory(self.param)
        self.display = Display(self.param)
        self.display.load_frame(self.vid_mana.frame)
        self.display.load_traj(self.traj)
        self.ui = UI(self.param, self.display, self.vid_mana)
        self.session = Session(video_file, self.vid_mana)
    

        #vid_mana.play_sound()
        self.vid_mana.start_time = time.time()
        self.mode = "video"
        self.prev_mode = "video"


    def run(self):
        global ready
        ready = True
        while self.mode != "over":
            self.display.load_frame(self.vid_mana.frame)
            key = cv2.waitKey(1) & 0xFF 
            self.prev_mode, self.mode = gc.update(key, self.vid_mana, self.session, self.ui, self.param, self.prev_mode, self.mode)    
            self.ui.move_parameters()    

            if self.mode == "video":
                self.vid_mana.update_frame()
                if self.vid_mana.over:
                    break
                all_ball = self.im_proc.get_all_ball(self.vid_mana.frame)
                self.traj.update(all_ball) 
                if self.traj.is_over:
                    self.session.load_traj(self.traj)
                    self.traj = Trajectory(self.param)
                    self.display.load_traj(self.traj)
                    self.session.next_video()
            elif self.mode == "parameters":
                darken_factor = 0.5 
                self.display.frame = (self.display.frame * darken_factor).astype(np.uint8)

 
            self.display.display(self.ui.brightness)
            #self.session.load(self.display.frame)
            #cv2.imshow('main', im_proc.processed_frame_difference)

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main = Main("vid4.mp4", "video")
    main.run()

def is_ready():
    return ready