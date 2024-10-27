# Import necessary libraries
import smtplib  # For sending emails
import os  # For interacting with the operating system (e.g., getting environment variables)
import imghdr  # For determining the image type
from email.message import EmailMessage  # For creating email messages

# Retrieve the email password from an environment variable
password = os.getenv("password")
# Set the sender and receiver email addresses
sender = "lordbeilish13@gmail.com"
receiver = "dkelnumero1@gmail.com"


def send_email(image_path):
    """
    Sends an email with an attached image.

    Args:
      image_path: The path to the image file to be attached.
    """
    print("send_email function started.")  # Indicate the start of the function

    # Create an email message object
    email_message = EmailMessage()
    email_message["Subject"] = (
        "New customer showed up!"  # Set the email subject
    )
    email_message.set_content(
        "Hey, we just saw a new customer!"
    )  # Set the email body

    # Open the image file in binary read mode
    with open(image_path, "rb") as file:
        content = file.read()  # Read the image content

    # Add the image as an attachment to the email
    email_message.add_attachment(
        content, maintype="image", subtype=imghdr.what(None, content)
    )

    # Connect to the Gmail SMTP server
    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()  # Identify yourself to the server
    gmail.starttls()  # Start TLS encryption for secure communication
    gmail.login(sender, password)  # Log in to the sender's email account
    gmail.sendmail(
        sender, receiver, email_message.as_string()
    )  # Send the email
    gmail.quit()  # Close the connection to the server
    print("send_email function ended.")  # Indicate the end of the function


# This block of code will only run if the script is executed directly (not imported as a module)
if __name__ == "__main__":
    send_email(
        image_path="images/19.png"
    )  # Call the send_email function with a sample image path