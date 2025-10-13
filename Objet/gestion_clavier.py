import subprocess

def update(key, vid_mana, session, ui, param, prev_mode, mode):
    if key == ord('q'):
        return "over", "over"
    if key == ord('s'):
        session.save()
    if key == ord('p'):
        if mode == "video" or mode == "pause":
            vid_mana.pause()
            prev_mode = mode
            mode = "parameters"
        elif mode == "parameters":
            vid_mana.resume()
            mode = prev_mode
    if key == 32:
        if mode == "video":
            vid_mana.pause()
            prev_mode = mode
            mode = "pause"
        elif mode == "pause" or mode == "parameters":
            vid_mana.resume()
            mode = prev_mode
    
    if key == 13:
        ui.change_setting_mode()
    
    if key == 27:
        param.change_window_mode()
    
    if key == ord('n'):
        vid_mana.next_camera()

    if key == ord('b'):
        vid_mana.prev_camera()      

    return prev_mode, mode


if __name__ == "__main__":
    subprocess.run(["python", "Objet/Main.py"])