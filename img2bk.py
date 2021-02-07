#!/usr/bin/python
# -*- coding: windows-1251 -*- 

from PIL import Image
import sys
import numpy as np
import struct


#width, height = 512, 256 # Ширина и высота экрана
width, height = 256, 256 # Ширина и высота экрана
image_offset, image_size = 0o40000, 0o100000 - 0o40000 # Адрес загрузки и размер изображения


def combine(b):
    return ((b[3]&3)<<6) | ((b[2]&3)<<4) | ((b[1]&3)<<2) | (b[0]&3) 


print("Usage: img2bk [--no-dither] [--fit] [--no-preview] Image1 Image2 ...")

dither = False
try:
    sys.argv.remove("--no-dither")
except ValueError:
    dither = True

cover = False
try:
    sys.argv.remove("--fit")
except ValueError:
    cover = True

preview = False
try:
    sys.argv.remove("--no-preview")
except ValueError:
    preview = True


palette = [0,   0,   0,  
           0,   0,   255, 
           0,   255, 0, 
           255, 0,   0]
p_img = Image.new('P', (16, 16))
p_img.putpalette(palette * 64)
    
for imgfn in sys.argv[1:]:
    in_image = Image.open(imgfn).convert("RGB")
    w,h = in_image.size

    hh = int(float(width*h)/w)
    if (cover and (hh > height)) or ((not cover) and (hh < height)):
        in_image = in_image.resize((width,hh), Image.ANTIALIAS).crop( (0,(hh-height)/2, width,(hh+height)/2) )
    else:
        w = int(float(w*height)/h)
        in_image = in_image.resize((w, height), Image.ANTIALIAS).crop( ((w-width)/2,0,(w+width)/2,height) )

    conv = in_image.quantize(palette=p_img, dither=(1 if dither else 0))
    if preview:
        conv.show()
    
    data = np.frombuffer(bytes(conv.tobytes()), dtype=np.uint8)
    data = data.reshape(-1,4)
    
    # Формирование файла для загрузки в экран БК
    with open(imgfn + '.BIN', mode='wb') as f:
        f.write(struct.pack('<HH',image_offset, image_size))
        f.write(bytearray(map(combine, data))) # Bitmap
