from qrhandler import QRVideoHandler
from skimage.measure import compare_ssim
from skimage.measure import compare_psnr
from skimage.metrics import peak_signal_noise_ratio
import argparse
import math
from policy import ProcessPolicy

class ProcessorBase(object):
  def __init__(self):
    self.results = []

  def GetResult(self):
    return self.results

class PSNRProcessor(ProcessorBase):
  def __init__(self):
    self.ids = []
    super(PSNRProcessor,self).__init__()
  
  def __call__(self, id, raw_frame, test_frame):
    self.ids.append(id)
    self.results.append(peak_signal_noise_ratio(raw_frame,test_frame))
  
  def GetResult(self):
    return self.ids, self.results

class DropFrameProcessor(ProcessorBase):
  def __init__(self):
    super(DropFrameProcessor,self).__init__()
  
  def __call__(self, id, data):
    print(str(id) + " droped!")
    self.results.append(int(id))


class VideoTraverser:
  def __init__(self, raw_video, test_video, size, format):
    self.video_handler = QRVideoHandler()
    self.raw_video = raw_video
    self.test_video = test_video
    self.raw_video_content = None
    self.test_video_content = None
    self.video_width, self.video_height = size
    self.video_format = format
    self.policy = ProcessPolicy.DropNoneId

  def SetPolicy(self, policy):
    self.policy = policy

  def LoadVideo(self):
    self.raw_video_content = self.video_handler.QRRecognize(
        self.raw_video,
        (self.video_width, self.video_height),
        self.video_format,
        qr_position=(0,0,150,150))
    
    self.test_video_content = self.video_handler.QRRecognize(
        self.test_video,
        (self.video_width, self.video_height),
        self.video_format,
        qr_position=(0,0,150,150))
    
    if (not len(self.raw_video_content) or
        not len(self.test_video_content)):
      raise Exception("Invalid raw video or test video.")
  
  def Preprocess(self):
    if (not self.raw_video_content):
      self.LoadVideo()
    
    if self.policy == ProcessPolicy.DropNoneId:
      return
    elif self.policy == ProcessPolicy.LeftAlign:
      left_id = -1
      for index in range(len(self.test_video_content)):
        if self.test_video_content[index][0] == None:
          self.test_video_content[index] = (left_id + 1, self.test_video_content[index][1]) 
          left_id += 1
        else:
          left_id = self.test_video_content[index][0]
    elif self.policy == ProcessPolicy.RightAlign:
      right_id = len(raw_video_content)
      for index in range(len(self.test_video_content))[::-1]:
        if self.test_video_content[index][0] == None:
          self.test_video_content[index][0] = (right_id - 1, self.test_video_content[index][2])
          right_id -= 1
        else:
          right_id = self.test_video_content[index][0]


  def Process(self, frame_existed_processor, frame_dropped_processor):
    self.Preprocess()
    for raw_frame_id,raw_frame_data in self.raw_video_content:
      test_frame_id, test_frame_data = self.GetTestFrameContent(raw_frame_id)
      if (test_frame_id != None):
        frame_existed_processor(raw_frame_id, raw_frame_data, test_frame_data)
      else:
        frame_dropped_processor(raw_frame_id, raw_frame_data)
  
  def GetTestFrameContent(self, id):
    for test_frame_id, test_frame_data in self.test_video_content:
      if (test_frame_id == id):
        return test_frame_id, test_frame_data
    return None,None

class VideoQualityAssessment:
  def __init__(self, raw_video, test_video, dimension, format):
    self.raw_video = raw_video
    self.test_video = test_video
    self.video_dimension = dimension
    self.video_format = format
    self.video_traverser = VideoTraverser(
        self.raw_video, 
        self.test_video,
        self.video_dimension,
        self.video_format)

  def PSNRAssessment(self):
    psnr_processor = PSNRProcessor()
    dropped_processor = DropFrameProcessor()
    self.video_traverser.SetPolicy(ProcessPolicy.LeftAlign)
    self.video_traverser.Process(psnr_processor, dropped_processor)
    found_ids, psnr_result = psnr_processor.GetResult()
    dropped_ids = dropped_processor.GetResult()
    return found_ids, psnr_result, dropped_ids
  
  def FrameRateAssessment(self, framerate, found_ids, dropped_ids):
    total_frame = len(found_ids) + len(dropped_ids)
    duration = math.ceil(total_frame / framerate)
    frame_per_second = [framerate for _ in range(duration)]
    for dropped in dropped_ids:
      idx = int(dropped / framerate)
      frame_per_second[idx] -= 1
    
    return frame_per_second
      

if __name__ == "__main__":
  parse = argparse.ArgumentParser(description = 'manual to this script')
  parse.add_argument('--rawvideo', type=str, default="", help="Raw video, video before encode.")
  parse.add_argument('--testvideo', type=str, default="", help="Test video, video after encode, transmission and decode.")
  parse.add_argument('--dimension', type=str, default="", help="Width and height of video, like 1280x720")
  parse.add_argument('--format', type=str, default="", help="Color format of video, like I420")
  argv = parse.parse_args()

  assessment = VideoQualityAssessment("video/sport.yuv", "video/sport_test.yuv", (1280,720), "I420")
  found_ids, psnr_data, dropped_ids = assessment.PSNRAssessment()
  plt.plot(found_ids, psnr_data)
  plt.show()