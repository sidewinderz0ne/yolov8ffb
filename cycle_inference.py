import argparse
import subprocess
import time
import psutil

def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False

def execute_script(args):
    # Your main script logic here (formerly track_master_main)
    print("9-track-master.py is running.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cycle Program")
    parser.add_argument('--yolo_model', type=str, default='./model/best.pt', help='model.pt path')
    parser.add_argument('--source', type=str, default='./video/Sampel Scm.mp4', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=1280, help='inference size h,w')
    parser.add_argument('--conf_thres', type=float, default=0.05, help='object confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--tracker', type=str, default='bytetrack.yaml', help='bytetrack.yaml or botsort.yaml')
    parser.add_argument('--roi', type=float, default=0.43, help='line height')
    # parser.add_argument('--show', type=bool, default=True, help='line height')
    parser.add_argument('--pull_data', type=str, default='-')
    parser.add_argument('--mode', type=str, default='sampling')
    # parser.add_argument('--save_vid', type=bool, default=False)
    # parser.add_argument("--debug", type=bool, default=False, help="Enable debug mode to store everything printed result into txt file")
    # parser.add_argument("--tiket", type=str, default='default', help="Enable debug mode to store everything printed result into txt file")
    cycle_args = parser.parse_args()

    process_name = "9-track-master.py"

    while True:
        if is_process_running(process_name):
            print(f"{process_name} is running.")
            execute_script(cycle_args)
        else:
            print(f"{process_name} is not running. Restarting...")

            subprocess_args = ["python", process_name]

            # Add each argument from cycle_args dynamically
            for arg_name, arg_value in vars(cycle_args).items():
                subprocess_args.extend([f"--{arg_name}", str(arg_value)])

            subprocess.run(subprocess_args)

        time.sleep(3)

