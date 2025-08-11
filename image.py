import numpy as np
from PIL import Image
import sys

SYNCA = "000011001100110011001100110011000000000"
SYNCB = "000011100111001110011100111001110011100"

def main():
    if len(sys.argv) != 3:
        print("Usage: python apt_encoder.py image1.jpg image2.png")
        return
    
    apt_format = int(input("APT格式 (0=可见光/红外, 1=红外/红外): "))
    fault_flag = int(input("故障标志 (0=不故障, 1=故障): "))
    
    img1 = Image.open(sys.argv[1]).convert('L')
    img2 = Image.open(sys.argv[2]).convert('L')
    
    w1, h1 = img1.size
    new_height = int(909 * h1 / w1)
    imgA = img1.resize((909, new_height))
    imgB = img2.resize((909, new_height))
    
    arrA = np.array(imgA)
    arrB = np.array(imgB)
    
    len_syncA = len(SYNCA)
    len_syncB = len(SYNCB)
    len_space = 47
    len_telemetry = 45
    len_image = 909
    
    total_width = len_syncA + len_space + len_image + len_telemetry + len_syncB + len_space + len_image + len_telemetry
    output = np.zeros((new_height, total_width), dtype=np.uint8)
    
    syncA_arr = np.array([255 if c == '1' else 0 for c in SYNCA], dtype=np.uint8)
    syncB_arr = np.array([255 if c == '1' else 0 for c in SYNCB], dtype=np.uint8)
    
    avhrr = 0
    avhrr1 = 0
    
    for y in range(new_height):
        line = []
        
        line.extend(syncA_arr.tolist())
        
        if y % 110 == 0 or y % 110 == 1:
            spaceA = 255 if apt_format == 0 else 0
        else:
            spaceA = 0 if apt_format == 0 else 255
        line.extend([spaceA] * len_space)
        
        line.extend(arrA[y].tolist())
        
        if 0 <= avhrr < 7:
            t_val = 0
        elif 7 <= avhrr < 14:
            t_val = 57
        elif 14 <= avhrr < 21:
            t_val = 28
        elif 21 <= avhrr < 28:
            t_val = 57
        elif 28 <= avhrr < 35:
            t_val = 85
        elif 35 <= avhrr < 42:
            t_val = 114
        elif 42 <= avhrr < 49:
            t_val = 142
        elif 49 <= avhrr < 56:
            t_val = 171
        elif 56 <= avhrr < 63:
            t_val = 199
        elif 63 <= avhrr < 70:
            t_val = 227
        elif 70 <= avhrr < 77:
            t_val = 255
        elif 77 <= avhrr < 84:
            t_val = 0
        elif 84 <= avhrr < 112:
            t_val = 57
        elif 112 <= avhrr < 119:
            t_val = 0
        else:
            t_val = 85
        line.extend([t_val] * len_telemetry)
        
        line.extend(syncB_arr.tolist())
        
        if fault_flag == 0:
            spaceB = 0 if (y % 110 == 0 or y % 110 == 1) else 255
        else:
            spaceB = 255 if (y % 110 == 0 or y % 110 == 1) else 0
        line.extend([spaceB] * len_space)
        
        line.extend(arrB[y].tolist())
        
        if 0 <= avhrr1 < 7:
            t_val1 = 114
        elif 7 <= avhrr1 < 14:
            t_val1 = 57
        elif 14 <= avhrr1 < 21:
            t_val1 = 28
        elif 21 <= avhrr1 < 28:
            t_val1 = 57
        elif 28 <= avhrr1 < 35:
            t_val1 = 85
        elif 35 <= avhrr1 < 42:
            t_val1 = 114
        elif 42 <= avhrr1 < 49:
            t_val1 = 142
        elif 49 <= avhrr1 < 56:
            t_val1 = 171
        elif 56 <= avhrr1 < 63:
            t_val1 = 199
        elif 63 <= avhrr1 < 70:
            t_val1 = 227
        elif 70 <= avhrr1 < 77:
            t_val1 = 255
        elif 77 <= avhrr1 < 84:
            t_val1 = 0
        elif 84 <= avhrr1 < 112:
            t_val1 = 57
        elif 112 <= avhrr1 < 119:
            t_val1 = 114
        else:
            t_val1 = 85
        line.extend([t_val1] * len_telemetry)
        
        output[y] = np.array(line, dtype=np.uint8)
        
        avhrr = 0 if avhrr >= 126 else avhrr + 1
        avhrr1 = 0 if avhrr1 >= 126 else avhrr1 + 1
    
    Image.fromarray(output).save('output.png')

if __name__ == "__main__":
    main()