from point import Point
import numpy as np
import subprocess
import warnings

class Trajectory:
    def __init__(self, param, previous_points = []):
        self.param = param
        self.points_before = previous_points
        self.points = []
        self.parabola = []
        self.ball_found = False
        self.is_up = False
        self.is_down = False
        self.is_over = False
        self.original_direction = "Vertical"
        self.keep_points = False
        self.is_precise = False
        self.is_high = False
        self.no_ball_frame = 0
        self.all_ball = []
        self.is_set = False
        self.start_traj = 0
        self.highest = 0
        self.flag_side = False
        self.poly = [0, 0, 0]

        self.find_ball()

    
    def update(self, all_ball, current_frame):
        self.all_ball = all_ball
        self.current_frame = current_frame
        if not self.ball_found:
            self.update_not_found()
            #self.update_not_found_easy()
        else:
            self.update_found()
    
    def update_found(self):
        next_point = self.highest_point()
        self.update_next_point(next_point)
        self.update_all()
    
    def update_all(self):    
        self.update_state()
        if self.is_over:
            return
        if self.is_up:
            self.update_poly()
            self.update_info()
            self.update_color()

    
    def update_state(self):
        self.update_is_up()
        self.update_is_down()
        self.update_is_over()
        
    
    def update_is_up(self):
        if not self.is_up and self.points[-3].y > self.points[-2].y and self.points[-2].y > self.points[-1].y and (self.is_left() or self.is_right()):
            self.is_up = True
            if abs(self.points[-3].x - self.points[-1].x) < 5:
                self.original_direction = "Vertical"
            elif self.is_left():
                self.original_direction = "Left"
            else:
                self.original_direction = "Right"
            self.start_traj = len(self.points) - 2
    
    def update_is_down(self):
        if self.is_up and self.points[-3].y < self.points[-2].y and self.points[-2].y < self.points[-1].y:
            self.is_down = True
        
    def update_is_over(self):
        if self.is_down and self.points[-3].y > self.points[-2].y and self.points[-2].y > self.points[-1].y:
            self.is_over = True
            self.keep_points = True
            self.last_3_points = [self.points[-3], self.points[-2], self.points[-1]]
            self.points.remove(self.points[-1])
            self.points.remove(self.points[-1])
            return

        if ((self.original_direction == "Left" and self.is_right()) or (self.original_direction == "Right" and self.is_left())):#and self.horizontal_flag:
            self.is_over = True
            self.keep_points = True
            self.last_3_points = [self.points[-3], self.points[-2], self.points[-1]]
            self.points.remove(self.points[-1])
            self.points.remove(self.points[-1])
            return

        if self.no_ball_frame > 1:
            self.is_over = True
            self.last_3_points = []
            return

        '''if self.poly[0] < 0 and len(self.points) > 5:
            self.is_over = True
            return'''

        #if (self.is_up and self.no_ball_frame > 10) or (not self.is_up and self.no_ball_frame > 1):
        
                
        '''if self.is_up and ((self.was_left and self.points[-1].x > self.points[-2].x + 10) or (not self.was_left and self.points[-1].x < self.points[-2].x - 10)):
            self.is_over = True
            self.points.remove(self.points[-1])
            return'''
        
        '''if self.is_up and len(self.points) > 5 and self.poly[0] < 0:
            self.is_over = True
            print("parabola")'''
    

    def is_left(self):
        return self.points[-3].x > self.points[-2].x and self.points[-2].x > self.points[-1].x

    def is_right(self):
        return self.points[-3].x < self.points[-2].x and self.points[-2].x < self.points[-1].x
        
    def update_next_point(self, next_point):
        if self.is_point_not_valid(next_point, 100):
            self.no_ball_frame += 1
        else:
            self.no_ball_frame = 0
            if not self.flag_side and ((self.original_direction == "Left" and next_point.x > self.points[-1].x) or (self.original_direction == "Right" and next_point.x < self.points[-1].x)):
                self.suspicious_point = next_point
                self.flag_side = True
                return
            if self.flag_side :
                if (self.original_direction == "Left" and next_point.x < self.suspicious_point.x) or (self.original_direction == "Right" and next_point.x > self.suspicious_point.x):
                    self.points.append(self.suspicious_point)
                    self.flag_side = False
                else:
                    self.is_over = True
                    self.last_3_points = [next_point, self.suspicious_point, self.points[-1]]
                    return
            self.points.append(next_point)
            
    
    def update_poly(self):
        x = np.array([self.points[i].x for i in range(self.start_traj, len(self.points))])
        y = np.array([self.points[i].y for i in range(self.start_traj, len(self.points))])
        self.x_mean = np.mean(x)
        x_scaled = x - self.x_mean
        if len(x) < 3:
            self.poly = [0] + list(np.polyfit(x_scaled, y, 1, rcond=1e-5))
        else:
            self.poly = np.polyfit(x_scaled, y, 2, rcond=1e-5)

        self.parabola = []
        liste = np.linspace(self.points[self.start_traj].x, self.points[-1].x, int(abs(self.points[-1].x - self.points[self.start_traj].x))+1)
        liste = liste.tolist()
        '''dx = 1
        while self.original_direction == "Right" and self.eva_poly(liste[0] - (dx+1)) < self.param.get_point_y("net") - 20 and self.poly[0] > 0:
            liste.insert(0, liste[0] - dx)
            dx += 1
        dx = 1
        while self.original_direction == "Left" and self.eva_poly(liste[0] + (dx+1)) < self.param.get_point_y("net") - 20 and self.poly[0] > 0:
            liste.insert(0, liste[0] + dx)
            dx += 1'''
        for i in range(len(liste)):
            self.parabola.append(Point(liste[i], self.eva_poly(liste[i])))
        
    def get_3_last_points(self):
        res = []
        for i in range(len(self.last_3_points)):
            res.append((self.last_3_points[i], i))
        return res

    def update_info(self):
        '''if not self.horizontal_flag:
            if self.is_left():
                self.was_left = self.is_left()
                self.horizontal_flag = True
            if self.is_right():
                self.was_left = not self.is_right()
                self.horizontal_flag = True'''

        x_box_1 = np.linspace(self.param.get_point_x("wind_l_tl"), self.param.get_point_x("wind_l_br"), 100)
        x_box_2 = np.linspace(self.param.get_point_x("wind_r_tl"), self.param.get_point_x("wind_r_br"), 100)
        x_box = np.concatenate((x_box_1, x_box_2))
        y_box = self.eva_poly(x_box)

        flag = False
        for y in y_box:
            if self.param.get_point_y("wind_l_tl") <= y <= self.param.get_point_y("wind_l_br") or self.param.get_point_y("wind_r_tl") <= y <= self.param.get_point_y("wind_r_br"):
                flag = True
                break
        self.is_precise = flag

        self.highest = self.poly[2] - (self.poly[1]**2)/(4*self.poly[0]+0.000001) 
        self.set_height = (self.param.get_point_y("net") - self.highest)/self.param.ant_height
        if self.param.get_point_y("set_margin_over") < self.highest < self.param.get_point_y("set_margin_under"):
            self.is_high = True
        else: 
            self.is_high = False

    def highest_point(self):
        mini_pt = [0, 0]
        mini = 10000
        for point in self.all_ball:
            if point[1] < mini:
                mini = point[1]
                mini_pt = point
        return Point(mini_pt[0], mini_pt[1])

    def is_point_not_valid(self, point, limit):
        return len(self.all_ball) == 0 or self.distance(point, self.points[-1]) > limit

    def update_not_found(self):
        if self.no_ball_frame > 1:
            self.is_over = True
            self.last_3_points = []
            return
        if len(self.all_ball) == 0:
            self.no_ball_frame += 1
            return
        self.no_ball_frame = 0
        for point in self.all_ball:
            self.points_before.append([Point(point[0], point[1]), self.current_frame])
        self.find_ball()
    
    def update_not_found_easy(self):
        for point in self.all_ball:
            self.points_before.append([Point(point[0], point[1]), self.current_frame])
            if len(self.points_before) >= 3:
                self.ball_found = True
                self.points = self.points_before
                self.update_all()
                return
            
    def angle_3pts(self, A, B, C):
        """
        Calcule l'angle (en degrés) formé par trois objets points A, B, C
        où chaque point a des attributs .x et .y
        et B est le sommet (le point central).
        """
        # Convertir en vecteurs numpy
        AB = np.array([A.x - B.x, A.y - B.y])
        CB = np.array([C.x - B.x, C.y - B.y])

        # Produit scalaire et normes
        dot = np.dot(AB, CB)
        norm = np.linalg.norm(AB) * np.linalg.norm(CB)
        if norm == 0:
            return None  # si deux points sont identiques

        # Calcul de l'angle
        cos_angle = np.clip(dot / norm, -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        return angle

    def find_ball(self):
        if len(self.points_before) < 3:
            return
        for po1 in self.points_before:
            for po2 in self.points_before:
                for po3 in self.points_before:
                    p1, p2, p3, t1, t2, t3 = po1[0], po2[0], po3[0], po1[1], po2[1], po3[1]
                    if self.is_different(p1, p2) and self.is_different(p2, p3) and self.is_different(p1, p3) and self.distance(p1, p2) + self.distance(p2, p3) < 200 and t1 < t2 < t3 and ((p1.y < p2.y < p3.y) or (p1.y > p2.y > p3.y)) and (self.angle_3pts(p1, p2, p3) < 20 or abs(180 - self.angle_3pts(p1, p2, p3)) < 20):
                        self.ball_found = True
                        self.points = [p1, p2, p3]
                        self.update_all()
                        return
    
    def is_different(self, p1, p2):
        return p1.is_different(p2)
    
    def distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def eva_poly(self, x):
        '''retourne le polynôme évalué en un point'''
        return self.poly[0]*((x-self.x_mean)**2)+self.poly[1]*(x-self.x_mean)+self.poly[2]
    
    def update_color(self):
        if self.is_precise and self.is_high:
            self.color = (0, 255, 0)
        elif not self.is_precise and self.is_high:
            self.color = (255, 0, 0)
        elif self.is_precise and not self.is_high:
            self.color = (255, 255, 255)
        else :
            self.color = (0, 0, 255)

if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])