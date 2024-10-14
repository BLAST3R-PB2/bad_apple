import os
import config

FILE_NAME = "bad_apple_map.xml"

## STEP 1

pixel_size = 10  # Size of each movable
width_pixels = config.ASPECT_RATIO_WIDTH  # Number of pixels wide (4:3 aspect ratio)
height_pixels = config.ASPECT_RATIO_HEIGHT  # Number of pixels high (4:3 aspect ratio)

# Calculate the offset to center the grid on (0, 0)
x_offset = -(width_pixels // 2) * pixel_size
y_offset = -(height_pixels // 2) * pixel_size

# Start writing the XML data
xml_data = []

PLAYER_NAME = 'BLAST3R'

# player, camera, and concrete ground data
player_data_xml = f'<player uid="#player*1" x="270" y="170" tox="0" toy="0" hea="500" hmax="500" team="0" side="1" char="77" incar="-1" botaction="0" ondeath="-1" /><box x="-500" y="170" w="1100" h="1230" m="0" /><trigger uid="#trigger*9999999" x="310" y="20" enabled="true" maxcalls="1" actions_1_type="51" actions_1_targetA="120" actions_1_targetB="0" actions_2_type="-1" actions_2_targetA="0" actions_2_targetB="0" actions_3_type="52" actions_3_targetA="#player*1" actions_3_targetB="BLAST3R" actions_4_type="-1" actions_4_targetA="0" actions_4_targetB="0" actions_5_type="-1" actions_5_targetA="0" actions_5_targetB="0" actions_6_type="-1" actions_6_targetA="0" actions_6_targetB="0" actions_7_type="-1" actions_7_targetA="0" actions_7_targetB="0" actions_8_type="-1" actions_8_targetA="0" actions_8_targetB="0" actions_9_type="-1" actions_9_targetA="0" actions_9_targetB="0" actions_10_type="-1" actions_10_targetA="0" actions_10_targetB="0" /><timer uid="#timer*9999999" x="310" y="-10" enabled="true" maxcalls="1" target="#trigger*9999999" delay="0" />'

xml_data.append(player_data_xml)

# Create 2 triggers per pixel, the first one turns it white, the second one turns it black

# coords to start placing the triggers & timers
y_value = -700
x_value = -700

# Iterate through the grid
uid = 1  # Start UID for each movable (door)
trigger_uid = 1
for i in range(height_pixels):
    for j in range(width_pixels):
        # Calculate the x and y position for each movable
        x = j * pixel_size + x_offset
        y = i * pixel_size + y_offset
        
        # Create the XML element for the movable
        xml_element = f'<door uid="#door*{uid}" x="{x}" y="{y}" w="{pixel_size}" h="{pixel_size}" moving="false" tarx="0" tary="0" maxspeed="10" vis="true" attach="-1" />'
        pixel_trigger_list_white = [f'actions_1_type="71" actions_1_targetA="#door*{uid}" actions_1_targetB="#FFFFFF"']
        pixel_trigger_list_black = [f'actions_1_type="71" actions_1_targetA="#door*{uid}" actions_1_targetB="#000000"']

        for k in range(1, 10):
            pixel_trigger_list_white.append(f'actions_{k+1}_type="-1" actions_{k+1}_targetA="0" actions_{k+1}_targetB="0"')
            pixel_trigger_list_black.append(f'actions_{k+1}_type="-1" actions_{k+1}_targetA="0" actions_{k+1}_targetB="0"')
        
        white_trigger_actions = " ".join(pixel_trigger_list_white)
        black_trigger_actions = " ".join(pixel_trigger_list_black)

        white_trigger_element = f'<trigger uid="#trigger*{trigger_uid}" x="{x_value}" y="{y_value}" enabled="true" maxcalls="-1" {white_trigger_actions} />'
        black_trigger_element = f'<trigger uid="#trigger*{trigger_uid + 1}" x="{x_value - 50}" y="{y_value}" enabled="true" maxcalls="-1" {black_trigger_actions} />'

        xml_data.append(xml_element)
        xml_data.append(white_trigger_element)
        xml_data.append(black_trigger_element)

        y_value += 50

        trigger_uid += 2
        uid += 1  # Increment UID for the next movable
    
    x_value -= 100
    y_value = -700

# Write to an XML file
with open(f'{FILE_NAME}', 'w') as file:
    file.write('\n'.join(xml_data))


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
timer_delay_value = timer_delay_delta # initial wait is 10 sec (CHANGE THIS)

# coords to start placing the timers
y_value = -700
x_value = -4000

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
                timer_element = f'<timer uid="#timer*{uid}" x="{x_value}" y="{y_value}" enabled="true" maxcalls="1" target="#trigger*{(i+1)*2-1}" delay="{timer_delay_value}"/>'
            else:  # Make it black
                timer_element = f'<timer uid="#timer*{uid}" x="{x_value}" y="{y_value}" enabled="true" maxcalls="1" target="#trigger*{(i+1)*2}" delay="{timer_delay_value}"/>'
            
            # Append the timer element only when there's a change
            timer_data_xml.append(timer_element)

            # place the leading triggers below the trigger that came before
            y_value += 50

            # increment the uid to make sure the ids are unique
            uid += 1

    # Increase the timer delay to maintain the 30 FPS rate
    timer_delay_value += timer_delay_delta

    # copy the triggers from the last frame to be able to compare them with the next
    old_frames_list = frame_data_content

    # shift the triggers left per frame
    x_value -= 100
    y_value = -700


# append all changes made.

# Write to an XML file
with open(f'{FILE_NAME}', 'a') as file:
    file.write('\n'.join(timer_data_xml))

print(f"Map {FILE_NAME} created successfully.")
