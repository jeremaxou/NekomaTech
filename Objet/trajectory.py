from point import Point
import numpy as np
import subprocess
import warnings

class Trajectory:
    def __init__(self, param):
        self.param = param
        self.points_before = []
        self.points = []
        self.parabola = []
        self.ball_found = False
        self.is_up = False
        self.is_down = False
        self.is_over = False
        self.was_left = False
        self.is_precise = False
        self.is_high = False
        self.no_ball_frame = 0
        self.all_ball = []
        self.is_set = False
        self.start_traj = 0
        self.highest = 0
        self.horizontal_flag = False

    
    def update(self, all_ball):
        self.all_ball = all_ball
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
            self.was_left = self.is_left()
            self.start_traj = len(self.points) - 2
    
    def update_is_down(self):
        if self.is_up and self.points[-3].y < self.points[-2].y and self.points[-2].y < self.points[-1].y:
            self.is_down = True
        
    def update_is_over(self):
        if self.is_down and self.points[-3].y > self.points[-2].y and self.points[-2].y > self.points[-1].y:
            self.is_over = True
            self.points.remove(self.points[-1])
            self.points.remove(self.points[-1])
            return

        if ((self.was_left and self.is_right()) or (not self.was_left and self.is_left())):#and self.horizontal_flag:
            self.is_over = True
            self.points.remove(self.points[-1])
            self.points.remove(self.points[-1])
            return

        #if (self.is_up and self.no_ball_frame > 10) or (not self.is_up and self.no_ball_frame > 1):
        if self.no_ball_frame > 1:
            self.is_over = True
            return
        
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
            self.points.append(next_point)
            
    
    def update_poly(self):
        with warnings.catch_warnings():
            from numpy.polynomial.polyutils import RankWarning
            warnings.simplefilter("ignore", RankWarning)
            self.poly = np.polyfit([self.points[i].x for i in range(self.start_traj, len(self.points))], [self.points[i].y for i in range(self.start_traj, len(self.points))], 2, rcond=1e-5)

        self.parabola = []
        liste = np.linspace(self.points[self.start_traj].x, self.points[-1].x, int(abs(self.points[-1].x - self.points[self.start_traj].x))+1)
        liste = liste.tolist()
        dx = 1
        while not self.was_left and self.eva_poly(liste[0] - (dx+1)) < self.param.get_point_y("net") - 20 and self.poly[0] > 0:
            liste.insert(0, liste[0] - dx)
            dx += 1
        dx = 1
        while self.was_left and self.eva_poly(liste[0] + (dx+1)) < self.param.get_point_y("net") - 20 and self.poly[0] > 0:
            liste.insert(0, liste[0] + dx)
            dx += 1
        for i in range(len(liste)):
            self.parabola.append(Point(liste[i], self.eva_poly(liste[i])))

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
        for point in self.all_ball:
            self.points_before.append(Point(point[0], point[1]))
        self.find_ball()
    
    def update_not_found_easy(self):
        for point in self.all_ball:
            self.points_before.append(Point(point[0], point[1]))
            if len(self.points_before) >= 3:
                self.ball_found = True
                self.points = self.points_before
                self.update_all()
                return
    
    def find_ball(self):
        for p1 in self.points_before:
            for p2 in self.points_before:
                for p3 in self.points_before:
                    if self.is_different(p1, p2) and self.is_different(p2, p3) and self.is_different(p1, p3) and self.distance(p1, p2) + self.distance(p2, p3) < 200 :
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
        return self.poly[0]*(x**2)+self.poly[1]*x+self.poly[2]
    
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