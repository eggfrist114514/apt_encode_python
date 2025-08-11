import numpy as np
from PIL import Image
import sys
import wave
import math
import struct
import os

SYNCA = "000011001100110011001100110011000000000"
SYNCB = "000011100111001110011100111001110011100"

def process_image_path(path):
    return path.strip('"').strip("'")

def convert_to_8bit(image):
    if image.mode == 'I;16':
        array = np.array(image, dtype=np.uint16)
        array = (array >> 8).astype(np.uint8)
        return Image.fromarray(array, 'L')
    else:
        return image.convert('L')

def generate_image():
    if len(sys.argv) != 3:
        print("Usage: python apt_encoder.py image1.jpg image2.png")
        return
    
    img1_path = process_image_path(sys.argv[1])
    img2_path = process_image_path(sys.argv[2])
    
    apt_format = int(input("APT格式 (0=可见光/红外, 1=红外/红外): "))
    fault_flag = int(input("故障标志 (0=不故障, 1=故障): "))
    
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    img1 = convert_to_8bit(img1)
    img2 = convert_to_8bit(img2)
    
    w1, h1 = img1.size
    new_height = int(909 * h1 / w1)
    imgA = img1.resize((909, new_height), Image.NEAREST)
    imgB = img2.resize((909, new_height), Image.NEAREST)
    
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
        
        if y % 120 == 0 or y % 120 == 1:
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
            spaceB = 0 if (y % 120 == 0 or y % 120 == 1) else 255
        else:
            spaceB = 255 if (y % 120 == 0 or y % 120 == 1) else 0
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
    
    output_path = 'output.png'
    Image.fromarray(output).save(output_path)
    print(f"APT图像已保存至: {os.path.abspath(output_path)}")
    return new_height, total_width

def generate_audio(height, width):
    output_path = 'output.png'
    if not os.path.exists(output_path):
        print("错误: 未找到output.png文件")
        return
    
    img = Image.open(output_path)
    if img.mode != 'L':
        img = convert_to_8bit(img)
    arr = np.array(img)
    
    sample_rate = 12480
    frequency = 2400
    samples_per_pixel = sample_rate // (2 * width)
    
    wav_file = wave.open('apt.wav', 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    
    phase = 0.0
    angle_increment = 2 * math.pi * frequency / sample_rate
    forge = 0
    
    for y in range(height):
        for x in range(width):
            pixel = arr[y, x]
            amplitude = pixel / 255.0
            
            for _ in range(samples_per_pixel):
                sample = amplitude * math.sin(phase)
                normalized = int(sample * 32767)
                wav_file.writeframes(struct.pack('<h', normalized))
                phase += angle_increment
        
        forge += 1
        percentage = (forge / height) * 100
        sys.stdout.write(f"\r\x1b[34mProgress\x1b[0m: {percentage:.2f}%")
        sys.stdout.flush()
    
    wav_file.close()
    print(f"\nAPT音频已保存至: {os.path.abspath('apt.wav')}")

if __name__ == "__main__":
    height, width = generate_image()
    generate_audio(height, width)