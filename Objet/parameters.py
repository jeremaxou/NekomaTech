import screeninfo
from point import Point, Point_param
import cv2
import numpy as np
import subprocess


class Parameters:
    def __init__(self):
        cv2.namedWindow('main', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('main', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # Obtenir la taille de l'écran
        screen = screeninfo.get_monitors()[0]
        self.width = screen.width
        self.height = screen.height
        self.mode = "full"
        
        # Liste des points intéressants
        self.interesting_points = [
            Point_param("ant_tl", self.width / 5, 2 * self.height / 5, (0, 0, 255)),  
            Point_param("wind_l_tl", self.width * 3 / 10, 2 * self.height / 5, (0, 255, 0)), 
            Point_param("wind_l_br", self.width * 4 / 10, self.height * 12 / 25, (0, 255, 0)), 
            Point_param("wind_r_tl", self.width * 6 / 10, 2 * self.height / 5, (0, 255, 0)), 
            Point_param("wind_r_br", self.width * 7 / 10, self.height * 12 / 25, (0, 255, 0)), 
            Point_param("set_height", self.width/2, self.height / 4,(255, 255, 255)), 
            Point_param("set_margin_over", self.width/2, self.height * 3 / 16, (200, 200, 200)),
            Point_param("set_margin_under", self.width/2, self.height * 5 / 16, (200, 200, 200))
        ]

        self.interesting_points.append(Point_param("ant_tr", 4 * self.width / 5, self.get_point("ant_tl").y, (0, 0, 255)))
        self.interesting_points.append(Point_param("net", self.get_center_x("ant_tl", "ant_tr"), self.height/2, (255, 255, 0)))
        self.interesting_points.append(Point_param("ant_bl", self.get_point("ant_tl").x, self.get_point("net").y, (0, 0, 255)))
        self.interesting_points.append(Point_param("ant_br", self.get_point("ant_tr").x, self.get_point("net").y, (0, 0, 255)))
        self.interesting_points.append(Point_param("wind_l_bl", self.get_point("wind_l_tl").x, self.get_point("wind_l_br").y, (0, 255, 0)))
        self.interesting_points.append(Point_param("wind_l_tr", self.get_point("wind_l_br").x, self.get_point("wind_l_tl").y, (0, 255, 0)))
        self.interesting_points.append(Point_param("wind_r_bl", self.get_point("wind_r_tl").x, self.get_point("wind_r_br").y, (0, 255, 0)))
        self.interesting_points.append(Point_param("wind_r_tr", self.get_point("wind_r_br").x, self.get_point("wind_r_tl").y, (0, 255, 0)))
        self.interesting_points.append(Point_param("wind_l_m", self.get_center_x("wind_l_tl", "wind_l_br"), self.get_center_y("wind_l_tl", "wind_l_br"), (0, 255, 0)))
        self.interesting_points.append(Point_param("wind_r_m", self.get_center_x("wind_r_tl", "wind_r_br"), self.get_center_y("wind_r_tl", "wind_r_br"), (0, 255, 0)))

        self.ant_height = self.get_point("net").y - self.get_point("ant_tl").y

    def change_window_mode(self):
        if self.mode == "full":
            cv2.setWindowProperty('main', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            self.mode = "normal"
        else:
            cv2.setWindowProperty('main', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            self.mode = "full"

    def get_point(self, name):
        for point in self.interesting_points:
            if point.name == name:
                return point

    def get_point_pos(self, name):
        return self.get_point(name).pos()
    
    def get_point_x(self, name):
        return self.get_point(name).x
    
    def get_point_y(self, name):
        return self.get_point(name).y
    
    def get_center_x(self, name1, name2):
        return (self.get_point(name1).x + self.get_point(name2).x)/2
    
    def get_center_y(self, name1, name2):
        return (self.get_point(name1).y + self.get_point(name2).y)/2
    
    def get_center(self, name1, name2):
        return [self.get_center_x(name1, name2), self.get_center_y(name1, name2)]
    
    def distance(self, name1, name2):
        return np.sqrt((self.get_point_x(name1) - self.get_point_x(name2)) ** 2 +
                        (self.get_point_y(name1) - self.get_point_y(name2)) ** 2)
    

if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])
