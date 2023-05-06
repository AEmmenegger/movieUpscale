import os
from re import I
import shutil
import cv2
import glob
import subprocess
import re
class ffmpegHandler():
    
    def __init__(self,input,output,ffmpegPath):
        """
        Initialize the ffmpegHandler class.
        
        :param input: str, path to the input video file
        :param output: str, path to the output folder for the extracted frames
        :param ffmpegPath: str, path to the ffmpeg executable
        """
        self.input = input
        self.ffmpegPath = ffmpegPath
        self.output = output

    def splitInput(self):
        """
        Extracts audio channels, subtitle channels, and video frames from the input video file.
        
        The extracted audio channels are saved as 'audio_<channel_index>.mp3'.
        The extracted subtitle channels are saved as 'subtitle_<channel_index>.srt'.
        The extracted video frames are saved as 'img%04d.png' in the output folder.
        """
        audio_prefix = "audio_"
        subtitle_prefix = "subtitle_"
        get_audio_channels = self.ffmpegPath + " -i " + self.input + " -vn -map 0:a -f null -c copy -y " + audio_prefix + "%d.mp3" + " 2>&1"
        ffmpeg_output = subprocess.check_output(get_audio_channels, shell=True, stderr=subprocess.STDOUT, text=True)

        # Count the number of audio and subtitle streams using regex
        num_audio_channels = len(re.findall(r'Stream #\d:\d.*Audio', ffmpeg_output))
        num_subtitle_channels = len(re.findall(r'Stream #\d:\d.*Subtitle', ffmpeg_output))

        # Then, extract each audio channel
        for i in range(num_audio_channels):
            splitAudio = self.ffmpegPath + " -i " + self.input + " -vn -map 0:a:" + str(i) + "? -c:a libmp3lame " + audio_prefix + str(i) + ".mp3"
            os.system(splitAudio)

        # Extract each subtitle stream
        for i in range(num_subtitle_channels):
            splitSubtitle = self.ffmpegPath + " -i " + self.input + " -map 0:s:" + str(i) + "? -c:s srt " + subtitle_prefix + str(i) + ".srt"
            os.system(splitSubtitle)

        splitVideo = self.ffmpegPath + " -i " + self.input + " " + self.output + "img%04d.png"
        os.system(splitVideo)

        

    def combineToVideo(self, frameLoc, out, frameRate):
        """
        Combines video frames into a single video file.
        
        :param frameLoc: str, path to the folder containing the video frames
        :param out: str, path to the output video file
        :param frameRate: str, frame rate of the input video file
        """
        combineInstr = self.ffmpegPath +" -r " + frameRate + " -start_number 0001 -f image2 -s 3840x2160" + " -i " + frameLoc + "/img%04d.png" + " -vcodec libx264 -crf 25 -pix_fmt yuv420p upscaled.mp4"
        combineInstr += " -threads 12"
        os.system(combineInstr)
        
    def addSound(self):
        """
        Merges the extracted audio channels into the upscaled video.
        
        The upscaled video file should be named 'upscaled.mp4'.
        The output file with audio will be named 'final.mp4'.
        """
        # Find all extracted audio files
        audio_files = glob.glob("audio_*.mp3")

        # Add all audio files back to the new video
        mergeAudio = self.ffmpegPath + " -i " + "upscaled.mp4"
        for i, audio_file in enumerate(audio_files):
            mergeAudio += f" -i {audio_file}"

        mergeAudio += " -c copy -map 0:v:0"
        for i in range(len(audio_files)):
            mergeAudio += f" -map {i+1}:a:0"

        mergeAudio += " final.mp4"
        os.system(mergeAudio)

    def addSubtitles(self):
        """
        Adds the extracted subtitle channels to the video file with audio.
        
        The input video file should be named 'final.mp4'.
        The output video file with subtitles will be named 'upscaledWithSubs.mp4'.
        """
        # Find all extracted subtitle files
        subtitle_files = glob.glob("subtitle_*.srt")

        input_file = "final.mp4"
        output_file = "upscaledWithSubs_0.mp4"

        for i, subtitle_file in enumerate(subtitle_files):
            mergeSubtitles = self.ffmpegPath + f" -i {input_file} -i {subtitle_file} -c copy -c:s mov_text -map 0 -map 1 {output_file}"
            os.system(mergeSubtitles)

            #Depending on what subtitle files were extracted, adding the subtitles may failv. This is a check on whether adding the subtitles succeeded or not.
            sizeBefore = os.path.getsize(input_file)
            sizeAfter = os.path.getsize(output_file)

            #Success case
            if(sizeAfter > sizeBefore):
                os.remove(input_file)
                input_file = output_file
            else:
                os.remove(output_file)

            output_file = f"upscaledWithSubs_{i+1}.mp4"

        # Rename the final output file
        if len(subtitle_files) > 0:
            os.rename(input_file, "upscaledWithSubs.mp4")





def upscale(neuralNetType, toUpscale, upScaled):
    """
    Upscales video frames using the specified neural network model.
    
    :param neuralNetType: str, type of neural network model to use for upscaling
    :param toUpscale: str, path to the folder containing the video frames to be upscaled
    :param upScaled: str, path to the folder where the upscaled frames will be saved
    """
    #Use the commented out line instead should your GPU not have enough VRAM
    #upscaleInstr = "realesrgan-ncnn-vulkan.exe -i " + toUpscale + " -o "+ upScaled+ " -n " + neuralNetType + " -t 400"
    upscaleInstr = "realesrgan-ncnn-vulkan.exe -i " + toUpscale + " -o "+ upScaled+ " -n " + neuralNetType + " -t 2400 -s 2 -f png"
    os.system(upscaleInstr)

def setup(intermed, upscaleLoc):
    """
    Creates intermediate and upscaled directories for processing video frames.
    
    :param intermed: str, path to the intermediate directory for storing video frames
    :param upscaleLoc: str, path to the directory for storing upscaled video frames
    """
    os.mkdir(intermed)
    os.mkdir(upscaleLoc)

def cleanup(intermed, upscaleLoc):
    """
    Cleans up temporary files and folders created during the video processing.
    
    Removes the intermediate directory, upscaled directory, 'upscaled.mp4', audio files, and subtitle files.
    
    :param intermed: str, path to the intermediate directory
    :param upscaleLoc: str, path to the upscaled directory
    """
    shutil.rmtree(intermed)
    shutil.rmtree(upscaleLoc)
    os.remove("./upscaled.mp4")
    
    
    audio_files = glob.glob("audio_*.mp3")
    subtitle_files = glob.glob("subtitle_*.srt")
    for i, audio_file in enumerate(audio_files):
        os.remove("./"+audio_file)

    for i, subtitle_file in enumerate(subtitle_files):
        os.remove("./"+subtitle_file)
    

def renameAndRemove(old_name, original):
    """
    Renames the upscaled video file and removes the original video file.
    
    The upscaled video file will be renamed to '<original_basename>_upscaled.<extension>'.
    The original video file will be deleted.
    
    :param old_name: str, path to the upscaled video file to be renamed
    :param original: str, path to the original video file to be removed
    """
    try:
            # Split the file name and extension of the upscaled
            _, file_extension = os.path.splitext(old_name)
            suffix = "_upscaled"
            file_name = os.path.basename(original)
            # Removing the old extension from the filename
            file_name, _ = os.path.splitext(file_name)
            new_name = f"{file_name}{suffix}{file_extension}"
            # Rename the file
            os.rename(old_name, new_name)
            print(f"File '{old_name}' has been renamed to '{new_name}'.")
    except Exception as e:
        print(f"An error occurred while renaming the file: {e}")
    #Removing the input file
    try:
        # Check if the old file exists
        if os.path.isfile(original):
            os.remove(original)
    except Exception as e:
        print(f"An error occurred while deleting the original file: {e}")

def getFPS(video_path):
    """
    Retrieves the frame rate (FPS) of the given video file.
    
    :param video_path: str, path to the video file
    :return: float or None, the frame rate (FPS) of the video file or None if the video could not be opened
    """
    video = cv2.VideoCapture(video_path)

    # Check if the video was opened successfully
    if not video.isOpened():
        print("Error: Could not open the video file.")
        return None

    # Get the framerate (FPS) of the video
    framerate = video.get(cv2.CAP_PROP_FPS)

    # Release the video object
    video.release()

    return framerate

def removingWhiteSpaces(directory_path):
    """
    Removes white spaces from file names in the specified directory.
    
    Replaces all white spaces in file names with underscores ('_') in the given directory.
    
    :param directory_path: str, path to the directory containing the files to be renamed
    """
    for filename in os.listdir(directory_path):
        new_filename = filename.replace(' ', '_')
        old_file_path = os.path.join(directory_path, filename)
        new_file_path = os.path.join(directory_path, new_filename)

        if old_file_path != new_file_path:
            os.rename(old_file_path, new_file_path)


def main():
    """
    The main function that processes video files in the input directory.
    
    For each video file in the input directory, the following steps are performed:
      1. Removing white spaces in file names.
      2. Extracting audio, subtitles, and video frames using ffmpegHandler.
      3. Upscaling video frames using a neural network model.
      4. Combining upscaled video frames into a single video file.
      5. Merging audio channels into the upscaled video.
      6. Adding subtitle channels to the upscaled video with audio.
      7. Renaming the upscaled video file and removing the original video file.
      8. Cleaning up temporary files and folders.
    """
    intermed = "./frames/"
    ffmpeg_path = "ffmpeg.exe"
    neuralNet = "RealESRGANv2-animevideo-xsx2"
    upscaleLoc = "./upscaled"
    inputPath = "input/"
    removingWhiteSpaces(inputPath)
    all_contents = os.listdir(inputPath)
    print(all_contents) 
    for item in all_contents:
        # Use os.path.join() to create the full path to the item
        item_path = os.path.join(inputPath, item)
        setup(intermed, upscaleLoc)
        ff = ffmpegHandler(item_path,intermed,ffmpeg_path)
        ff.splitInput()
        upscale(neuralNet, intermed, upscaleLoc)
        ff.combineToVideo(upscaleLoc, "upscaled.mp4", str(getFPS(item_path)))
        ff.addSound()
        ff.addSubtitles()
        renameAndRemove("upscaledWithSubs.mp4", item_path)


        cleanup(intermed, upscaleLoc)

    

if __name__ == "__main__":
    main()
