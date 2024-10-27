from threading import Thread
import cv2
import time
import glob
import os
from emailing import send_email

# Initialize video capture from default camera (index 0)
video = cv2.VideoCapture(0)
# Give the camera a second to initialize
time.sleep(1)

# Variable to store the first frame for background subtraction
first_frame = None
# List to store the status of motion detection (0 for no motion, 1 for motion)
status_list = []
# Counter for image file names
count = 1


def clean_folder():
    """
    This function cleans up the 'images' folder by deleting all PNG files.
    """
    print(
        "clean_folder function started."
    )  # Indicate the start of the function
    images = glob.glob(
        "images/*.png"
    )  # Get a list of all PNG files in the 'images' folder
    for image in images:
        os.remove(image)  # Delete each image file
    print("clean_folder function ended.")  # Indicate the end of the function


# Main loop for continuous video processing
while True:
    status = 0  # Initialize motion status to 0 (no motion)
    check, frame = video.read()  # Read a frame from the video capture
    gray_frame = cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY
    )  # Convert the frame to grayscale
    gray_frame_gau = cv2.GaussianBlur(
        gray_frame, (21, 21), 0
    )  # Apply Gaussian blur for noise reduction

    # Capture the first frame as the background
    if first_frame is None:
        first_frame = gray_frame_gau

    delta_frame = cv2.absdiff(
        first_frame, gray_frame_gau
    )  # Calculate the absolute difference between the background and current frame
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[
        1
    ]  # Apply thresholding to create a binary image
    dil_frame = cv2.dilate(
        thresh_frame, None, iterations=2
    )  # Dilate the thresholded image to fill in gaps
    cv2.imshow(
        "My Video", dil_frame
    )  # Display the dilated frame (for debugging)

    contours, check = cv2.findContours(
        dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )  # Find contours of moving objects

    # Loop through detected contours
    for contour in contours:
        if cv2.contourArea(contour) < 5000:  # Ignore small contours (noise)
            continue
        x, y, w, h = cv2.boundingRect(
            contour
        )  # Get the bounding rectangle of the contour
        rectangle = cv2.rectangle(
            frame, (x, y), (x + w, y + h), (0, 255, 0), 3
        )  # Draw a rectangle around the moving object
        if rectangle.any():  # Check if a rectangle was drawn
            status = 1  # Set motion status to 1 (motion detected)
            cv2.imwrite(
                f"images/{count}.png", frame
            )  # Save the frame with the detected object
            count += 1  # Increment the image counter
            all_images = glob.glob(
                "images/*.png"
            )  # Get a list of all saved images
            index = int(
                len(all_images) / 2
            )  # Calculate the index of the middle image
            image_with_object = all_images[
                index
            ]  # Get the path to the middle image

    status_list.append(status)  # Add the current motion status to the list
    status_list = status_list[-2:]  # Keep only the last two status values

    # Check if motion has stopped (transition from 1 to 0)
    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(
            target=send_email, args=(image_with_object, )
        )  # Create a thread to send an email with the image
        email_thread.daemon = True  # Set the email thread as a daemon thread (runs in the background)
        clean_thread = Thread(
            target=clean_folder
        )  # Create a thread to clean the 'images' folder
        clean_thread.daemon = True  # Set the clean thread as a daemon thread

        email_thread.start()  # Start the email thread

    cv2.imshow("Video", frame)  # Display the video frame
    key = cv2.waitKey(1)  # Wait for 1 millisecond for a key press

    if key == ord("q"):  # Exit the loop if 'q' is pressed
        break

video.release()  # Release the video capture object
clean_thread.start()  # Start the clean thread after the loop ends