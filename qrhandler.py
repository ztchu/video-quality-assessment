from pyzbar.pyzbar import decode
from yuvreader import YUVReader
import PIL.Image as Image
import argparse
import cv2
import numpy as np
import qrcode
import os

BAD_IMAGE_PATH = "bad"
class QRPictureHandler:
  def __init__(self):
    self.error_correct_flag = [
      qrcode.constants.ERROR_CORRECT_L, 
      qrcode.constants.ERROR_CORRECT_M, 
      qrcode.constants.ERROR_CORRECT_Q, 
      qrcode.constants.ERROR_CORRECT_H
    ]

  def AddQRToImage(self, image, message, error_correction=3, border=0):
    '''
      Add QR in top-left of image.
    Args:
      image: Image type data, get from Image.open(..) or other way.
      message: message QR store.
      error_correction: Determine the robustness of QR, from 0 ~ 3.
      border: Image border.
    Return:
      Image with QR
    '''
    qr=qrcode.QRCode(
      version=1,
      error_correction=self.error_correct_flag[error_correction],
      border=border,
    )
    qr.add_data(message)
    qr.make()
    qr_img = qr.make_image().resize((150,150))
    image.paste(qr_img, (0,0))
    return image
  
  def RecognizeQRInImage(self, image):
    '''
      Recognize the QR and return it's message.
    Args:
      image: Image type data, get from Image.open(..) or other way.
    Return:
      Message in QR.
    '''
    encoded  = decode(image)
    if (not len(encoded)):
      return []
    return [item.data for item in encoded]

class QRVideoHandler:
  def __init__(self):
    self.frame_handler = QRPictureHandler()
  
  def QRMark(self, video_name, size, format): 
    '''
      Mark number as QR in each frame of video. Number start with 0.
    Args:
      video_name: Name of input file.
      size: Video (width, height) pair. 
      format: Color format, only support color format I420 at this time.
    Return:
      Output a file with .out behind video file name.
    '''
    video_reader = YUVReader(video_name, size, format)
    with open(video_name+".out", 'wb') as video_out:
      frame_index = 0
      while (True):
        ret, frame = video_reader.Read()
        if (ret == False):
          break
        frame = Image.fromarray(frame)
        new_frame = self.frame_handler.AddQRToImage(
          image=frame,
          message=str(frame_index),
        )
        new_frame = cv2.cvtColor(np.asarray(new_frame), cv2.COLOR_RGB2YUV_I420)
        video_out.write(new_frame)
        frame_index += 1
    
  def QRRecognize(self, video_name, size, format, qr_position=None):
    '''
      Recognize QR message in each frame of video.
    Args:
      video_name: Name of input file.
      size: Video (width, height) pair. 
      format: Color format, only support color format I420 at this time.
      qr_position: Can specify the position of QR in image to increase accuracy, by default, recognize the whole image.
    Return:
      Array include QR message and frame data.
    '''
    video_reader = YUVReader(video_name, size, format)
    result_map = []
    if not os.path.exists(BAD_IMAGE_PATH):
      os.makedirs(BAD_IMAGE_PATH)
    while(True):
      ret, frame = video_reader.Read()
      if (ret == False):
        break
      image = Image.fromarray(frame)
      if (qr_position != None):
        image = image.crop(qr_position)
      qrdatas = self.frame_handler.RecognizeQRInImage(image)
      if len(qrdatas) != 1:
        image.save(os.path.join(BAD_IMAGE_PATH, str(len(result_map))+".png"))
        print("Can't recognize frame! Save as " + str(len(result_map))+".png")
        result_map.append((None, frame))
      else:
        result_map.append((int(qrdatas[0].decode()), frame))
    return result_map

if __name__ == "__main__":
  parse = argparse.ArgumentParser(description = 'manual to this script')
  parse.add_argument('--videoname', type=str, default="walle.yuv", help="Video to mark QR")
  parse.add_argument('--dimension', type=str, default="1280x720", help="Width and height of video, like 1280x720")
  parse.add_argument('--format', type=str, default="I420", help="Color format of video, like I420")
  argv = parse.parse_args()

  handler = QRVideoHandler()
  size = argv.dimension.split('x')
  width = int(size[0])
  height = int(size[1])
  if (argv.format != "I420"):
    parse.help()
  else:
    handler.QRMark(argv.videoname, (width, height), argv.format)