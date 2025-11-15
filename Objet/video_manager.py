import cv2
import time  
from moviepy import VideoFileClip
import os 
import sys 
sys.stdout = open(os.devnull, "w") 
import pygame
sys.stdout = sys.__stdout__
import subprocess



class VideoManager:
    def __init__(self, video_file, parameters, sound, video_type):
        self.video_file = video_file    
        self.video_type = video_type
        self.new_frame_treated = True
        if self.video_type == "video":
            self.cap = cv2.VideoCapture(self.video_file)
        elif self.video_type == "direct":
            self.list_cameras = self.search_cameras()
            if len(self.list_cameras) == 0:
                raise ValueError("Aucune caméra disponible.")
            self.index = 0
            self.cap = cv2.VideoCapture(self.list_cameras[self.index])

        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        #self.fps = 3
        self.fps_type = "real"
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.over = False
        self.parameters = parameters

        self.start_time = time.time()
        self.current_time = time.time()
        self.time_video = self.current_time - self.start_time

        self.sound = sound

        self.init_frame()
    
    def init_frame(self):
        _, self.frame = self.cap.read()
        if self.frame is None:
            raise ValueError("Impossible de charger les images. Vérifiez les chemins des fichiers.")
        self.frame = cv2.resize(self.frame, (self.parameters.width, self.parameters.height))
        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def next_camera(self):
        self.index += 1
        if self.index >= len(self.list_cameras):
            self.index = 0
        self.cap.release()
        self.cap = cv2.VideoCapture(self.list_cameras[self.index])
        self.init_frame()
    
    def prev_camera(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.list_cameras) - 1
        self.cap.release()
        self.cap = cv2.VideoCapture(self.list_cameras[self.index])
        self.init_frame()

 
    def search_cameras(self):
        max_cameras=10
        backend=cv2.CAP_DSHOW
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        return available_cameras
        
    def play_sound(self):
        # Initialiser pygame pour l'audio
        pygame.mixer.init()

        # Extraire l'audio de la vidéo avec moviepy
        video_clip = VideoFileClip(self.video_file)
        self.audio = video_clip.audio

        # Sauvegarder l'audio sous un fichier temporaire pour pygame
        self.audio_file = "temp_audio.wav"
        self.audio.write_audiofile(self.audio_file)

        # Charger l'audio dans pygame
        self.sound = pygame.mixer.Sound(self.audio_file)
        self.sound.play()

    def is_not_over(self):
        return not self.over

    def pause(self):
        self.stop_time = time.time()
    
    def resume(self):
        self.start_time += time.time() - self.stop_time
        
    def update_frame(self):

        if self.video_type == "video":
            self.current_time = time.time()
            self.time_video = self.current_time - self.start_time
            self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame_targeted = int(self.time_video * self.fps)
            jump_frame = frame_targeted - self.current_frame

            self.new_frame_treated = False
            for _ in range(jump_frame):
                ret, self.frame = self.cap.read()
                if not ret:
                    self.over = True
                    break
                self.new_frame_treated = True
                self.current_frame += 1  

            if not self.over:
                self.frame = cv2.resize(self.frame, (self.parameters.width, self.parameters.height))
        
        elif self.video_type == "direct":
            self.update_frame_easy()
            self.current_frame += 1

    def update_frame_easy(self):
        _, self.frame = self.cap.read()
        self.frame = cv2.resize(self.frame, (self.parameters.width, self.parameters.height))


    def stop(self):
        self.over = True

    def change_fps(self):
        if self.fps_type == "real":
            self.fps_type = "fixed"
            self.fps = 3
        else:
            self.fps_type = "real"
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
    
if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])

