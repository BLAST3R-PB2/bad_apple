import os
import config

FILE_NAME = "bad_apple_map.xml"

## STEP 1

width_pixels = config.ASPECT_RATIO_WIDTH  # Number of pixels wide (4:3 aspect ratio)
height_pixels = config.ASPECT_RATIO_HEIGHT  # Number of pixels high (4:3 aspect ratio)

# Calculate the offset to center the grid on (0, 0)
x_offset = -(width_pixels // 2) * config.PIXEL_SIZE
y_offset = -(height_pixels // 2) * config.PIXEL_SIZE

# Start writing the XML data
xml_data = []

PLAYER_NAME = 'BLAST3R'
ZOOM_VALUE = 100

# player, camera, and concrete ground data
player_data_xml = f'<player uid="#player*1" x="270" y="170" tox="0" toy="0" hea="500" hmax="500" team="0" side="1" char="77" incar="-1" botaction="0" ondeath="-1" /><box x="-500" y="170" w="1100" h="1230" m="0" /><trigger uid="#trigger*9999999" x="310" y="20" enabled="true" maxcalls="1" actions_1_type="51" actions_1_targetA="{ZOOM_VALUE}" actions_1_targetB="0" actions_2_type="52" actions_2_targetA="#player*1" actions_2_targetB="{PLAYER_NAME}"/><timer uid="#timer*9999999" x="310" y="-10" enabled="true" maxcalls="1" target="#trigger*9999999" delay="0" />'

xml_data.append(player_data_xml)

def number_to_letters(n): # more sophisticated base-52 numbering method for shorter id names
    characters = [chr(i) for i in range(ord('a'), ord('z')+1)] + [chr(i) for i in range(ord('A'), ord('Z')+1)]
    base = len(characters)
    result = ''
    
    while n > 0:
        n -= 1  # Adjust to 0-based indexing
        result = characters[n % base] + result
        n //= base
    
    return result

# Iterate through the grid
uid = 1  # Start UID for each movable (door)
trigger_uid = 1
for i in range(height_pixels):
    for j in range(width_pixels):
        # Calculate the x and y position for each movable
        x = j * config.PIXEL_SIZE + x_offset
        y = i * config.PIXEL_SIZE + y_offset
        
        # Create the XML element for the movable
        xml_element = f'<door uid="#*{number_to_letters(uid)}" x="{x}" y="{y}" w="{config.PIXEL_SIZE}" h="{config.PIXEL_SIZE}" tarx="0" tary="0" vis="true"/>'
        
        # Create 2 triggers per pixel, the first one turns it white, the second one turns it black
        pixel_trigger_list_white = [f'actions_1_type="71" actions_1_targetA="#*{number_to_letters(uid)}" actions_1_targetB="#FFFFFF"']
        pixel_trigger_list_black = [f'actions_1_type="71" actions_1_targetA="#*{number_to_letters(uid)}" actions_1_targetB="#0"']
        
        white_trigger_actions = " ".join(pixel_trigger_list_white)
        black_trigger_actions = " ".join(pixel_trigger_list_black)

        white_trigger_element = f'<trigger uid="#{number_to_letters(trigger_uid)}" enabled="true" maxcalls="-1" {white_trigger_actions}/>'
        black_trigger_element = f'<trigger uid="#{number_to_letters(trigger_uid + 1)}" enabled="true" maxcalls="-1" {black_trigger_actions}/>'

        xml_data.append(xml_element)
        xml_data.append(white_trigger_element)
        xml_data.append(black_trigger_element)

        trigger_uid += 2
        uid += 1  # Increment UID for the next movable

# Write to an XML file
with open(f'{FILE_NAME}', 'w') as file:
    file.write(''.join(xml_data))


## STEP 2, add frame logic and call the triggers with timers IF necessary


def clean_content(data):
    data = data.replace("\n", " ")
    data = data.split(" ")
    data.remove('')
    return data

# Path to the pixel_categorized_frames folder
output_folder = 'pixel_categorized_frames'

# After creating the pixels start the animation cycle
frame_data_files = [file for file in os.listdir(output_folder) if file.endswith('.txt')]

timer_data_xml = []

# timer values to sync framerate in PB2 with 30fps actual framerate
timer_delay_delta = (30//config.FRAME_RATE)
timer_delay_value = timer_delay_delta # initial wait time

# uid values will be incremented after every timer has been placed
uid = 1

# keeping track of previous frame to avoid changing pixels when not needed (saves data)
old_frames_list = [0] * config.ASPECT_RATIO_WIDTH * config.ASPECT_RATIO_HEIGHT

for frame in range(len(frame_data_files)): # start reading data from every frame 

    frame_data_content = None

    with open(f"{output_folder}/{frame_data_files[frame]}", "r") as content:
        frame_data_content = content.read()
    
    frame_data_content = clean_content(frame_data_content)  # list of binary data [1, 0]

    for i in range(len(frame_data_content)):
        # Only create timer_element if the pixel value changed from the old frame
        if frame_data_content[i] != old_frames_list[i]:
            if frame_data_content[i] == "1":  # Make it white
                timer_element = f'<timer enabled="true" maxcalls="1" target="#{number_to_letters((i+1)*2-1)}" delay="{timer_delay_value}"/>'
            else:  # Make it black
                timer_element = f'<timer enabled="true" maxcalls="1" target="#{number_to_letters((i+1)*2)}" delay="{timer_delay_value}"/>'
            
            # Append the timer element only when there's a change
            timer_data_xml.append(timer_element)

            # increment the uid to make sure the ids are unique
            uid += 1

    # Increase the timer delay to maintain the 30 FPS rate
    timer_delay_value += timer_delay_delta

    # copy the data from the last frame to be able to compare them with the next
    old_frames_list = frame_data_content.copy()


# append all changes made.

# Write to an XML file
with open(f'{FILE_NAME}', 'a') as file:
    file.write(''.join(timer_data_xml))

print(f"Map {FILE_NAME} created successfully.")
