import cv2
import os
import config

# Path to the input video file
video_path = 'bad_apple.mp4'  # Change this to your video file path
output_folder = 'frames'  # Folder to save the frames

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Open the video file
cap = cv2.VideoCapture(video_path)

frame_count = 0
saved_frame_count = 0

while True:
    ret, frame = cap.read()  # Read a frame from the video
    if not ret:
        break  # Exit the loop if there are no frames left

    # save the frames at a certain frame rate
    if frame_count % (30//config.FRAME_RATE) == 0:
        # Resize the frame
        resized_frame = cv2.resize(frame, (config.ASPECT_RATIO_WIDTH, config.ASPECT_RATIO_HEIGHT))

        # Save the resized frame as an image file
        frame_filename = os.path.join(output_folder, f'frame_{saved_frame_count:04d}.png')
        cv2.imwrite(frame_filename, resized_frame)

        saved_frame_count += 1  # Increment the saved frame count

    frame_count += 1  # Increment the total frame count

# Release the video capture object
cap.release()

print(f"Extracted {saved_frame_count} frames and saved them to '{output_folder}' directory.")

## Create categorized frames

print("Beginning categorization process...")

# Input and output paths
categorized_frames_output_folder = 'pixel_categorized_frames'  # Folder for categorized pixels

# Create the output folder if it doesn't exist
os.makedirs(categorized_frames_output_folder, exist_ok=True)

# Iterate through each frame in the frames folder
for frame_file in os.listdir(output_folder):
    if frame_file.endswith('.png'):
        # Read the frame
        frame_path = os.path.join(output_folder, frame_file)
        frame = cv2.imread(frame_path)

        # Create an array to hold pixel categories
        pixel_categories = []

        # Loop through each pixel in the frame
        for row in range(frame.shape[0]):  # Iterate over height
            row_categories = []  # Categories for this row
            for col in range(frame.shape[1]):  # Iterate over width
                # Get the pixel value (assuming grayscale)
                pixel_value = frame[row, col][0]  # Get the intensity of the pixel

                # Classify the pixel as black or white
                if pixel_value < 128:  # Threshold to distinguish between black and white
                    row_categories.append('0')
                else:
                    row_categories.append('1')
            
            # Append the row categories to the pixel categories
            pixel_categories.append(row_categories)

        # Save the pixel categories to a text file
        output_file_path = os.path.join(categorized_frames_output_folder, f'categorized_{frame_file[:-4]}.txt')
        with open(output_file_path, 'w') as f:
            for row in pixel_categories:
                f.write(' '.join(row) + '\n')

print(f"Categorized pixel frames saved to '{categorized_frames_output_folder}' directory.")
