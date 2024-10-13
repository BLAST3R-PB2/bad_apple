# PB2 Video to Map Converter

This project converts a video file (specifically "bad_apple.mp4") into a series of frames and generates a map file for Plazma Burst 2 (PB2) based on the pixel data from these frames. The project includes scripts for frame extraction, pixel categorization, and XML map generation.

## Video Showcase

Check out the YouTube video showcasing the "Bad Apple" animation in Plazma Burst 2 side by side with the original:

[Watch the Bad Apple Animation](https://www.youtube.com/watch?v=mGOykNZoVmc)

## Features

- Extract frames from a video at 5 frames per second (fps).
- Categorize pixels in each frame as either black or white.
- Generate a PB2-compatible map in XML format based on the pixel data.
- Customizable aspect ratio for the frame extraction and mapping process.

## Files

- `create_frames.py`: Script to extract frames from the video and categorize pixels.
- `create_pb2_map.py`: Script to generate the PB2 map from categorized pixel data.
- `config.py`: Configuration file to set the aspect ratio.
- `bad_apple.mp4`: Input video file for frame extraction.

## Installation

1. Clone this repository and navigate into the directory:
   ```bash
   git clone https://github.com/BLAST3R-PB2/bad_apple.git
   cd bad_apple
   ```

2. Ensure you have OpenCV installed. You can install it via pip:
   ```bash
   pip install opencv-python
   ```

## Usage

1. Extract frames from the video:
   ```bash
   python create_frames.py
   ```

2. Generate the PB2 map:
   ```bash
   python create_pb2_map.py
   ```

The extracted frames will be saved in the `frames` directory, and the categorized pixel frames will be in the `pixel_categorized_frames` directory. The final map will be saved as `bad_apple_map.xml`.

## Configuration

You can adjust the aspect ratio in the `config.py` file:

```python
ASPECT_RATIO_WIDTH = 16
ASPECT_RATIO_HEIGHT = 12
```

#### Note: 

From my experience, due to PB2's limitations, it's only possible to load & play maps up to **15MB** in size.
The map will fail to load and the game will throw an error if the `bad_apple_map.xml` file is too large.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
