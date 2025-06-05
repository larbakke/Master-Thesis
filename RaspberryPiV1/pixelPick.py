import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import picamera
import time

pixelNames = [
        'n48',
        'n25',
        'p0',
        'p25',
        'p48',
        'l_top_c',
        'l_top_l',
        'l_top_r',
        'l_centr',
        'l_low_l',
        'l_low_r',
        'l_low_c',
        'l_dot',
        'r_top_c',
        'r_top_l',
        'r_top_r',
        'r_centr',
        'r_low_l',
        'r_low_r',
        'r_low_c',
        'r_dot'
              ]

click_done = False
current_coords = (0,0)
current_index = 0

def mouse_callback(event, x, y, flags, param):
    global click_done, current_coords
    if event == cv2.EVENT_LBUTTONDOWN:
        current_coords = (x,y)
        click_done = True
        
def main():
    global click_done, current_coords, current_index
    
    camera = picamera.PiCamera(resolution=(640,480), sensor_mode=4)
    camera.iso = 400
    time.sleep(1)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.awb_gains = camera.awb_gains
    
    
    

    rawCapture = PiRGBArray(camera, size=(int(640),int(480)))
    
    time.sleep(0.1)
    
    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", mouse_callback)
    
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        
        frame = frame.array
        rawCapture.truncate(0)
        
        if current_index >= len(pixelNames):
            print("complete")
            break
        
        name = pixelNames[current_index]
        
        frame = cv2.putText(frame, name, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 1)
        mouse_x, mouse_y = current_coords
        frame = cv2.putText(frame, f"mouse: {mouse_x}, {mouse_y}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 1)
        
        
        
        cv2.imshow('Frame', frame)

        key = cv2.waitKey(1) & 0xFF
        
        
        if key == ord('q'):
            break

        if click_done:
            x, y = current_coords
            print(f"'{name}' : Pixel({x}, {y}, '{name}'),")
            current_index +=1
            click_done=False
            
    camera.close()
    cv2.destroyAllWindows()
    
main()

