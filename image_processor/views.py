import json
import cv2
from django.http import HttpResponse
from PIL import Image
from pytesseract import Output
import numpy as np
import pytesseract
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from .models import UploadedImage, Destination
from decouple import config



def home_page(request):
    return render(request, 'index.html')


def map_view(request):
    
    secret_key = config('SECRET_KEY')
    return render(request, 'map.html', {'secret_key': secret_key})


@csrf_exempt 
def save_destination(request):
    if request.method == 'POST':
        stops = json.loads(request.body.decode('utf-8'))
        trip = Destination(
            stops=stops['stops'],
            total_distance=stops['totalDistance']
        )
        trip.save()
        return JsonResponse({'message': 'Trip saved successfully.'})
    return JsonResponse({'error': 'Invalid request method.'})


def download_pdf(request):
    trips = Destination.objects.all()  # Fetch saved trips from the database
    
    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trip_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    story = []

    # Define a style for the Paragraph
    style = getSampleStyleSheet()['Normal']
    style.wordWrap = 'CJK'

    # Create a Spacer for vertical separation
    vertical_space = Spacer(1, 20)

    for trip_number, trip in enumerate(trips, start=1):
        trip_info = []
        
        # Add trip stops information
        stops = trip.stops
        stops_info = [f"• {stop['display_name']}" for stop in stops]
        trip_info.append(Paragraph(f"<b>Trip {trip_number}:</b><br/>{'<br/>'.join(stops_info)}", style))

        # Add total distance
        trip_info.append(Paragraph(f"<b>Total distance:</b> {trip.total_distance} km", style))

        story.extend(trip_info)
        story.append(vertical_space)

    doc.build(story)

    return response
  

def find_dominant_angle(image_path):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    
    # Apply Hough Line Transform to detect lines
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
    
    if lines is not None:
        angles = [line[0][1] for line in lines]
        median_angle = np.median(angles) * 180 / np.pi - 90

        if median_angle > 45:
          median_angle = 90 
        elif median_angle > 25 :
           median_angle = median_angle + 120 #90
        elif median_angle > 0 and median_angle <=25:
          median_angle = median_angle 
        else:
          median_angle = median_angle + 90   
          
        # elif median_angle < -45:
        #     median_angle = 0
        # elif median_angle < 0:
        #     median_angle = 220 + median_angle
        return median_angle
    else:
        return None


def rotate_image(image_path, angle):
    # Load the image
    image = cv2.imread(image_path)
    
    # Calculate rotation matrix
    height, width = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), -angle, 1)
    
    # Rotate the image
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    
    return rotated_image


def process_image(request):
    
    if request.method == 'POST':
        imag = request.FILES['image']
        uploaded_image = UploadedImage.objects.create(image=imag)
        image = cv2.imread(uploaded_image.image.path)
        image_path = uploaded_image.image.path
        inclination_angle = find_dominant_angle(image_path)
        
        if inclination_angle is not None:
            print(f"Inclination Angle for {image_path}: {inclination_angle} degrees")
            rotated_image = rotate_image(image_path, -inclination_angle)
            
            # Convert the image to grayscale
            gray = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)
            binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(binary, kernel, iterations=1)
            # Preprocess the image (optional, but can help with OCR)
            preprocessed = cv2.GaussianBlur(gray, (5, 5), 1)
            custom_config = r'--oem 3 --psm 11 -l eng'
            text = pytesseract.image_to_string(dilated, config=custom_config, output_type=Output.STRING)

            title = [word for word in text.split() if len(word) > 3]
            print(title, "title")

            rotated_array = np.array(rotated_image)

            pil_image = Image.fromarray(rotated_array.astype(np.uint8))
            rotated_path = "rotated_image.jpg"
            pil_image.save(rotated_path)
            
            with open(rotated_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="image/jpeg")
            return response

        else:
            print(f"No lines detected in {image_path}.")

    return render(request, 'home_page.html')


