import os
import config

FILE_NAME = "bad_apple_map.xml"

## STEP 1

pixel_size = 20  # Size of each movable (20x20 pixels)
width_pixels = config.ASPECT_RATIO_WIDTH  # Number of pixels wide (4:3 aspect ratio)
height_pixels = config.ASPECT_RATIO_HEIGHT  # Number of pixels high (4:3 aspect ratio)

# Calculate the offset to center the grid on (0, 0)
x_offset = -(width_pixels // 2) * pixel_size
y_offset = -(height_pixels // 2) * pixel_size

# Start writing the XML data
xml_data = []

PLAYER_NAME = 'BLAST3R'

# player, camera, and concrete ground data
player_data_xml = f'<player uid="#player*1" x="300" y="170" tox="0" toy="0" hea="130" hmax="130" team="0" side="1" char="77" incar="-1" botaction="0" ondeath="-1" /><box x="-600" y="170" w="1200" h="430" m="0" /><region uid="#region*1" x="-370" y="-180" w="530" h="330" use_target="-1" use_on="0" /><trigger uid="#trigger*999999" x="330" y="-10" enabled="true" maxcalls="1" actions_1_type="245" actions_1_targetA="#region*1" actions_1_targetB="0.2" actions_2_type="51" actions_2_targetA="120" actions_2_targetB="0" actions_3_type="52" actions_3_targetA="#player*1" actions_3_targetB="{PLAYER_NAME}" actions_4_type="-1" actions_4_targetA="0" actions_4_targetB="0" actions_5_type="-1" actions_5_targetA="0" actions_5_targetB="0" actions_6_type="-1" actions_6_targetA="0" actions_6_targetB="0" actions_7_type="-1" actions_7_targetA="0" actions_7_targetB="0" actions_8_type="-1" actions_8_targetA="0" actions_8_targetB="0" actions_9_type="-1" actions_9_targetA="0" actions_9_targetB="0" actions_10_type="-1" actions_10_targetA="0" actions_10_targetB="0" /><timer uid="#timer*999999" x="330" y="-40" enabled="true" maxcalls="1" target="#trigger*999999" delay="0" />'

xml_data.append(player_data_xml)

# Iterate through the grid
uid = 1  # Start UID for each movable (door)
for i in range(height_pixels):
    for j in range(width_pixels):
        # Calculate the x and y position for each movable
        x = j * pixel_size + x_offset
        y = i * pixel_size + y_offset
        
        # Create the XML element for the movable
        xml_element = f'<door uid="#door*{uid}" x="{x}" y="{y}" w="{pixel_size}" h="{pixel_size}" moving="false" tarx="0" tary="0" maxspeed="10" vis="true" attach="-1" />'
        xml_data.append(xml_element)
        
        uid += 1  # Increment UID for the next movable

# Write to an XML file
with open(f'{FILE_NAME}', 'w') as file:
    file.write('\n'.join(xml_data))


## STEP 2

def clean_content(data):
    data = data.replace("\n", " ")
    data = data.split(" ")
    data.remove('')
    return data

# Path to the pixel_categorized_frames folder
output_folder = 'pixel_categorized_frames'

# After creating the pixels start the animation cycle
frame_data_files = [file for file in os.listdir(output_folder) if file.endswith('.txt')]

trigger_and_timer_data = []

# timer values to sync 5fps framerate in PB2 with 30fps actual framerate, 30fps/5fps = 6 timer delta value
timer_delay_delta = 6
timer_delay_value = timer_delay_delta

# coords to start placing the triggers & timers
y_value = -700
x_value = -700

# uid values will be incremented after every trigger/timer has been placed
uid = 1

# keeping track of old triggers to avoid changing pixels when not needed (saves data)
# this is a form of "delta encoding" in a sense
old_trigger_list = []

for frame in range(len(frame_data_files)): # start reading data from every frame

    frame_data_content = None

    with open(f"{output_folder}/{frame_data_files[frame]}", "r") as content:
        frame_data_content = content.read()
    
    frame_data_content = clean_content(frame_data_content) # list of binary data [1, 0]

    # A trigger has 10 actions, making it possible to control 10 pixels with a single trigger
    batch_size = 10

    trigger_list = []

    # Loop through the frame data in batches
    for i in range(0, len(frame_data_content), batch_size):
        # Create a trigger for this batch of 10 pixels (or fewer, if at the end)
        batch = frame_data_content[i:i + batch_size]

        # Initialize actions for this batch
        actions = []

        # Fill the action slots for the trigger (up to 10 actions)
        for j, pixel in enumerate(batch):
            # for every pixel in the batch, find its value (1=white, 0=black)
            # this value will be added to the trigger as the corresponding action
            trigger_target_value = "#FFFFFF" if pixel == "1" else "#000000"
            actions.append(f'actions_{j+1}_type="71" actions_{j+1}_targetA="#door*{i+j+1}" actions_{j+1}_targetB="{trigger_target_value}"')

        # Fill the remaining action slots with "-1" for unused slots
        for j in range(len(batch), 10):
            actions.append(f'actions_{j+1}_type="-1" actions_{j+1}_targetA="0" actions_{j+1}_targetB="0"')

        # Join the actions into a single string
        actions_str = " ".join(actions)

        # store the current list of trigger actions
        trigger_list.append(actions_str)

        # Create the trigger element
        trigger_element = f'<trigger uid="#trigger*{uid}" x="{x_value}" y="{y_value}" enabled="true" maxcalls="1" {actions_str} />'

        # Create the timer element
        timer_element = f'<timer uid="#timer*{uid}" x="{x_value-50}" y="{y_value}" enabled="true" maxcalls="1" target="#trigger*{uid}" delay="{timer_delay_value}"/>'

        # place the leading triggers below the trigger that came before
        y_value += 50

        # increment the uid to make sure the ids are unique
        uid += 1

        # first frame
        if len(old_trigger_list) == 0:
            # Append trigger and timer to the data list
            trigger_and_timer_data.append(trigger_element)
            trigger_and_timer_data.append(timer_element)
        
        else:
            # need an index between 0-43
            if old_trigger_list[i//batch_size] != trigger_list[i//batch_size]:
                # Append trigger and timer to the data list
                # this process happens only when the trigger is different, saving data/file size.
                trigger_and_timer_data.append(trigger_element)
                trigger_and_timer_data.append(timer_element)

    # Increase the timer delay to maintain the 30 FPS rate
    timer_delay_value += timer_delay_delta

    # copy the triggers from the last frame to be able to compare them with the next
    old_trigger_list = trigger_list.copy()

    # shift the triggers left per frame
    x_value -= 100
    y_value = -700


# append all changes made.

# Write to an XML file
with open(f'{FILE_NAME}', 'a') as file:
    file.write('\n'.join(trigger_and_timer_data))

print(f"Map {FILE_NAME} created successfully.")
