from ast import arg
import cv2
import os
import argparse
import datetime
import re
from datetime import datetime
from datetime import date
from pathlib import Path
# Global variable to store the coordinates of the click
click_coordinates = None
button_clicked = False  # Flag to indicate if the button is clicked
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')
ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'

def process_frame(frame, cctv_name):
    # Add your frame processing logic here
    # For example, you can apply some image processing filters
    # This is a placeholder, replace it with your actual processing code
    # processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Define the center and radius of the circular button
    width, height = 100, 100
    button_center = (1820, 100)
    radius = width // 2 - 5  # Leave a small border
    
    # Draw the button in the top right corner
    # cv2.circle(frame, button_center, radius, (0, 0, 255), -1)  # Red circle as a button
    # cv2.circle(frame, button_center, radius, (255, 255, 255), 5)

    # Add small text to the bottom left corner
    text = f"CCTV: {cctv_name}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5  # Adjust the font size as needed
    font_thickness = 1
    text_color = (255, 255, 255)  # White color
    text_position = (10, height - 20)  # Bottom left corner

    cv2.putText(frame, text, text_position, font, font_scale, text_color, font_thickness)

    return frame


def on_mouse_click(event, x, y, flags, param):
    global click_coordinates, button_clicked
    
    # Check if the left mouse button is clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        click_coordinates = (x, y)

        if x > 1720 and y < 200:
            button_clicked = True  # Set the flag to True


def contains_video_keywords(file_path):
    # Define a list of keywords that are commonly found in video file names
    video_keywords = ['avi', 'mp4', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']

    # Convert the file path to lowercase for case-insensitive matching
    file_path_lower = file_path.lower()

    # Check if any of the video keywords are present in the file path
    for keyword in video_keywords:
        if keyword in file_path_lower:
            return True

    return False

def main():
    global width, height  # Declare width and height as global variables
    
    # Argument parser setup
    parser = argparse.ArgumentParser(description='Process video frames and save the result as an MP4 file.')
    parser.add_argument('--source', default='./video/Sampel Scm.mp4', help='Path to the input video file.')
    parser.add_argument('--output', default='output_video.mp4', help='Path to the output MP4 file.')
    parser.add_argument('--tiket', type=str, default='main', help='Enable debug mode to store everything printed result into a txt file')
    args = parser.parse_args()

    file_directory = './hasil/' + formatted_date + '/' + args.tiket + '/'
    os.makedirs(file_directory, exist_ok=True)
    file_name = 'video_' + args.source + '.mp4'
    file_path = os.path.join(file_directory, file_name)

    ip_match = re.search(ip_pattern, args.source)

    if ip_match:
        extracted_ip = ip_match.group(1)
        stream = f'rtsp://admin:gr4d!ngs@{extracted_ip}/video'
    elif contains_video_keywords(args.source):
        stream = args.source
    else:
        stream = str(Path(os.getcwd() + '/video/Sampel Scm.mp4'))

    # Open the video file
    cap = cv2.VideoCapture(stream)

    # Get video properties
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = int(cap.get(5))


    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
    frame_name = 'Frame ' + args.source
    cv2.namedWindow(frame_name, cv2.WINDOW_NORMAL)  # WINDOW_NORMAL allows resizing
    # cv2.setMouseCallback(frame_name, on_mouse_click)

    # Set the window to full screen
    cv2.setWindowProperty(frame_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = process_frame(frame, args.source)

        out.write(processed_frame)

        # Display the processed frame (optional)
        cv2.imshow(frame_name, processed_frame)
        if button_clicked:
            break  # Break the loop if the button is clicked

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and writer objects
    cap.release()
    out.release()

    # Destroy any OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
