#Importing Libraries

import cv2
import dlib
import time
import math
import sys

#Classifier File
carCascade = cv2.CascadeClassifier("vech.xml")

# Constant Declaration - Balanced optimization for accuracy
WIDTH = 640  # Back to 640 for better detection
HEIGHT = 480  # Back to 480 for better detection
DETECTION_INTERVAL = 20  # More frequent detection for accuracy
MAX_TRACKERS = 8  # Allow more trackers
FRAME_SKIP = 1  # Process every frame for accuracy
MAX_FRAMES = 1000  # Allow more frames

#estimate speed function
def estimateSpeed(location1, location2):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    ppm = 8.8
    d_meters = d_pixels / ppm
    fps = 18
    speed = d_meters * fps * 3.6
    return speed

#tracking multiple objects
def trackMultipleObjects(input_video_path, output_video_path):
    #Video file capture
    video = cv2.VideoCapture(input_video_path)
    
    rectangleColor = (0, 255, 255)
    frameCounter = 0
    currentCarID = 0
    fps = 0

    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (WIDTH, HEIGHT))

    # Get video properties for progress estimation
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    
    while True:
        start_time = time.time()
        rc, image = video.read()
        if type(image) == type(None):
            break
            
        # Frame skipping disabled for accuracy
        # if frameCounter % FRAME_SKIP != 0:
        #     frameCounter += 1
        #     continue
            
        # Early termination for very long videos
        if frameCounter >= MAX_FRAMES:
            break

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()

        frameCounter = frameCounter + 1
        carIDtoDelete = []

        # Create a copy of keys to avoid RuntimeError when modifying dictionary during iteration
        for carID in list(carTracker.keys()):
            try:
                trackingQuality = carTracker[carID].update(image)

                if trackingQuality < 7:
                    carIDtoDelete.append(carID)
            except Exception as e:
                # Remove problematic tracker
                carIDtoDelete.append(carID)
                continue

        
        # Remove debug print statements for better performance
        # for carID in carIDtoDelete:
        #     print("Removing carID " + str(carID) + ' from list of trackers. ')
        #     print("Removing carID " + str(carID) + ' previous location. ')
        #     print("Removing carID " + str(carID) + ' current location. ')
        for carID in carIDtoDelete:
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        
        if not (frameCounter % DETECTION_INTERVAL):
            # Optimized cascade detection with balanced parameters
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Better detection parameters for accuracy
            cars = carCascade.detectMultiScale(gray, 1.05, 10, 18, (20, 20))

            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                # Limit number of trackers to prevent performance issues
                if len(carTracker) >= MAX_TRACKERS:
                    continue
                    
                matchCarID = None

                # Create a copy of keys to avoid RuntimeError when modifying dictionary during iteration
                for carID in list(carTracker.keys()):
                    trackedPosition = carTracker[carID].get_position()

                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID

                if matchCarID is None:
                    # Remove debug print for better performance
                # print(' Creating new tracker' + str(currentCarID))

                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1

        # Create a copy of keys to avoid RuntimeError when modifying dictionary during iteration
        for carID in list(carTracker.keys()):
            trackedPosition = carTracker[carID].get_position()

            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())

            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)

            carLocation2[carID] = [t_x, t_y, t_w, t_h]

        end_time = time.time()

        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)

        # Only calculate speed every 3 frames for better accuracy
        if frameCounter % 3 == 0:
            for i in list(carLocation1.keys()):
                if i in carLocation2:
                    [x1, y1, w1, h1] = carLocation1[i]
                    [x2, y2, w2, h2] = carLocation2[i]

                    carLocation1[i] = [x2, y2, w2, h2]

                    if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                        # Calculate speed for any movement, not just specific y range
                        if speed[i] == None or speed[i] == 0:
                            speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])

                        # Show speed for any detected vehicle with speed
                        if speed[i] != None and speed[i] > 0:
                            cv2.putText(resultImage, str(int(speed[i])) + "km/h", (int(x1 + w1/2), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0) ,2)

        # Progress reporting with detailed frame count
        processed_frames += 1
        if processed_frames % 25 == 0:
            progress = min((processed_frames / min(total_frames, MAX_FRAMES)) * 80 + 10, 90)
            print(f"PROGRESS:{processed_frames}/{total_frames}")

        out.write(resultImage)

        # Commented out waitKey to prevent blocking when running in background
        # if cv2.waitKey(1) == 27:
        #     break

    
    # Commented out destroyAllWindows since we're not showing any windows
    # cv2.destroyAllWindows()
    out.release()

if __name__ == '__main__':
    # Check if command line arguments are provided
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        trackMultipleObjects(input_path, output_path)
    else:
        # Use default values for backward compatibility
        trackMultipleObjects("carsVideo.mp4", "outTraffic.avi")
