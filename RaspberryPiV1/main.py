from multiprocessing import Process, Queue
import time
from lora import LoRa
from camera import Camera
from camera import Pixel

def loraTask(lora, queue):
    prevDistance = None
    prevDirection = None
    
    lora.initialize_lora()
    
    while True:
        time.sleep(0.01)
        if not queue.empty():
            data = queue.get()
            distance = data['dist']
            direction = data['dir']
            if distance!=prevDistance or direction !=prevDirection:
                prevDistance = distance
                prevDirection = direction
                lora.send_message(f"Angle:{direction};Distance:{distance}")
                time.sleep(0.2)
            
        
def cameraTask(camera, queue):
    print('running camera')
    camera.initPiCamera()
    camera.runCamera(queue)
    
def initCamera():
    pixels_dir = {
        'n48' : Pixel(52, 102, 'n48'),
        'n25' : Pixel(163, 52, 'n25'),
        'p0' : Pixel(295, 29, 'p0'),
        'p25' : Pixel(423, 45, 'p25'),
        'p48' : Pixel(536, 77, 'p48')
    }
    
    pixels_l = {
        'l_top_c' : Pixel(199, 152, 'l_top_c'),
        'l_top_l' : Pixel(121, 206, 'l_top_l'),
        'l_top_r' : Pixel(256, 198, 'l_top_r'),
        'l_centr' : Pixel(167, 260, 'l_centr'),
        'l_low_l' : Pixel(82, 325, 'l_low_l'),
        'l_low_r' : Pixel(232, 322, 'l_low_r'),
        'l_low_c' : Pixel(138, 395, 'l_low_c'),
        'l_dot' : Pixel(275, 389, 'l_dot')
    }

    pixels_r = {
        'r_top_c' : Pixel(437, 140, 'r_top_c'),
        'r_top_l' : Pixel(375, 194, 'r_top_l'),
        'r_top_r' : Pixel(506, 182, 'r_top_r'),
        'r_centr' : Pixel(434, 245, 'r_centr'),
        'r_low_l' : Pixel(367, 317, 'r_low_l'),
        'r_low_r' : Pixel(511, 304, 'r_low_r'),
        'r_low_c' : Pixel(434, 374, 'r_low_c'),
        'r_dot' : Pixel(572, 366, 'r_dot')
    }
    
    red_lower = (0, 0, 75*2.55)
    red_upper = (255, 4*2.55, 255)
    camera = Camera(pixels_dir, pixels_l, pixels_r, red_lower, red_upper)
    return camera
    
if __name__ == '__main__':
    lora = LoRa()
    camera = initCamera()
    q = Queue()
    
    p1 = Process(target = loraTask, args=(lora, q))
    p2 = Process(target = cameraTask, args=(camera, q))
    
    p1.start()
    p2.start()
    
    #p1.terminate()
    #p2.terminate()
    
    p1.join()
    p2.join()