import cv2
import argparse
from numpy import ndarray
from camera.csi_camera import Camera


def parse_arguments():
    parser = argparse.ArgumentParser(description="Camera Configuration")
    parser.add_argument(
        "--device_id",
        type=int,
        default=1,
        help="Camera device ID (default: 1)",
    )
    return parser.parse_args()

args = parse_arguments()


# device_id 0 -> container number
# device_id 1 -> seal

camera = Camera(
	camera_type = 0,
	device_id = args.device_id,
	width = 1920,
	height = 1080,
	flip = 0,
	debug = 1
)

def resize_image(
		image: ndarray, 
		scale_percent: int = 50
	) -> ndarray:
	width = int(image.shape[1] * scale_percent / 100)
	height = int(image.shape[0] * scale_percent / 100)
	dim = (width, height)
	# resize image
	resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
	return resized

while True:
	frame = camera.read()
	frame =  cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
	image = resize_image(frame, 60)
	cv2.imshow('image', image)
 
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break
  
camera.release() 
cv2.destroyAllWindows() 