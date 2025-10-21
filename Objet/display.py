import cv2
import parameters
import numpy as np
from trajectory import Trajectory
import subprocess
import time

class Display():
    def __init__(self, parameters):
        self.param = parameters
    
    def load_frame(self, frame):
        self.unprocessed_frame = np.copy(frame)
        self.frame = np.copy(frame)
    
    def load_time(self, time_video, start_time):
        self.time_video = time_video
        self.start_time = start_time
    
    def load_traj(self, traj):
        self.traj = traj
    
    def draw_traj(self):
        '''for i in range(len(self.traj.points)):
            cv2.circle(self.frame, self.traj.points[i].pos_int(), 5, (255, 255, 255), 3)

        if self.traj.is_up:
            for i in range(self.traj.start_traj, len(self.traj.points)):
                cv2.circle(self.frame, self.traj.points[i].pos_int(), 3, (0, 0, 0), 3)
        '''
        #cv2.circle(self.frame, self.traj.highest_point().pos_int(), 3, (0, 0, 0), 3)
        if len(self.traj.parabola) >= 3 :
            for i in range(len(self.traj.parabola)-1):
                #cv2.circle(self.frame, self.traj.parabola[i].pos_int(), 3, (0, 0, 0), 3)
                cv2.line(self.frame, self.traj.parabola[i].pos_int(), self.traj.parabola[i+1].pos_int(), self.traj.color, 2, lineType=cv2.LINE_AA)

    def unprocessed_frame_copy(self):
        return self.unprocessed_frame.copy()
    
    def draw_all_points(self, brightness = 1):
        background = self.frame.copy()
        for point in self.param.interesting_points:
            if point.name != "curs" and point.name != "bar_point_left" and point.name != "bar_point_right":
                self.draw_point(point)
        self.frame = cv2.addWeighted(background, 1 - brightness, self.frame, brightness, 0)

        
    
    def draw_point(self, point):
        cv2.circle(self.frame, point.pos_int(), 3, point.color, 3, lineType=cv2.LINE_AA)

    def draw_shape(self, brightness = 1, param_list = ["net", "ant", "wind", "height", "bar"]):
        def get_point(name):
            return self.param.get_point(name)
        
        background = self.frame.copy()
        for shape in param_list:
            if shape == "net":
                self.draw_line(get_point("ant_bl"), get_point("ant_br"), (255, 255, 0))
            elif shape == "ant":
                self.draw_line(get_point("ant_bl"), get_point("ant_tl"), (0, 0, 255))
                self.draw_line(get_point("ant_br"), get_point("ant_tr"), (0, 0, 255))
            elif shape == "wind":
                self.draw_rectangle(get_point("wind_l_tl"), get_point("wind_l_tr"), get_point("wind_l_br"), get_point("wind_l_bl"), (0, 255, 0))
                self.draw_rectangle(get_point("wind_r_tl"), get_point("wind_r_tr"), get_point("wind_r_br"), get_point("wind_r_bl"), (0, 255, 0))
            elif shape == "height":
                self.draw_line_x(get_point("set_height"), (255, 255, 255))
                self.draw_line_x(get_point("set_margin_over"), (200, 200, 200))
                self.draw_line_x(get_point("set_margin_under"), (200, 200, 200))
            elif shape == "bar":
                self.draw_line(get_point("bar_point_left"), get_point("bar_point"), (0, 0, 0), 5)
                self.draw_line(get_point("bar_point_right"), get_point("bar_point"), (100, 100, 100), 5)

        self.frame = cv2.addWeighted(background, 1 - brightness, self.frame, brightness, 0)

        '''cv2.line(display.frame, (0, int(info[5])), (s_w, int(info[5])), (255, 255, 255), 2)
        cv2.putText(display.frame, "Hauteur de mire : " + str(round(hau_mire, 1)),(0, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, "Precision : " + str(is_precise), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, "Parfait : " + str(stat[0]), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, "Mid : " + str(stat[1]), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, "Mid : " + str(stat[2]), (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, "Nul : " + str(stat[3]), (0, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(display.frame, str(round(hau_mire, 1)), (0, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.rectangle(display.frame, (int(info[3][0][0]), int(info[3][0][1])), (int(info[3][1][0]), int(info[3][1][1])), (0, 255, 0), 2)
        cv2.rectangle(display.frame, (int(info[4][0][0]), int(info[4][0][1])), (int(info[4][1][0]), int(info[4][1][1])), (0, 255, 0), 2)'''

    
    def draw_line(self, point1, point2, color, thickness = 2):
        cv2.line(self.frame, point1.pos_int(), point2.pos_int(), color, thickness, lineType=cv2.LINE_AA)
    
    def draw_line_x(self, point, color):
        cv2.line(self.frame, (0, point.pos_int()[1]), (self.param.width, point.pos_int()[1]), color, 2, lineType=cv2.LINE_AA)
    
    def draw_rectangle(self, point1, point2, point3, point4, color):
        self.draw_line(point1, point2, color)
        self.draw_line(point2, point3, color)
        self.draw_line(point3, point4, color)
        self.draw_line(point4, point1, color)
    
    def draw_balls(self, list_ball):
        for ball in list_ball:
            cv2.circle(self.frame, (int(ball[0]), int(ball[1])), int(ball[2]), (0, 0, 255), 2, lineType=cv2.LINE_AA)
    
    def draw_point_traj(self):
        for i in range(len(self.traj.points)):
            if i < self.traj.start_traj or not self.traj.is_up:
                cv2.circle(self.frame, self.traj.points[i].pos_int(), 3, (0, 0, 255), 3, lineType=cv2.LINE_AA)
            else :
                cv2.circle(self.frame, self.traj.points[i].pos_int(), 3, (255, 255, 255), 3, lineType=cv2.LINE_AA)
    
    def display(self, brightness, list_ball, current_frame = None):
        self.draw_shape(brightness)
        self.draw_all_points(brightness)     
        self.draw_traj()  
        self.draw_balls(list_ball)
        self.draw_point_traj()
        #cv2.putText(self.frame, str(len(self.traj.points)) +" "+ str(self.traj.start_traj) + " " + str(self.traj.no_ball_frame), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(self.frame, str(len(self.traj.points_before)), (10, self.param.height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('main', self.frame)
    
    
if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])