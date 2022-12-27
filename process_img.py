import cv2
from PIL import Image
import os
input_dir = 'images/haimura-images'
output_dir = 'images/haimura-images-processed'
h = 512
w = 512
aspect_ratio = (h,w)

imgs = os.listdir(input_dir)

def resize_img(path,l):
    print(path)
    img = cv2.imread(path)
    original_shape = (img.shape[1],img.shape[0] )
    print(original_shape)
    # (h,w)
    min_edge = min(original_shape)
    '''
    
    if portrait, min-edge = w, then 
        ratio = w/l
        
    
    '''
    ratio = min_edge/l
    new_shape =[ int(x/ratio) for x in original_shape ]
    print('New shape:',new_shape)
    img2 = cv2.resize(img,new_shape,interpolation=cv2.INTER_CUBIC)
    cv2.imshow("new",img2)
    cv2.waitKey(-1)


resize_img( os.path.join(input_dir,imgs[0]) , 512 )


# for f in os.listdir(input_dir):
#     print(f)
#     img = Image.open( os.path.join(input_dir,f) )
#     img = img.resize(aspect_ratio)
#     img.save( os.path.join(output_dir,f) )
