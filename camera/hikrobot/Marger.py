import os
import cv2
import glob
import shutil
import threading

def merge_images(image_paths, output_path, rotate=True):
    imgs = [cv2.imread(img_path) for img_path in image_paths]
    if rotate:
        imgs = [cv2.rotate(i, cv2.ROTATE_90_COUNTERCLOCKWISE) for i in imgs]

    result_image = None
    for img in imgs:
        if result_image is None:
            result_image = img
        else:
            result_image = cv2.hconcat([result_image, img])

    cv2.imwrite(output_path, result_image)
    return result_image

def merge_thread_images(
        output_frame: str, 
        output_saved: str, 
        filename: str, 
        position_camera: str,
        fps: int = None, 
        delay: int = None,
        num_threads : int = 4
    ):

    list_output_frame = sorted(glob.glob(os.path.join(output_frame+'/*.jpg')))
    # remove latest frame 
    if fps and delay:
        list_output_frame = list_output_frame[
            0:len(list_output_frame)-(delay*fps)
        ]

    # Calculate paths per thread
    paths_per_thread = len(list_output_frame) // num_threads


    # Create and start threads
    threads = []
    for i in range(num_threads):
        start_idx = i * paths_per_thread
        end_idx = start_idx + paths_per_thread if i < num_threads - 1 else len(list_output_frame)
        thread_paths = list_output_frame[start_idx:end_idx]
        
        thread = threading.Thread(target=merge_images, args=(thread_paths, f'{output_saved}/thread_{i}.jpg'))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    filename = f'{output_saved}/result_{filename}.jpg'
    thread_image_paths = [f'{output_saved}/thread_{i}.jpg' for i in range(num_threads)]

    result_image = merge_images(thread_image_paths, filename, rotate=False)
    if position_camera == 'right':
        result_image = cv2.flip(result_image, 1)
    cv2.imwrite(f'{filename}', result_image)

    # remove result thread
    [os.remove(i) for i in thread_image_paths]
    
    # remove file
    shutil.rmtree(output_frame)
    os.mkdir(output_frame)

    return filename