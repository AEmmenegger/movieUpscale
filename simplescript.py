import os
import cv2

class ffmpegHandler():
    
    def __init__(self,input,output,ffmpegPath):
        
        self.input = input
        self.ffmpegPath = ffmpegPath
        self.output = output

    def splitInput(self):
        #ffmpeg -i out.mkv -vn -c:a libmp3lame -y audio.mp3 besser glaub
        splitAudio = self.ffmpegPath + " -i " + self.input + " -vn -c:a libmp3lame -y out.mp3"
        splitVideo = self.ffmpegPath + " -i " + self.input + " " + self.output + "img%04d.png"

        os.system(splitAudio)
        os.system(splitVideo)

    def combineToVideo(self, frameLoc, out, frameRate):
        combineInstr = self.ffmpegPath +" -r " + frameRate + " -start_number 0001 -f image2 -s 3840x2160" + " -i " + frameLoc + "/img%04d.png" + " -vcodec libx264 -crf 25 -pix_fmt yuv420p upscaled.mp4"
        os.system(combineInstr)
        
    def addSound(self):
        mergeAudio = self.ffmpegPath + " -i " + "upscaled.mp4" + " -i " + "out.mp3" + " -c copy -map 0:v:0 -map 1:a:0 final.mp4"
        os.system(mergeAudio)

def upscale(neuralNetType, toUpscale, upScaled):
    #upscaleInstr = "realesrgan-ncnn-vulkan.exe -i " + toUpscale + " -o "+ upScaled+ " -n " + neuralNetType + " -t 400"
    upscaleInstr = "realesrgan-ncnn-vulkan.exe -i " + toUpscale + " -o "+ upScaled+ " -n " + neuralNetType + " -s 2 -f png"
    os.system(upscaleInstr)


def main():
    
    #name of input file
    input = "input/in.mkv"
    intermed = "./frames/"
    ffmpeg_path = "ffmpeg.exe"
    neuralNet = "RealESRGANv2-animevideo-xsx2"
    upscaleLoc = "./upscaled"
    #upscaleLoc = "C:\\Users\\andre\\Videos\\superscale\\upscaled"
    ff = ffmpegHandler(input,intermed,ffmpeg_path)
    
    
    #ff.splitInput()
    upscale(neuralNet, "frames", upscaleLoc)
    ff.combineToVideo(upscaleLoc, "upscaled.mp4", "23.976215")
    ff.addSound()


    """video = cv2.VideoCapture(input)
    fps = video.get(cv2.CAP_PROP_FPS)
    ff.splitInput()
    upscale(neuralNet, "frames", "upscaled")
    ff.combineToVideo("./upscale", "upscaled.mp4", fps)
    ff.addSound()
    """
    

    

if __name__ == "__main__":
    main()
