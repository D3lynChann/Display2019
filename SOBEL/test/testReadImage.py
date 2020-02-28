from PIL import Image
import numpy as np

img = np.array(Image.open(r'I:\codes\test\testPicClr.bmp').convert('I')).tolist()
        
gray = Image.fromarray(np.array(img)).convert('L')      

gray.save(r'I:\codes\test\testPicOutput.bmp', 'bmp')