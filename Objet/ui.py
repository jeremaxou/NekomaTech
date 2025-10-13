import cv2
from parameters import Parameters
from point import Point_param
import copy
import subprocess
import time

class UI:
    def __init__(self, parameters, display, vid_mana):
        self.vid_mana = vid_mana
        self.display = display
        self.param = parameters
        self.curs = Point_param("curs", 0, 0, (0, 0, 0))
        self.param.interesting_points.append(self.curs)
        self.point_defaut = Point_param("defaut", -1000, 0, (0, 0, 0))
        self.point_sel = Point_param("sel", -1000, 0, (0, 0, 0))
        self.param.interesting_points.append(self.point_sel)
        self.dragging = False
        self.point_near = False

        self.bar_left = parameters.width*1/4
        self.bar_right = parameters.width*3/4
        self.bar_top = parameters.height*14/16
        self.bar_bottom = parameters.height*15/16
        self.bar_point_left = Point_param("bar_point_left", self.bar_left, (self.bar_bottom + self.bar_top)/2, (0, 0, 0))
        self.param.interesting_points.append(self.bar_point_left)
        self.bar_point_right = Point_param("bar_point_right", self.bar_right, (self.bar_bottom + self.bar_top)/2, (0, 0, 0))
        self.param.interesting_points.append(self.bar_point_right)
        self.bar_point = Point_param("bar_point", self.bar_left + vid_mana.current_frame * (self.bar_right - self.bar_left) / vid_mana.total_frames, (self.bar_bottom + self.bar_top)/2, (0, 0, 0))
        self.param.interesting_points.append(self.bar_point)
        self.touch_bar = False
        self.last_mouse_move = time.time()
        self.flag_mouse_moving = False
        self.flag_mouse_freeze = False
        self.phase = 'imm'
        self.brightness = 0
        self.time_phase = 0

        self.point_pp = copy.copy(self.point_defaut)

        self.setting_locked = False

        
    def update_bar(self):
        if not self.touch_bar:
            self.bar_point.x = self.bar_left + self.vid_mana.current_frame * (self.bar_right - self.bar_left) / self.vid_mana.total_frames
        
    def move_parameters(self):
        cv2.setMouseCallback('main', self.mouse_event)
        self.update_phase()
        self.update_bar()
        if self.setting_locked:
            self.update_linked()
        if self.dragging and self.point_near:
            self.actu_para()
        else :
            self.ppp()  
            self.touch_bar = False
        self.point_sel.x = self.point_pp.x
        self.point_sel.y = self.point_pp.y 

    def is_mouse_moving(self):
        return time.time() - self.last_mouse_move < 0.6 or self.point_near

    def update_phase(self):
        if self.phase == 'imm':
            if time.time() - self.last_mouse_move <= 0.1:
                self.phase = 'up'
                self.time_phase = time.time()
            self.brightness = 0
        elif self.phase == 'up':
            if time.time() - self.time_phase <= 0.2:
                self.brightness = (time.time() - self.time_phase)*5
            else:
                self.phase = 'mov'
                self.brightness = 1
                self.time_phase = time.time()
        elif self.phase == 'mov':
            if self.point_near:
                self.last_mouse_move = time.time()
            if time.time() - self.last_mouse_move >= 1: 
                self.phase = 'down'
                self.time_phase = time.time()
            self.brightness = 1
        elif self.phase == 'down':
            if time.time() - self.last_mouse_move <= 0.1:
                self.phase = 'mov'
                self.time_phase = time.time()
            self.brightness = 1 - (time.time() - self.time_phase)*5
            if time.time() - self.time_phase >= 0.2:
                self.phase = 'imm'
                self.brightness = 0

            
    def get_brightness(self):
        if not self.flag_mouse_moving:
            self.mouse_begin_move = self.last_mouse_move
            self.flag_mouse_moving = True
        if 0 <= time.time() - self.mouse_begin_move <= 0.2:
            return (time.time() - self.mouse_begin_move)*5
        elif time.time() - self.last_mouse_move <= 0.4:
            return 1
        elif 0.6 >= time.time() - self.last_mouse_move >= 0.4 and not self.point_near:
            return (0.6 - (time.time() - self.last_mouse_move))*5
        self.flag_mouse_moving = False
        if self.point_near:
            self.flag_mouse_moving = False
        return 1
            
        
    def set_bar(self, x): 
        self.vid_mana.current_frame = int((x - self.bar_left) * self.vid_mana.total_frames / (self.bar_right - self.bar_left))
        self.vid_mana.start_time = time.time() - self.vid_mana.current_frame / self.vid_mana.fps
        self.vid_mana.cap.set(cv2.CAP_PROP_POS_FRAMES, self.vid_mana.current_frame)

    
    def mouse_event(self, event, x, y, flags, param):
        '''met à jour les paramètres grace au mouvement de la souris'''
        self.last_mouse_move = time.time()
        self.curs.x = x
        self.curs.y = y

        if event == cv2.EVENT_LBUTTONDOWN and not self.dragging:
            self.dragging = True
        if event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            if self.touch_bar:
                self.set_bar(x)

    
    def ppp(self):
        mini = 2000
        for pt in self.param.interesting_points:
            if pt.name != self.curs.name and pt.name != self.point_sel.name and self.param.distance(pt.name, self.curs.name) < mini:
                mini = self.param.distance(pt.name, self.curs.name) 
                self.point_pp = pt
        if mini < 50:
            self.point_near = True
        else:
            self.point_near = False
            self.point_pp = copy.copy(self.point_defaut)
    
    def change_setting_mode(self):
        if not self.setting_locked:
            self.update_user_info()
        self.setting_locked = not self.setting_locked

    def update_user_info(self):
        def get_point(name):
            return self.param.get_point(name)
        self.set_height = (get_point("net").y - get_point("set_height").y) / (get_point("net").y - get_point("ant_tl").y)
        self.set_margin_over = (get_point("net").y - get_point("set_margin_over").y) / (get_point("net").y - get_point("ant_tl").y)
        self.set_margin_under = (get_point("net").y - get_point("set_margin_under").y) / (get_point("net").y - get_point("ant_tl").y)
        self.wind_l_l = (get_point("wind_l_tl").x - get_point("ant_tl").x) / (get_point("ant_tr").x - get_point("ant_tl").x)
        self.wind_l_r = (get_point("wind_l_tr").x - get_point("ant_tl").x) / (get_point("ant_tr").x - get_point("ant_tl").x)
        self.wind_l_t = (get_point("net").y - get_point("wind_l_tl").y) / (get_point("net").y - get_point("ant_tl").y)
        self.wind_l_b = (get_point("net").y - get_point("wind_l_bl").y) / (get_point("net").y - get_point("ant_tl").y)
        self.wind_r_l = (get_point("ant_tr").x - get_point("wind_r_tl").x) / (get_point("ant_tr").x - get_point("ant_tl").x)
        self.wind_r_r = (get_point("ant_tr").x - get_point("wind_r_tr").x) / (get_point("ant_tr").x - get_point("ant_tl").x)
        self.wind_r_t = (get_point("net").y - get_point("wind_r_tr").y) / (get_point("net").y - get_point("ant_tr").y)
        self.wind_r_b = (get_point("net").y - get_point("wind_r_br").y) / (get_point("net").y - get_point("ant_tr").y)

    def actu_para(self):
        def get_point(name):
            return self.param.get_point(name)
        def update_x():
            point.x = self.curs.x
        def update_y():
            point.y = self.curs.y
        def update():
            update_x()
            update_y()
        def update_ref_x(name):
            get_point(name).x += self.curs.x - point.x
        def update_ref_x_list(name):
            for name in name:
                update_ref_x(name)      
        def update_ref_y(name):
            get_point(name).y += self.curs.y - point.y
        def update_ref_y_list(name):
            for name in name:
                update_ref_y(name)  
        def update_ref(name):
            update_ref_x(name)
            update_ref_y(name)
        def update_ref_list(name):
            for name in name:
                update_ref(name)
        def is_left(name1, name2, margin):
            return get_point(name1).x < get_point(name2).x + 50
        def is_right(name1, name2, margin):
            return get_point(name1).x > get_point(name2).x - 50 
        def is_over(name1, name2, margin):
            return get_point(name1).y < get_point(name2).y + 50
        def is_under(name1, name2, margin):
            return get_point(name1).y > get_point(name2).y - 50
        def put_left(name1, name2):
            get_point(name1).x = get_point(name2).x - 50
        def put_right(name1, name2):
            get_point(name1).x = get_point(name2).x + 50
        def put_over(name1, name2):
            get_point(name1).y = get_point(name2).y - 50
        def put_under(name1, name2):
            get_point(name1).y = get_point(name2).y + 50
        def update_center_x(name1, name2, name3):
            get_point(name1).x = self.param.get_center_x(name2, name3)
        def update_center_y(name1, name2, name3):
            get_point(name1).y = self.param.get_center_y(name2, name3)
        def update_center(name1, name2, name3):
            update_center_x(name1, name2, name3)
            update_center_y(name1, name2, name3)
        def valid_to_left(name):
            if is_left("curs", name):
                put_right("curs", name)
        def valid_to_right(name):
            if is_right("curs", name):
                put_left("curs", name)
        def valid_to_up(name):
            if is_over("curs", name):
                put_under("curs", name)
        def valid_to_down(name):
            if is_under("curs", name):
                put_over("curs", name)


        point = self.point_pp
        name = point.name
        if not self.setting_locked:
            if name == "net":          
                update_ref("ant_tl")
                update_ref("ant_bl")
                update_ref("ant_tr")
                update_ref("ant_br")
                update()

            if name == "ant_bl":
                valid_to_right("ant_br")
                update_ref_x("ant_tl")
                update_x()
                update_center("net", "ant_bl", "ant_br")
            
            if name == "ant_br":
                valid_to_left("ant_bl")
                update_ref_x("ant_tr")
                update_x()
                update_center("net", "ant_bl", "ant_br")
            
            if name == "ant_tl":
                valid_to_down("ant_bl")
                valid_to_right("ant_tr")
                update_ref_x("ant_bl")
                update_ref_y("ant_tr")
                update()
                update_center_x("net", "ant_bl", "ant_br")
                
            if name == "ant_tr":
                valid_to_down("ant_br")
                valid_to_left("ant_tl")
                update_ref_x("ant_br")
                update_ref_y("ant_tl")
                update()
                update_center_x("net", "ant_bl", "ant_br")
                
            
            if name == "wind_l_tl":
                valid_to_right("wind_l_tr")
                valid_to_down("wind_l_bl")
                update_ref_y("wind_l_tr")
                update_ref_x("wind_l_bl")
                update()
                update_center("wind_l_m", "wind_l_tl", "wind_l_br")
                
            if name == "wind_l_tr":
                valid_to_left("wind_l_tl")
                valid_to_down("wind_l_br")
                update_ref_y("wind_l_tl")
                update_ref_x("wind_l_br")
                update()
                update_center("wind_l_m", "wind_l_tl", "wind_l_br")
                
            if name == "wind_l_br":
                valid_to_left("wind_l_bl")
                valid_to_up("wind_l_tr")
                update_ref_y("wind_l_bl")
                update_ref_x("wind_l_tr")
                update()
                update_center("wind_l_m", "wind_l_tl", "wind_l_br")
                
            if name == "wind_l_bl":
                valid_to_right("wind_l_br")
                valid_to_up("wind_l_tl")
                update_ref_y("wind_l_br")
                update_ref_x("wind_l_tl")
                update()
                update_center("wind_l_m", "wind_l_tl", "wind_l_br")
                
            if name == "wind_l_m":
                update_ref("wind_l_tl")
                update_ref("wind_l_tr")
                update_ref("wind_l_br")
                update_ref("wind_l_bl")
                update()
            if name == "wind_r_tl":
                valid_to_right("wind_r_tr")
                valid_to_down("wind_r_bl")
                update_ref_y("wind_r_tr")
                update_ref_x("wind_r_bl")
                update()
                update_center("wind_r_m", "wind_r_tl", "wind_r_br")
            if name == "wind_r_tr":
                valid_to_left("wind_r_tl")
                valid_to_down("wind_r_br")
                update_ref_y("wind_r_tl")
                update_ref_x("wind_r_br")
                update()
                update_center("wind_r_m", "wind_r_tl", "wind_r_br")
            if name == "wind_r_br":
                valid_to_left("wind_r_bl")
                valid_to_up("wind_r_tr")
                update_ref_y("wind_r_bl")
                update_ref_x("wind_r_tr")
                update()
                update_center("wind_r_m", "wind_r_tl", "wind_r_br")
            if name == "wind_r_bl":
                valid_to_right("wind_r_br")
                valid_to_up("wind_r_tl")
                update_ref_y("wind_r_br")
                update_ref_x("wind_r_tl")
                update()
                update_center("wind_r_m", "wind_r_tl", "wind_r_br")
            if name == "wind_r_m":
                update_ref("wind_r_tl")
                update_ref("wind_r_tr")
                update_ref("wind_r_br")
                update_ref("wind_r_bl")
                update()
            

            if name == "set_height":
                update_ref_y("set_margin_over")
                update_ref_y("set_margin_under")
                update_y()
            if name == "set_margin_over":
                valid_to_down("set_height")
                update_y()
            if name == "set_margin_under":
                valid_to_up("set_height")
                update_y()
            
            if name == "bar_point":
                self.touch_bar = True
                valid_to_left("bar_point_left")
                valid_to_right("bar_point_right")
                update_x()
        else:
            if name == "ant_tl":
                valid_to_down("ant_bl")
                valid_to_right("ant_tr")
                update()
                get_point("ant_bl").x = get_point("ant_tl").x
                get_point("ant_tr").y = get_point("ant_tl").y
            if name == "ant_tr":
                valid_to_down("ant_br")
                valid_to_left("ant_tl")
                update()
                get_point("ant_br").x = get_point("ant_tr").x
                get_point("ant_tl").y = get_point("ant_tr").y
            if name == "ant_bl":
                valid_to_up("ant_tl")
                valid_to_right("ant_br")
                update()
                get_point("ant_tl").x = get_point("ant_bl").x
                get_point("ant_br").y = get_point("ant_bl").y
            if name == "ant_br":
                valid_to_up("ant_tr")
                valid_to_left("ant_bl")
                update()
                get_point("ant_tr").x = get_point("ant_br").x
                get_point("ant_bl").y = get_point("ant_br").y
            
    def update_linked(self):
        def get_point(name):
            return self.param.get_point(name)
        def update_center(name1, name2, name3):
            get_point(name1).x = self.param.get_center_x(name2, name3)
            get_point(name1).y = self.param.get_center_y(name2, name3)

        net = get_point("net")
        ant_height = net.y - get_point("ant_tl").y
        ant_witdh = get_point("ant_tr").x - get_point("ant_tl").x
        
        get_point("set_height").y = net.y - self.set_height * ant_height
        get_point("set_margin_over").y = net.y - self.set_margin_over * ant_height
        get_point("set_margin_under").y = net.y - self.set_margin_under * ant_height
        get_point("wind_l_tl").y = net.y - self.wind_l_t * ant_height
        get_point("wind_l_bl").y = net.y - self.wind_l_b * ant_height
        get_point("wind_l_tr").y = net.y - self.wind_l_t * ant_height
        get_point("wind_l_br").y = net.y - self.wind_l_b * ant_height
        
        get_point("wind_r_tl").y = net.y - self.wind_r_t * ant_height
        get_point("wind_r_bl").y = net.y - self.wind_r_b * ant_height
        get_point("wind_r_tr").y = net.y - self.wind_r_t * ant_height
        get_point("wind_r_br").y = net.y - self.wind_r_b * ant_height

        get_point("wind_l_tl").x = get_point("ant_tl").x + self.wind_l_l * ant_witdh
        get_point("wind_l_bl").x = get_point("ant_tl").x + self.wind_l_l * ant_witdh
        get_point("wind_l_tr").x = get_point("ant_tl").x + self.wind_l_r * ant_witdh
        get_point("wind_l_br").x = get_point("ant_tl").x + self.wind_l_r * ant_witdh
        get_point("wind_r_tl").x = get_point("ant_tr").x - self.wind_r_l * ant_witdh
        get_point("wind_r_bl").x = get_point("ant_tr").x - self.wind_r_l * ant_witdh
        get_point("wind_r_tr").x = get_point("ant_tr").x - self.wind_r_r * ant_witdh
        get_point("wind_r_br").x = get_point("ant_tr").x - self.wind_r_r * ant_witdh

        update_center("wind_l_m", "wind_l_tl", "wind_l_br")
        update_center("wind_r_m", "wind_r_tl", "wind_r_br")
        update_center("net", "ant_bl", "ant_br")


if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])