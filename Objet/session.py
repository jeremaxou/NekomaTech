import cv2
import time
import os
import subprocess


class Session:
    def __init__(self, video_file, vid_mana):
        self.name = video_file
        self.time = time.time()
        self.fps = vid_mana.fps
        self.width = vid_mana.parameters.width
        self.height = vid_mana.parameters.height
        self.video_list = [[]]
        self.traj_list = []
    
    def load(self, frame):
        self.video_list[-1].append(frame)
    
    def load_traj(self, traj):
        self.traj_list.append(traj)
    
    def next_video(self):
        self.video_list.append([])
    
    def save(self):        

        # Ajouter chaque frame à la vidéo
        output_dir = r"C:\Users\jerem\CentraleSupelec\1A\Cours\S6\Projet\video"
        os.makedirs(output_dir, exist_ok=True)
        count = 0
        for video in self.video_list:
            output_path = os.path.join(output_dir, f"extract_{count}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec pour MP4
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
            count += 1
            for frame in video:
                out.write(frame)

            # Fermer l'écriture de la vidéo
            out.release()

        output_path = os.path.join(output_dir, "all.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec pour MP4
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        for video in self.video_list:
            for frame in video:
                out.write(frame)

            # Fermer l'écriture de la vidéo
        out.release()


if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])