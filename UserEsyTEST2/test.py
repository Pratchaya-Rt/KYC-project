import requests
import os

url = 'http://localhost:5000/database'  # Replace with the appropriate URL

# Set the data for the request
data = {
    'id': 1,
    'status': 'your_status_value'
}

# Set the paths to the image files
image1_path = 'face-id/1.jpg'  # Replace 'image1.jpg' with the actual image file name
image2_path = 'face-id/2.jpg'  # Replace 'image2.jpg' with the actual image file name

# Open the image files
with open(image1_path, 'rb') as image1_file, open(image2_path, 'rb') as image2_file:
    # Set the files for the request
    files = {
        'image1': (image1_path, image1_file),
        'image2': (image2_path, image2_file)
    }

    # Send the POST request
    response = requests.post(url, data=data, files=files)

# Check the response status
if response.status_code == 200:
    print('Data saved successfully.')
else:
    print('Error occurred:', response.text)