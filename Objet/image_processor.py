import cv2
import numpy as np
import parameters
import subprocess

class ImageProcessing:
    def __init__(self, parameters, ia):
        '''construit l'objet avec des paramètres et une frame d'entrée'''
        self.param = parameters
        self.ia = ia
        self.prev_frame = np.zeros((self.param.height, self.param.width, 3), dtype=np.uint8)
        self.next_frame = np.zeros((self.param.height, self.param.width, 3), dtype=np.uint8)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=70, detectShadows=False)

        if self.ia:
            self.best_ball = [[0, 0]]
            from ultralytics import YOLO
            #self.model = YOLO("detection_mire_automatique/runs/detect/train5/weights/best.pt")
            self.model = YOLO("detection_mire_automatique2/weights/best.pt")
            # Détecter si on peut utiliser le GPU
            #self.device = "cuda" if torch.cuda.is_available() else "cpu"
            #self.model.to(self.device)  # Déplacer le modèle sur le GPU
            if self.device == "cuda":
                self.model.half()

    def get_all_ball(self, next_frame):
        self.update_next_frame(next_frame)
        if self.ia:
            return self.ia_method()
        #return self.difference_method()
        return self.background_method()
    
    def ia_method(self):
        # Faire une prédiction sur une image
        #next_frame = cv2.cvtColor(next_frame, cv2.COLOR_BGR2RGB)
        new_width = 1000
        new_height = 600
        resized_frame = cv2.resize(self.next_frame, (new_width, new_height))
        #with torch.no_grad():  # 🚀 Désactive le calcul du gradient
        results = self.model(resized_frame, verbose=False, conf=0.01)
        #results = self.model(next_frame, verbose=False)
    
        best_confidence = 0  # Valeur minimale de confiance

        for result in results:
            for box in result.boxes:
                conf = float(box.conf)  # Score de confiance
                if conf > best_confidence:
                    best_confidence = conf
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordonnées de la boîte englobante
                    x1 *= self.param.width/new_width
                    x2 *= self.param.width/new_width
                    y1 *= self.param.height/ new_height
                    y2 *= self.param.height/new_height
                    self.best_ball = [[(x1+x2)/2, (y1+y2)/2]]

        return self.best_ball.copy()


    def difference_method(self):
        '''Traite une paire de frames pour détecter les balles''' 
        self.frame_difference()
        self.open_if_openable(5, (3, 3), (23, 23))
        contours, _ = cv2.findContours(self.processed_frame_difference, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      
        all_ball = self.find_circles(contours)
        return all_ball

    def background_method(self):
        '''Traite une paire de frames pour détecter les balles''' 
        self.background_difference()
        self.open_if_openable(1, (5, 5), (23, 23))
        contours, _ = cv2.findContours(self.processed_frame_difference, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      
        all_ball = self.find_circles(contours)
        return all_ball
        
    def update_next_frame(self, frame):
        self.update_prev_frame(self.next_frame.copy())
        self.next_frame = np.copy(frame)
    
    def update_prev_frame(self, frame):
        self.prev_frame = np.copy(frame)

    def frame_difference(self):
        '''actualise la différence de frame'''
        frame_diff = cv2.absdiff(self.prev_frame, self.next_frame)
        gray_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        self.unprocessed_frame_difference = thresh
    
    def background_difference(self):
        fgmask = self.fgbg.apply(self.next_frame)
        self.unprocessed_frame_difference = fgmask

    def open(self, ero, dila):
        def get_pos(name):
            return self.param.get_point(name).pos_int()
        # Extraire la région d'intérêt (ROI)
        roi = self.unprocessed_frame_difference[0:min(self.param.height, get_pos("net")[1]), max(0, get_pos("ant_tl")[0]-50):min(self.param.width, get_pos("ant_tr")[0]+50)]

        # Appliquer l'ouverture morphologique uniquement sur la ROI
        roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ero))
        roi = cv2.dilate(roi, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, dila))

        # Remplacer la ROI dans l'image originale
        self.processed_frame_difference = np.zeros_like(self.unprocessed_frame_difference)
        self.processed_frame_difference[0:min(self.param.height, get_pos("net")[1]), max(0, get_pos("ant_tl")[0]-50):min(self.param.width, get_pos("ant_tr")[0]+50)] = roi

    def open2(self):
        #frame = cv2.dilate(frame, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))
        frame = cv2.morphologyEx(self.unprocessed_frame_difference, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        frame = cv2.dilate(frame, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))
        self.processed_frame_difference = frame

    def open_if_openable(self, white_thresh, ero, dila):
        def get_pos(name):
            return self.param.get_point(name).pos_int()

        # Définir les coordonnées de la ROI
        y1, y2 = 0, min(self.param.height, get_pos("net")[1])
        x1, x2 = max(0, get_pos("ant_tl")[0] - 50), min(self.param.width, get_pos("ant_tr")[0] + 50)

        # Extraire la ROI à partir de l'image non traitée
        roi = self.unprocessed_frame_difference[y1:y2, x1:x2]

        # Calculer le pourcentage de pixels blancs uniquement dans la ROI
        total_pixels = roi.size
        white_pixels = cv2.countNonZero(roi)
        white_percentage = (white_pixels / total_pixels) * 100
        if white_percentage < white_thresh:
            self.open(ero, dila)
        else:
            self.processed_frame_difference = np.zeros_like(self.unprocessed_frame_difference)
    
    def find_circles(self, contours):
        '''Trouve les cercles dans les contours'''
        l = []
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            l.append([x, y, radius])

            # Vérification si le cercle est dans la région d'intérêt
            # if (y < self.param.get_point_y("net") - 
            #     (self.param.get_point_y("net") - self.param.get_point_y("ant_tl")) / 5 and 
            #     self.param.get_point_x("ant_tl") < x < self.param.get_point_x("ant_tr")):
        return l



if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])