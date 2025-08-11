import wave
import math
import struct
import numpy as np
from PIL import Image
import sys

def main():
    img = Image.open('output.png').convert('L')
    arr = np.array(img)
    height, width = arr.shape
    
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
                normalized = sample * 32767
                wav_file.writeframes(struct.pack('<h', int(normalized)))
                phase += angle_increment
        
        forge += 1
        percentage = (forge / height) * 100
        sys.stdout.write(f"\r\x1b[34mProgress\x1b[0m: {percentage:.2f}%")
        sys.stdout.flush()
    
    wav_file.close()
    print("\nAudio generation completed. Saved as apt.wav")

if __name__ == "__main__":
    main()