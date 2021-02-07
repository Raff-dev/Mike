import cv2


def capture(max_frames=int('inf')):
    video = cv2.VideoCapture(1)
    frame = 0
    image = None
    try:
        while cv2.waitKey(1) & 0xFF != ord('q') and (frame := frame+1) < max_frames:
            image and cv2.imshow('frame', image)
            _, image = video.capture()
            if image:
                yield image
    finally:
        video.release()
        cv2.destroyAllWindows()
