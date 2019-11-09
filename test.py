from qrhandler import QRPictureHandler, QRVideoHandler
from yuvreader import YUVReader
from video_assessment import VideoQualityAssessment
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def TestRead():
  reader = YUVReader("walle.yuv", (1280,720), "I420")
  ret, frame = reader.Read()
  cv2.imwrite("walle.jpg", frame)

def TestQRPictureHandler():
  image = Image.open("live_test_1.png")
  picture_handler = QRPictureHandler()
  img_1 = picture_handler.AddQRToImage(image, "1", 0)
  print(picture_handler.RecognizeQRInImage(img_1))
  img_1.save("img_1.png")

  img_2 = picture_handler.AddQRToImage(image, "2", 3)
  print(picture_handler.RecognizeQRInImage(img_2))
  img_2.save("img_2.png")

def TestQRVideoHandler():
  handler = QRVideoHandler()
  handler.QRMark("/mnt/f/code/video_set/sport.yuv", (1280, 720), "I420")
  qrresult = handler.QRRecognize("/mnt/f/code/video_set/sport.yuv.out", (1280, 720), "I420",
        qr_position=(0,0,150,150))
  for data in qrresult:
    print(data[0])

def TestQRVideoRecognize():
  handler = QRVideoHandler()
  qrresult = handler.QRRecognize("video/sport.yuv", (1280, 720), "I420",
        qr_position=(0,0,150,150))
  for data in qrresult:
    print(data[0])

def ExpandList(input):
  output = []
  for idx,value in enumerate(input):
    tmp = [idx for i in range(value)]
    output.extend(tmp)
  return output

def TestPSNRAssessment():
  assessment1 = VideoQualityAssessment("video/2.4G/sport.yuv", "video/2.4G/recovery_sport.yuv", (1280,720), "I420")
  found_ids1, psnr_data1, dropped_ids1 = assessment1.PSNRAssessment()
  framerate1 = assessment1.FrameRateAssessment(15, found_ids1, dropped_ids1)
  framerate1 = ExpandList(framerate1)

  assessment2 = VideoQualityAssessment("video/2.4G/sport.yuv", "video/2.4G/unrecovery_sport.yuv", (1280,720), "I420")
  found_ids2, psnr_data2, dropped_ids2 = assessment2.PSNRAssessment()
  framerate2 = assessment2.FrameRateAssessment(15, found_ids2, dropped_ids2)
  framerate2 = ExpandList(framerate2)

  assessment3 = VideoQualityAssessment("video/2.4G/sport.yuv", "video/2.4G/recovery_10_sport.yuv", (1280,720), "I420")
  found_ids3, psnr_data3, dropped_ids3 = assessment3.PSNRAssessment()
  framerate3 = assessment3.FrameRateAssessment(15, found_ids3, dropped_ids3)
  framerate3 = ExpandList(framerate3)

  assessment4 = VideoQualityAssessment("video/2.4G/sport.yuv", "video/2.4G/unrecovery_10_sport.yuv", (1280,720), "I420")
  found_ids4, psnr_data4, dropped_ids4 = assessment4.PSNRAssessment()
  framerate4 = assessment4.FrameRateAssessment(15, found_ids4, dropped_ids4)
  framerate4 = ExpandList(framerate4)

  fig = plt.figure()
  ax1 = fig.add_subplot(211)
  labels = ['recover', 'unrecoverable', 'recover 10% loss', 'unrecoverable 10% loss']
  p = ax1.plot(found_ids1, psnr_data1, found_ids2, psnr_data2, found_ids3, psnr_data3, found_ids4, psnr_data4)
  ax1.axhline(sum(psnr_data1)/len(psnr_data1), color=p[0].get_color(), linestyle='dashed', linewidth=1)
  ax1.axhline(sum(psnr_data2)/len(psnr_data2), color=p[1].get_color(), linestyle='dashed', linewidth=1)
  ax1.axhline(sum(psnr_data3)/len(psnr_data3), color=p[2].get_color(), linestyle='dashed', linewidth=1)
  ax1.axhline(sum(psnr_data4)/len(psnr_data4), color=p[3].get_color(), linestyle='dashed', linewidth=1)
  plt.legend(iter(p), labels)

  ax2 = fig.add_subplot(212)
  ax2.hist(framerate1, 20, histtype='step', align='mid')
  ax2.hist(framerate2, 20, histtype='step', align='mid')
  ax2.hist(framerate3, 20, histtype='step', align='mid')
  ax2.hist(framerate4, 20, histtype='step', align='mid')
  ax2.xaxis.set_major_locator(ticker.MultipleLocator(1))

  plt.show()

if __name__ == "__main__":
  TestPSNRAssessment()
  #TestQRVideoRecognize()
  #TestQRVideoHandler()