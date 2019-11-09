import numpy as np
import cv2

class YUVReader:
  def __init__(self, filename, size, format):
    self.yuv_file = open(filename, 'rb')
    self.width, self.height = size
    if (format == "I420"):
      self.ParseI420()

  def ParseI420(self):
    self.frame_size = int(self.width * self.height * 3 / 2)
    self.frame_shape = (int(self.height * 3 / 2), self.width)
    self.color_format = cv2.COLOR_YUV2RGB_I420
  
  def ReadRaw(self):
    try:
      raw = self.yuv_file.read(self.frame_size)
      if (len(raw) == 0):
        return False, None
      yuv = np.frombuffer(raw, dtype=np.uint8)
      yuv = yuv.reshape(self.frame_shape)
    except Exception as e:
      print(e)
      return False,None
    return True, yuv
  
  def Read(self):
    ret, yuv = self.ReadRaw()
    if not ret:
      return ret, yuv
    bgr = cv2.cvtColor(yuv, self.color_format)
    return True, bgr