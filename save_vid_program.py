import subprocess
import argparse
import os

def run_your_program(source_vid, yolo_model, imgsz, roi, conf, iou_conf):
    # Example command: python 9-track-master.py --source_vid <source_vid> --yolo_model <yolo_model> --imgsz <imgsz> --roi <roi> --conf <conf> --iou_conf <iou_conf>
    command = [
        'python',
        '9-track-master.py',
        '--source',
        str(source_vid.rstrip('\n')),
        '--yolo_model',
        str(yolo_model),
        '--roi',
        str(roi),
        '--conf_thres',
        str(conf),
        '--iou_thres',
        str(iou_conf),
        '--save_vid',
        'True'
    ]

    try:
        # Run the subprocess
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Description of your script.')
    parser.add_argument('--input_file', help='Path to the input file containing parameters', required=True)
    args = parser.parse_args()

    source_vid = None  # Initialize source_vid outside the loop

    with open(args.input_file, 'r') as file:
        for line in file:
            
            if any(video_format in line.lower() for video_format in ['.mp4', '.avi', '.mkv']):
                source_vid = line
                # Add your code for handling video lines here
                continue  # Skip the rest of the code in this iteration and move to the next iteration

            
               
            else:
                model, imgsize, roi, conf, iou_conf = line.strip().split()

                print(model, imgsize, roi, conf, iou_conf)
                imgsize = int(imgsize.strip('[]'))
                
                roi = float(roi)
                iou_conf = float(iou_conf)
                run_your_program(source_vid, model, imgsize, roi, conf, iou_conf)

if __name__ == '__main__':
    main()
