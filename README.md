# Video Upscaler

This Python script allows you to upscale videos using the RealESRGANv2-animevideo-xsx2 model by default. The model is based on the paper [Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data](https://arxiv.org/abs/2111.09630) by Xintao Wang, Liangbin Xie, Chao Dong, and Ying Shan. 

The script extracts audio channels, subtitle channels, and video frames from the input video file, upscales the video frames using the specified neural network model, and then combines the upscaled frames, audio channels, and subtitle channels into a final upscaled video file.

Please note that the script currently requires a significant amount of storage for processing long videos. This issue will be addressed in future updates.

## Dependencies

To use this script, you need to have the following installed:

- Python 3
- OpenCV (`pip install opencv-python`)
- FFmpeg executable in the same directory as the script

You also need the RealESRGANv2-animevideo-xsx2 model, which can be downloaded from the [Real-ESRGAN repository](https://github.com/xinntao/Real-ESRGAN).

## Usage

1. Clone the repository or download the script.
2. Install the required dependencies.
If you haven't cloned the repository and only downloaded the script proceed with steps 3 and 4. Otherwhise you can proceed with step 5.
3. Place the FFmpeg executable in the same directory as the script.
4. Download the RealESRGANv2-animevideo-xsx2 model and update the `neuralNet` variable in the script with the appropriate path.
5. Place the video files you want to upscale in the `input/` folder.
6. Run the script using the following command:

```
python upscale.py
```

The script will process each video file in the `input/` folder and save the upscaled video files in the same directory with the `_upscaled` suffix.

## Customizing the Model

If you want to use a different model for upscaling, you can update the `neuralNet` variable in the script with the path to the desired model.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please [open an issue](https://github.com/your-username/your-repo/issues) or submit a pull request.