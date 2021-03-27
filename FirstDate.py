from djitellopy import Tello
import cv2
from time import sleep

drone = Tello()
drone.connect() # Connect is used to send the initial connection request to the drone

print(drone.get_battery())

drone.streamoff()
drone.streamon()

while True:
    # Getting image from drone
    frame = drone.get_frame_read().frame
    img = cv2.resize(frame, (480, 360))
    cv2.imshow("Tello", img)
    cv2.waitKey(1)

    drone.takeoff()
    print("Taking off...")
    sleep(5)
    drone.rotate_clockwise(30)
    print("Rotating clockwise...")
    sleep(5)
    drone.move_forward(20)
    print("Going forward...")
    drone.land()
    print("It's enough, I'm landing!")
    sleep(20)

    # If something went wrong, press the 'q' button to Land the drone
    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break

