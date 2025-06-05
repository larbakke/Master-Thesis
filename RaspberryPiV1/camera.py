import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import picamera
import time
import subprocess
import os
import signal
from multiprocessing import Queue

class Camera:
    def __init__(self, pixels_dir, pixels_l, pixels_r, hsv_lower=(0,100,100), hsv_upper=(10,255,255)):
        self.hsv_lower = np.array(hsv_lower, dtype=np.uint8)
        self.hsv_upper = np.array(hsv_upper, dtype=np.uint8)
        self.pixels_dir = pixels_dir
        self.pixels_l = pixels_l
        self.pixels_r = pixels_r
        self.direction = 0
        self.distance = -1       
        
        #self.initPiCamera()
        #self.runCamera()

        
    def initCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -5)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
        self.cap.set(cv2.CAP_PROP_GAIN, 0)
        
        
    def getDirection(self):
        return self.direction
    
    def getDistance(self):
        return self.distance
    
    def initPiCamera(self):
        self.killCameraUsers()
        self.camera = picamera.PiCamera(resolution=(640,480), sensor_mode=4)
        try:
            self.camera.iso = 400
            time.sleep(1)
            self.camera.shutter_speed = self.camera.exposure_speed
            self.camera.exposure_mode = 'off'
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = self.camera.awb_gains
        except:
            print('error in camera. Stopping the program')
            self.closeCamera()
            raise Error('Camera init error')
        
    def killCameraUsers(self):
        try:
            result = subprocess.check_output(['lsof', '/dev/vchiq']).decode()
            
            lines = result.strip().split('\n')[1:]
            for line in lines:
                pid = int(line.split()[1])
                print(f"Killing process using camera: PID {pid}")
                os.kill(pid, signal.SIGTERM)
        except subprocess.CalledProcessError:
            print("N camera users found.")
        
    def checkCamera(self):
        if not self.cap.isOpened:
            print("Can not open camera")
            exit()
    
    def runCamera(self, queue):
        #self.checkCamera()
        
        #while True:
         #   ret, frame = self.cap.read()
          #  if not ret:
           #     print("Can't receive frame. Exiting...")
            #    break
        rawCapture = PiRGBArray(self.camera, size=(int(640),int(480)))
        time.sleep(0.1)
        for frame in self.camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
            frame = frame.array
            rawCapture.truncate(0)
            
            
            binary_frame = self.processFrame(frame)
            #pixel = self.pixels_l['l_top_c']
            self.distance = self.readDigit(binary_frame)
            self.direction = self.readDir(binary_frame)
            queue.put({'dist':self.distance, 'dir':self.direction})
            #print(f'Direction: {self.getDirection()}, Distance: {self.getDistance()}')
            #print(f'Direction: {self.direction}, Distance: {self.distance}')
            
            frame = self.drawAllPixels(frame)
            
            cv2.imshow('Processed feed', binary_frame)
            cv2.imshow('Camera feed', frame)

            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            
        self.closeCamera()
        
    def processFrame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        #mask = cv2.morphologyEx(mask, cv2.MOPRH_DILATE, kernel)
        
        binaryOutput = (mask > 0).astype(np.uint8)
        
        return binaryOutput*255
        
    def closeCamera(self):
        self.camera.close()
        cv2.destroyAllWindows()
        
    def drawAllPixels(self, frame):
        pixel_dicts = [self.pixels_dir, self.pixels_l, self.pixels_r]
        for pixel_dict in pixel_dicts:
            for key, pixel in pixel_dict.items():
                frame = self.drawPixel(frame, pixel)
        return frame
        
        
        
    def drawPixel(self, frame, pixel):
        frame = cv2.circle(frame, (pixel.x, pixel.y), radius=4, color=(0,255,0), thickness=-1)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (pixel.x+5, pixel.y)
        fontScale = 0.6
        color = (0, 255, 0)
        thickness=1
        
        frame = cv2.putText(frame, pixel.name, org, font, fontScale, color, thickness, cv2.LINE_AA)
        
        return frame
        
    def readDir(self, binary_frame):
        if self.pixelIsOn(binary_frame, self.pixels_dir['n48']):
            return -48
        elif self.pixelIsOn(binary_frame, self.pixels_dir['n25']):
            return -25
        elif self.pixelIsOn(binary_frame, self.pixels_dir['p0']):
            return 0
        elif self.pixelIsOn(binary_frame, self.pixels_dir['p25']):
            return 25
        elif self.pixelIsOn(binary_frame, self.pixels_dir['p48']):
            return 48
        else:
            return None
        
    def readDigit(self, binary_frame):
        l_top_c = self.pixelIsOn(binary_frame, self.pixels_l['l_top_c'])
        l_top_l = self.pixelIsOn(binary_frame, self.pixels_l['l_top_l'])
        l_top_r = self.pixelIsOn(binary_frame, self.pixels_l['l_top_r'])
        l_centr = self.pixelIsOn(binary_frame, self.pixels_l['l_centr'])
        l_low_l = self.pixelIsOn(binary_frame, self.pixels_l['l_low_l'])
        l_low_r = self.pixelIsOn(binary_frame, self.pixels_l['l_low_r'])
        l_low_c = self.pixelIsOn(binary_frame, self.pixels_l['l_low_c'])
        l_dot = self.pixelIsOn(binary_frame, self.pixels_l['l_dot'])
        
        r_top_c = self.pixelIsOn(binary_frame, self.pixels_r['r_top_c'])
        r_top_l = self.pixelIsOn(binary_frame, self.pixels_r['r_top_l'])
        r_top_r = self.pixelIsOn(binary_frame, self.pixels_r['r_top_r'])
        r_centr = self.pixelIsOn(binary_frame, self.pixels_r['r_centr'])
        r_low_l = self.pixelIsOn(binary_frame, self.pixels_r['r_low_l'])
        r_low_r = self.pixelIsOn(binary_frame, self.pixels_r['r_low_r'])
        r_low_c = self.pixelIsOn(binary_frame, self.pixels_r['r_low_c'])
        r_dot = self.pixelIsOn(binary_frame, self.pixels_r['r_dot'])
        
        left=None
        right=None
        
        if l_top_c and l_top_l and l_top_r and l_low_c and l_low_l and l_low_r and not l_centr:
            left = 0
        elif not l_top_c and not l_top_l and l_top_r and not l_low_c and not l_low_l and l_low_r and not l_centr:
            left = 1
        elif l_top_c and not l_top_l and l_top_r and l_low_c and l_low_l and not l_low_r and l_centr:
            left = 2
        elif l_top_c and not l_top_l and l_top_r and l_low_c and not l_low_l and l_low_r and l_centr:
            left = 3
        elif not l_top_c and l_top_l and l_top_r and not l_low_c and not l_low_l and l_low_r and l_centr:
            left = 4
        elif l_top_c and l_top_l and not l_top_r and l_low_c and not l_low_l and l_low_r and l_centr:
            left = 5
        elif l_top_c and l_top_l and not l_top_r and l_low_c and l_low_l and l_low_r and l_centr:
            left = 6
        elif l_top_c and not l_top_l and l_top_r and not l_low_c and not l_low_l and l_low_r and not l_centr:
            left = 7
        elif l_top_c and l_top_l and l_top_r and l_low_c and l_low_l and l_low_r and l_centr:
            left = 8
        elif l_top_c and l_top_l and l_top_r and l_low_c and not l_low_l and l_low_r and l_centr:
            left = 9
            
        if r_top_c and r_top_l and r_top_r and r_low_c and r_low_l and r_low_r and not r_centr:
            right = 0
        elif not r_top_c and not r_top_l and r_top_r and not r_low_c and not r_low_l and r_low_r and not r_centr:
            right = 1
        elif r_top_c and not r_top_l and r_top_r and r_low_c and r_low_l and not r_low_r and r_centr:
            right = 2
        elif r_top_c and not r_top_l and r_top_r and r_low_c and not r_low_l and r_low_r and r_centr:
            right = 3
        elif not r_top_c and r_top_l and r_top_r and not r_low_c and not r_low_l and r_low_r and r_centr:
            right = 4
        elif r_top_c and r_top_l and not r_top_r and r_low_c and not r_low_l and r_low_r and r_centr:
            right = 5
        elif r_top_c and r_top_l and not r_top_r and r_low_c and r_low_l and r_low_r and r_centr:
            right = 6
        elif r_top_c and not r_top_l and r_top_r and not r_low_c and not r_low_l and r_low_r and not r_centr:
            right = 7
        elif r_top_c and r_top_l and r_top_r and r_low_c and r_low_l and r_low_r and r_centr:
            right = 8
        elif r_top_c and r_top_l and r_top_r and r_low_c and not r_low_l and r_low_r and r_centr:
            right = 9
            
        #print('Left ', left, 'Right ', right)
        
        if left!=None and right!=None:
            distance = 10*left+right
            if l_dot:
                distance = distance/10
            return distance
        return None
        
    def pixelIsOn(self, binary_frame, pixel, buffer=6):
        height, width = binary_frame.shape
        
        x = pixel.x
        y = pixel.y
        
        x_start = max(0, x-buffer)
        x_end = min(width, x+buffer+1)
        y_start = max(0, y-buffer)
        y_end = min(height, y+buffer+1)
        
        roi = binary_frame[y_start:y_end, x_start:x_end]
        return np.any(roi>=254)
        
        
class Pixel:
    def __init__(self, x ,y, name):
        self.x = x
        self.y = y
        self.name=name
       
#main test:
if __name__ =="__main__":
    
    pixels_dir = {
        'n48' : Pixel(80, 164 , 'n48'),
        'n25' : Pixel(205, 120 , 'n25'),
        'p0' : Pixel(320, 100 , 'p0'),
        'p25' : Pixel(440, 110 , 'p25'),
        'p48' : Pixel(570, 155 , 'p48')
    }
    
    pixels_l = {
        'l_top_c' : Pixel(246, 220, 'l_top_c'),
        'l_top_l' : Pixel(150 ,265, 'l_top_l'),
        'l_top_r' : Pixel(282, 260, 'l_top_r'),
        'l_centr' : Pixel(208, 330, 'l_centr'),
        'l_low_l' : Pixel(110, 380, 'l_low_l'),
        'l_low_r' : Pixel(265, 380, 'l_low_r'),
        'l_low_c' : Pixel(185, 463, 'l_low_c'),
        'l_dot' : Pixel( 305, 460, 'l_dot')
    }

    pixels_r = {
        'r_top_c' : Pixel(460, 215 , 'r_top_c'),
        'r_top_l' : Pixel(410, 265 , 'r_top_l'),
        'r_top_r' : Pixel(540, 260 , 'r_top_r'),
        'r_centr' : Pixel(468, 320 , 'r_centr'),
        'r_low_l' : Pixel(400, 380 , 'r_low_l'),
        'r_low_r' : Pixel(545, 380 , 'r_low_r'),
        'r_low_c' : Pixel(475, 463 , 'r_low_c'),
        'r_dot' : Pixel(620, 455 , 'r_dot')
    }
    
    red_lower = (0, 0, 75*2.55)
    red_upper = (255, 4*2.55, 255)
    camera = Camera(pixels_dir, pixels_l, pixels_r, red_lower, red_upper)
    #camera.runCamera()
            