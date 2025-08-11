# apt_encode_python
这是一个基于python的apt生成代码,您可以输入以下命令来运行这个脚本
python File_Directory/apt.py input1.png(chA) input2.png(chB)
你需要安装下列支持库来使用这个脚本:pillow,numpy
#!bin/bash pip install pillow numpy
对于termux
#!bin/bash
pkg update&&pkg upgrade
pkg install python numpy pillow
输入图片不支持16位灰度图像,png格式,图片会变白
可以用ffmpeg转换格式
#!bin/bash
apt install ffmpeg
对于termux
#!bin/bashpkg install ffmpeg

#!bin/bash
ffmpeg -i input.png(input.tiff) output.jpg
脚本会预先生成图片,既output.png,在生成12480采样率的wav文件
