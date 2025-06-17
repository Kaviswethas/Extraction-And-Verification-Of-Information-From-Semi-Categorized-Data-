import random
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
import requests
import nltk
from django.conf import settings
import re
from concurrent.futures import ThreadPoolExecutor
from langdetect import detect  # For language detection
from googletrans import Translator  # For translation

import smtplib


HOST="smtp.gmail.com"
PORT=587

FROM_EMAIL="gokulnathramesh25@gmail.com"

TO_EMAIL=""

PASSWORD="jingtxqoyndtopya"

MESSAGE=""

# Load NLTK resources
nltk.download('punkt')

def index(request):
    return render(request, 'index.html')

def perform_ocr(image_file, api_key):
    """ Perform OCR on a single image file using an external API. """
    url = 'https://api.ocr.space/parse/image'  # Replace with your actual endpoint
    response = requests.post(url, files={'file': image_file}, data={'apikey': api_key, 'language': 'eng'})
    if response.status_code == 200:
        result = response.json()
        extracted_text = result.get("ParsedResults")[0].get("ParsedText")
        return extracted_text
    else:
        return None

def clean_and_tokenize(text):
    """ Clean text by removing special characters, lowering case, and splitting into words. """
    text = re.sub(r'[^\w\s]', '', text)
    return set(nltk.word_tokenize(text.lower()))

def detect_language(text):
    """ Detect the language of the given text using langdetect. """
    try:
        return detect(text)
    except:
        return 'en'  # Default to English if detection fails

def translate_text(text, target_language='en'):
    """ Translate the given text to the target language using googletrans. """
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except:
        return text  # If translation fails, return the original text
@csrf_exempt
def verify_form(request):
    if request.method == "POST":
        api_key = 'K81626268488957'  # Replace with your OCR.Space API key
        form_data = request.POST
        files = request.FILES
        response_data = {}

        # Step 1: Perform OCR for all uploaded files concurrently
        extracted_text = ""
        with ThreadPoolExecutor() as executor:
            ocr_results = list(executor.map(lambda file: perform_ocr(file, api_key), files.values()))
        # Combine all OCR results into one text
        extracted_text = " ".join([ocr_text for ocr_text in ocr_results if ocr_text])

        # Step 2: Detect language of extracted OCR text
        ocr_language = detect_language(extracted_text)
        print(f"OCR Language Detected: {ocr_language}")

        # If OCR language is not English, translate it to English
        if ocr_language != 'en':
            extracted_text = translate_text(extracted_text)

        # Clean and tokenize the extracted OCR text
        ocr_tokens = clean_and_tokenize(extracted_text)

        # Step 3: Check each form field against the OCR tokens for any matching words
        for field_name, field_value in form_data.items():
            # Detect the language of the field value
            field_language = detect_language(field_value)
            print(f"Field '{field_name}' Language Detected: {field_language}")

            # If the field language is not English, translate it to English
            if field_language != 'en':
                field_value = translate_text(field_value)

            # Clean and tokenize the form field value
            field_tokens = clean_and_tokenize(field_value)

            # Find if there is any common word between the OCR text and field input
            match_found = any(word in ocr_tokens for word in field_tokens)
            response_data[field_name] = match_found
            print(f"{field_name} : {match_found}")
            print(extracted_text)

        return JsonResponse(response_data)

import json
import smtplib
from django.shortcuts import render, redirect
from django.contrib import messages

# SMTP Configuration
HOST = "smtp.gmail.com"
PORT = 587
FROM_EMAIL = "gokulnathramesh25@gmail.com"
EMAIL_PASSWORD = "jingtxqoyndtopya"

def send_email(to_email, subject, body):
    try:
        with smtplib.SMTP(HOST, PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(FROM_EMAIL, to_email, message)
    except Exception as e:
        print(f"Error sending email: {e}")

def login(request):
    # Path to the JSON file
    import os
    json_file_path = os.path.join(os.path.dirname(__file__), '../data.json')

    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()
        forgot_password = request.POST.get('forgot-password', '').strip()

        # Load data from JSON
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            messages.error(request, "User database not found.")
            return render(request, 'login.html')

        users = data.get("register", [])
        # Forgot Password functionality
        if forgot_password:
            user = next((user for user in users if user["user_mail"] == email), None)
            if user:
                subject = "Forgot Password Assistance"
                body = (
                    f"Hi {user['user_name']},\n\n"
                    f"Here are your account details:\n"
                    f"User ID: {user['user_id']}\n"
                    f"Email: {user['user_mail']}\n"
                    f"Username: {user['user_name']}\n"
                    f"Password: {user['user_password']}\n\n"
                    "Best Regards,\nRAC Team"
                )
                try:
                    send_email(email, subject, body)
                    messages.success(request, "Account details have been sent to your email.")
                except Exception as e:
                    messages.warning(request, f"Unable to send email: {e}")
            else:
                messages.error(request, "Email not found.")
            return render(request, 'login.html')

        # Login Validation
        user = next((user for user in users if user["user_mail"] == email and user["user_password"] == password), None)
        if user:
            request.session['user'] = user 
            messages.success(request, f"Welcome {user['user_name']}!")
            user_name=user["user_name"]
            request.session["user_name"]=user_name
            user_mail=user["user_mail"]
            request.session["user_mail"]=user_mail
            return render(request,'user_dashboard.html',context={'user_name':user_name,'user_mail':user_mail})  # Redirect to dashboard
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, 'login.html')
    return render(request, 'login.html')

import json
import uuid
import smtplib
from django.shortcuts import render, redirect
from django.contrib import messages

HOST = "smtp.gmail.com"
PORT = 587
FROM_EMAIL = "gokulnathramesh25@gmail.com"
EMAIL_PASSWORD = "jingtxqoyndtopya"

def send_email(to_email, subject, body):
    try:
        with smtplib.SMTP(HOST, PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(FROM_EMAIL, to_email, message)
    except Exception as e:
        print(f"Error sending email: {e}")

def register(request):
    import os
    json_file_path = os.path.join(os.path.dirname(__file__), '../data.json')
    
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirm-password').strip()
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"register": []}  

        existing_users = data.get("register", [])
        if any(user["user_mail"] == email for user in existing_users):
            messages.error(request, "Email already exists.")
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        new_user = {
            "user_id": str(uuid.uuid4()),
            "user_mail": email,
            "user_name": username,
            "user_password": password,
        }
        data["register"].append(new_user)
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

        subject = "Registration Acknowledgment"
        body = (
            f"Hi {username},\n\n"
            "Thank you for registering at RAC. Here are your registration details:\n"
            f"User ID: {new_user['user_id']}\n"
            f"Email: {email}\n"
            f"Username: {username}\n\n"
            f"Password: {password}\n\n"
            "Best Regards,\nRAC Team"
        )
        try:
            send_email(email, subject, body)
            messages.success(request, "Registration successful. A confirmation email has been sent.")
        except Exception as e:
            messages.warning(request, f"Registration successful, but email could not be sent: {e}")

        return redirect('login')
    return render(request, 'register.html')

def user_dashboard(request):
    return render(request,'user_dashboard.html',{'Username':request.session.get('user_name')})

def user_logout(request):
    if 'user_name' in request.session:
        del request.session['user']
    request.session.flush()  
    return redirect('login')  

import json
import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def submit_application_form(request):
    if request.method == 'POST':
        try:
            json_file_path = os.path.join(os.path.dirname(__file__), '../data.json')

            # Load existing data
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as file:
                    data = json.load(file)
            else:
                data = {"application_form": []}

            # Generate a unique user ID (if not already provided)
            user_id = str(uuid.uuid4())

            # Create a directory for the user in the uploads folder
            user_uploads_path = os.path.join(settings.MEDIA_ROOT, 'uploads', user_id)
            os.makedirs(user_uploads_path, exist_ok=True)

            # Extract form data and files
            form_data = {
                "candidate_name": request.POST.get('candidate_name'),
                "father_name": request.POST.get('father_name'),
                "mother_name": request.POST.get('mother_name'),
                "dob": request.POST.get('dob'),
                "gender": request.POST.get('gender'),
                "email": request.POST.get('email'),
                "contact": request.POST.get('contact'),
                "religion": request.POST.get('religion'),
                "nationality": request.POST.get('nationality'),
                "present_address": request.POST.get('present_address'),
                
                "permanent_address": request.POST.get('permanent_address'),
                "city": request.POST.get('city'),
                "state": request.POST.get('state'),
                "sslc": request.POST.get('sslc'),
                "board": request.POST.get('board'),
                "year_passing": request.POST.get('year_passing'),
                "percentage": request.POST.get('percentage'),
                "aadhaar": request.POST.get('aadhaar'),
                "gate_reg": request.POST.get('gate_reg'),
                "gate_year": request.POST.get('gate_year'),
                "gate_score": request.POST.get('gate_score'),
                "pwd": request.POST.get('pwd'),
                "disability_type": request.POST.get('disability_type'),
                "disability_cert_no": request.POST.get('disability_cert_no'),
                "user_id": user_id  # Store user_id in the form data
            }

            # Handle file uploads and save file paths
            file_paths = []
            for key, value in request.FILES.items():
                # Save the file in the user's folder
                file_path = os.path.join(user_uploads_path, value.name)
                with open(file_path, 'wb') as f:
                    for chunk in value.chunks():
                        f.write(chunk)
                file_paths.append(file_path)

            # Add file paths to form data
            form_data["file_paths"] = file_paths

            # Add new form data to application_form
            data['application_form'].append(form_data)

            # Save back to JSON
            with open(json_file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return JsonResponse({"success": True, "message": "Application form submitted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


def success(request):
    return render(request,'success.html')

import json
from pathlib import Path
from django.shortcuts import render, redirect

# Path to your data.json file
DATA_FILE = Path(__file__).resolve().parent.parent / 'data.json'

def sa_login(request):
    """Handles the Super Admin login."""
    error = None

    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST.get('sa_username')
        password = request.POST.get('sa_password')

        # Read data from data.json
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)

        # Get the super_admin credentials
        super_admin = data.get('super_admin', [])

        # Check if the credentials match
        if any(admin['username'] == username and admin['password'] == password for admin in super_admin):
            # Save the user in the session
            request.session['sa_logged_in'] = True
            request.session['sa_username'] = username
            # Redirect to the dashboard on successful login
            return redirect('sa_dashboard')  # Replace with your actual dashboard URL name
        else:
            # Set error message for invalid credentials
            error = "Invalid credentials. Please try again."

    # Render the login page with an error message (if any)
    return render(request, 'sa_login.html', {'error': error})


def sa_dashboard(request):
    """Super Admin Dashboard."""
    # Check if the user is logged in
    if not request.session.get('sa_logged_in'):
        return redirect('sa_login')  # Redirect to login if session is not active

    # Render the dashboard
    return render(request, 'sa_dashboard.html', {'username': request.session.get('sa_username')})


def sa_logout(request):
    """Logs out the Super Admin."""
    # Clear the session
    request.session.flush()
    # Redirect to the login page
    return redirect('sa_login')

import json
from pathlib import Path
from django.shortcuts import render, redirect

# Path to your data.json file
DATA_FILE = 'data.json'

import json
import smtplib
import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Email Configuration
HOST = "smtp.gmail.com"
PORT = 587
FROM_EMAIL = "gokulnathramesh25@gmail.com"
PASSWORD = "jingtxqoyndtopya"

def create_admin(request):
    # Check if the user is logged in
    if not request.session.get('sa_logged_in'):
        return redirect('sa_login')  # Redirect to login if session is not active

    # Path to JSON file
    json_file = 'data.json'

    if request.method == 'POST':
        # Retrieve data from the form
        admin_name = request.POST.get('name')
        admin_email = request.POST.get('email')
        admin_password = request.POST.get('password')
        admin_contact = request.POST.get('contact_number')

        # Load existing data from JSON file
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"admin_details": []}

        # Check if email already exists
        for admin in data.get('admin_details', []):
            if admin['admin_mail'] == admin_email:
                return JsonResponse({'error': 'Email already exists!'}, status=400)

        # Generate a unique admin_id using uuid
        admin_id = str(uuid.uuid4())

        # Add new admin to the data with a unique admin_id
        new_admin = {
            "admin_id": admin_id,
            "admin_name": admin_name,
            "admin_mail": admin_email,
            "admin_password": admin_password,
            "admin_contact": admin_contact
        }
        data['admin_details'].append(new_admin)

        # Save data back to JSON
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

        # Send email to the new admin
        try:
            smtp = smtplib.SMTP(HOST, PORT)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(FROM_EMAIL, PASSWORD)

            # Create message
            message = f"""Subject: RAC ADMIN CREDENTIALS

Hi {admin_name},

Your credentials are:
Admin Name: {admin_name}
Admin Email: {admin_email}
Admin Password: {admin_password}
Admin Contact: {admin_contact}

Regards,
RAC Support Team
"""
            smtp.sendmail(FROM_EMAIL, admin_email, message)
            smtp.quit()
        except Exception as e:
            return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)

        # Return success response
        return render(request,'create_admin.html',{'username': request.session.get('sa_username')})

    return render(request, 'create_admin.html', {'username': request.session.get('sa_username')})

import json
import smtplib
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Email Configuration
HOST = "smtp.gmail.com"
PORT = 587
FROM_EMAIL = "gokulnathramesh25@gmail.com"
PASSWORD = "jingtxqoyndtopya"

def update_admin(request):
    # Check if the user is logged in
    if not request.session.get('sa_logged_in'):
        return redirect('sa_login')  # Redirect to login if session is not active

    # Path to JSON file
    json_file = 'data.json'

    if request.method == 'POST':
        # Get the updated admin details from the form
        admin_id = request.POST.get('admin_id')
        admin_name = request.POST.get('name')
        admin_email = request.POST.get('email')
        admin_contact = request.POST.get('contact')
        admin_password = request.POST.get('password')

        # Load the existing admin details from the JSON file
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"admin_details": []}

        # Find the admin by admin_id and update their details
        updated = False
        for admin in data.get('admin_details', []):
            if admin['admin_id'] == admin_id:
                admin['admin_name'] = admin_name
                admin['admin_mail'] = admin_email
                admin['admin_contact'] = admin_contact
                if admin_password:
                    admin['admin_password'] = admin_password
                updated = True
                break

        if updated:
            # Save the updated admin data back to the JSON file
            with open(json_file, 'w') as file:
                json.dump(data, file, indent=4)

            # Send updated credentials email
            try:
                smtp = smtplib.SMTP(HOST, PORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.login(FROM_EMAIL, PASSWORD)

                # Create message for updated credentials
                message = f"""Subject: Updated RAC Admin Credentials

Hi {admin_name},

Your credentials have been updated:
Admin Name: {admin_name}
Admin Email: {admin_email}
Admin Contact: {admin_contact}
Admin Password: {admin_password if admin_password else "No password change"}

Regards,
RAC Support Team
"""
                smtp.sendmail(FROM_EMAIL, admin_email, message)
                smtp.quit()

            except Exception as e:
                return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)

            return render(request, 'update_admin.html', {
        'username': request.session.get('sa_username'),
        'admins': data.get('admin_details', [])
    })
        else:
            return JsonResponse({'error': 'Admin not found!'}, status=404)

    # Load existing admin details to display in the form
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"admin_details": []}

    # Pass the admin details to the template for rendering
    return render(request, 'update_admin.html', {
        'username': request.session.get('sa_username'),
        'admins': data.get('admin_details', [])
    })

import json
from django.shortcuts import render, redirect
import os

def delete_admin(request):
    # Check if the user is logged in
    if not request.session.get('sa_logged_in'):
        return redirect('sa_login')  # Redirect to login if session is not active

    # Path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), '../../drdo/data.json')

    # Load existing admin data from JSON
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    admins = data.get('admin_details', [])

    # Handle form submission for deletion
    if request.method == 'POST':
        delete_id = request.POST.get('delete_id')
        # Ensure `delete_id` is not None
        if delete_id:
            admins = [admin for admin in admins if admin['admin_id'] != delete_id]  # Corrected key name

            # Save updated data back to JSON
            data['admin_details'] = admins
            with open(json_file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return redirect('delete_admin')  # Reload the page after deletion

    return render(request, 'delete_admin.html', {
        'username': request.session.get('sa_username'),
        'admins': admins
    })

from django.shortcuts import render, redirect
import json
from datetime import datetime
import pytz

def view_reports(request):
    """Super Admin Dashboard."""
    # Check if the user is logged in
    if not request.session.get('sa_logged_in'):
        return redirect('sa_login')  # Redirect to login if session is not active
    
    # Load the data from the JSON file
    with open('data.json', 'r') as file:
        data = json.load(file)

    # Get the reports data
    reports = data.get('reports', [])
    
    # Timezone setup
    ist = pytz.timezone('Asia/Kolkata')

    # Check and convert the timestamp to IST
    for report in reports:
        timestamp = report.get('timestamp')
        if timestamp:
            # Try to parse the timestamp and handle the timezone conversion
            try:
                # Convert timestamp string to a datetime object
                timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                
                # Assuming the timestamp is in UTC or without timezone info, convert it to IST
                if timestamp_dt.tzinfo is None:  # If no timezone is set
                    utc_time = pytz.utc.localize(timestamp_dt)  # Localize to UTC first
                else:
                    # If the timestamp has a timezone, convert to IST
                    utc_time = timestamp_dt.astimezone(pytz.utc)
                
                # Convert to IST
                ist_time = utc_time.astimezone(ist)
                report['timestamp'] = ist_time.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # In case the timestamp format is incorrect, skip it
                report['timestamp'] = "Invalid Timestamp"
    
    # Sort the reports in descending order by timestamp
    reports = sorted(reports, key=lambda x: x['timestamp'], reverse=True)
    
    # Render the reports
    return render(request, 'view_reports.html', {'username': request.session.get('sa_username'), 'reports': reports})

import json
from django.shortcuts import render, redirect
from django.contrib import messages

# Load JSON file
def load_json_data():
    json_path = os.path.join(settings.BASE_DIR, 'data.json')
    with open(json_path, 'r') as file:
        return json.load(file)

# Admin login view
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('admin_password')

        # Load JSON data
        data = load_json_data()
        admin_details = data.get('admin_details', [])

        # Validate credentials
        for admin in admin_details:
            if admin['admin_name'] == username and admin['admin_password'] == password:
                # Store admin details in session
                request.session['admin_id'] = admin['admin_id']
                request.session['admin_name'] = admin['admin_name']
                return redirect('admin_dashboard')  # Redirect to dashboard if successful
        
        # If credentials don't match, add error message
        messages.error(request, 'Invalid username or password.')
        return render(request, 'admin_login.html')
    
    return render(request, 'admin_login.html')

# Admin dashboard view
def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')  # Redirect to login if not authenticated
    return render(request, 'admin_dashboard.html')

import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from io import BytesIO
from reportlab.pdfgen import canvas

# Path to your data.json
# DATA_FILE = "../data.json"

# def load_data():
#     with open(DATA_FILE, "r") as file:
#         return json.load(file)

# def save_data(data):
#     with open(DATA_FILE, "w") as file:
#         json.dump(data, file, indent=4)

def view_applicants(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')  # Redirect to login if not authenticated

    # Read the JSON data from the file located in BASE_DIR
    data_file_path = os.path.join(settings.BASE_DIR, 'data.json')
    
    with open(data_file_path, 'r') as file:
        data = json.load(file)
    
    # Get the application form data
    applicants = data['application_form']
    
    context = {'applicants': applicants}
    return render(request, 'view_applicants.html', context)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
def download_pdf(request, user_id):
    # Read the JSON data from the file
    data_file_path = os.path.join(settings.BASE_DIR, 'data.json')
    
    with open(data_file_path, 'r') as file:
        data = json.load(file)
    
    # Find the specific applicant by user_id
    applicant = None
    for person in data['application_form']:
        if person['user_id'] == user_id:
            applicant = person
            break
    
    if not applicant:
        return HttpResponse("Applicant not found.", status=404)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="applicant_{user_id}.pdf"'
    
    # Create a PDF canvas with the letter page size
    pdf = canvas.Canvas(response, pagesize=letter)
    
    pdf.drawString(100, 750, f"Name: {applicant['candidate_name']}")
    pdf.drawString(100, 730, f"Father's Name: {applicant['father_name']}")
    pdf.drawString(100, 710, f"Mother's Name: {applicant['mother_name']}")
    pdf.drawString(100, 690, f"DOB: {applicant['dob']}")
    pdf.drawString(100, 670, f"Gender: {applicant['gender']}")
    pdf.drawString(100, 650, f"Email: {applicant['email']}")
    pdf.drawString(100, 630, f"Contact: {applicant['contact']}")
    pdf.drawString(100, 610, f"Religion: {applicant['religion']}")
    pdf.drawString(100, 590, f"Nationality: {applicant['nationality']}")
    pdf.drawString(100, 570, f"Present Address: {applicant['present_address']}")
    pdf.drawString(100, 550, f"Permanent Address: {applicant['permanent_address']}")
    pdf.drawString(100, 530, f"City: {applicant['city']}")
    pdf.drawString(100, 510, f"State: {applicant['state']}")
    pdf.drawString(100, 490, f"SSLC: {applicant['sslc']}")
    pdf.drawString(100, 470, f"Board: {applicant['board']}")
    pdf.drawString(100, 450, f"Year of Passing: {applicant['year_passing']}")
    pdf.drawString(100, 430, f"Percentage: {applicant['percentage']}")
    pdf.drawString(100, 410, f"Aadhaar: {applicant['aadhaar']}")
    pdf.drawString(100, 390, f"GATE Registration: {applicant['gate_reg']}")
    pdf.drawString(100, 370, f"GATE Year: {applicant['gate_year']}")
    pdf.drawString(100, 350, f"GATE Score: {applicant['gate_score']}")
    pdf.drawString(100, 330, f"PWD: {applicant['pwd']}")
    pdf.drawString(100, 310, f"Disability: {applicant['disability_type']}")
    pdf.drawString(100, 290, f"Disability Cert No: {applicant['disability_cert_no']}")

    pdf.showPage()
    pdf.save()

    return response

def block_applicant(request):
    if request.method == 'POST':
        # Get the user_id and reason for blocking
        user_id = request.POST.get('user_id')
        block_reason = request.POST.get('block_reason')
        
        # Read the data from JSON file
        data_file_path = os.path.join(settings.BASE_DIR, 'data.json')
        
        with open(data_file_path, 'r') as file:
            data = json.load(file)
        
        # Find the applicant and move them to the blocked list
        applicant_to_block = None
        for applicant in data['application_form']:
            if applicant['user_id'] == user_id:
                applicant_to_block = applicant
                break
        
        if applicant_to_block:
            # Add the applicant to the blocked list
            data['blocked'].append(applicant_to_block)
            data['application_form'].remove(applicant_to_block)
            
            # Update the block reason
            applicant_to_block['block_reason'] = block_reason

            # Save the updated data back to the file
            with open(data_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            return redirect('view_applicants')
        else:
            return HttpResponse("Applicant not found.", status=404)

    return redirect('view_applicants')

import json
import os
from django.conf import settings
from django.shortcuts import render, redirect

def applicant_queries(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')  # Redirect to login if not authenticated
    
    # Path to the JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'data.json')
    
    # Read the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract the contacts from the JSON
    contacts = data.get('contacts', [])
    
    # Pass the contacts data to the template
    return render(request, 'applicant_queries.html', {'contacts': contacts})

from django.http import JsonResponse
import json
import os
from django.conf import settings

def update_resolved_status(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            contact_name = request.POST.get('contact_name')
            resolved_status = request.POST.get('resolved_status')

            # Path to the JSON file
            json_file_path = os.path.join(settings.BASE_DIR, 'data.json')
            
            # Read the JSON data
            with open(json_file_path, 'r') as file:
                data = json.load(file)

            # Find the contact and update its resolved status
            contacts = data.get('contacts', [])
            for contact in contacts:
                if contact['name'] == contact_name:
                    contact['resolved'] = resolved_status

            # Write the updated data back to the JSON file
            with open(json_file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

from django.http import JsonResponse
import json
import os
from django.conf import settings

def get_contacts_data(request):
    try:
        # Path to the JSON file
        json_file_path = os.path.join(settings.BASE_DIR, 'data.json')

        # Read the JSON data
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

# Path to the JSON data file
data_file_path = settings.BASE_DIR / 'data.json'

def read_json_file():
    """Reads the JSON data from the file."""
    try:
        with open(data_file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return {}

def save_json_file(data):
    """Saves the modified data back to the JSON file."""
    try:
        with open(data_file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON file: {e}")

def blocked_applicants(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')  # Redirect to login if not authenticated
    
    data = read_json_file()  # Read the data from the JSON file
    blocked_applicants = data.get("blocked", [])

    if request.method == 'POST' and 'unblock' in request.POST:
        user_id_to_unblock = request.POST.get('user_id')
        # Remove from blocked list
        blocked_applicant = next((applicant for applicant in blocked_applicants if applicant['user_id'] == user_id_to_unblock), None)
        if blocked_applicant:
            blocked_applicants.remove(blocked_applicant)
            # Add to application_form
            data['application_form'].append(blocked_applicant)
            save_json_file(data)  # Save the updated data back to the file

            return redirect('blocked_applicants')  # Redirect after unblocking

    return render(request, 'blocked_applicants.html', {'blocked_applicants': blocked_applicants})

import json
from django.shortcuts import render, redirect

def unblock_candidate(request, user_id):
    # Get the file path to data.json (use os.path.join for cross-platform compatibility)
    data_file_path = settings.BASE_DIR / 'data.json'
    
    # Read the data from the JSON file
    with open(data_file_path, 'r') as file:
        data = json.load(file)
    
    # Find the blocked candidate to unblock
    blocked_candidate = None
    for candidate in data['blocked']:
        if candidate['user_id'] == user_id:
            blocked_candidate = candidate
            break
    
    if blocked_candidate:
        # Remove the candidate from the 'blocked' list
        data['blocked'].remove(blocked_candidate)
        
        # Remove the block_reason from the candidate's data
        candidate_data = blocked_candidate.copy()
        candidate_data.pop('block_reason', None)  # Remove the block_reason
        
        # Add the candidate to the 'application_form' list
        data['application_form'].append(candidate_data)
        
        # Write the updated data back to the JSON file
        with open(data_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        
        # Redirect to a page showing the updated applicants
        return redirect('blocked_applicants')  # Assuming this is the URL for blocked applicants
    else:
        # If the candidate was not found, redirect or show an error
        return redirect('blocked_applicants')  # Redirecting to the blocked applicants page

import json
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
import os

def add_reports(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')  # Redirect to login if not authenticated
    
    if request.method == 'POST':
        report_content = request.POST.get('report_content', '').strip()
        
        if report_content:
            # Get current admin's name from session
            admin_name = request.session.get('admin_name', 'Unknown Admin')

            # Get the current timestamp
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

            # Load data.json file
            data_file = os.path.join(settings.BASE_DIR, 'data.json')

            with open(data_file, 'r') as f:
                data = json.load(f)

            # Create new report entry
            new_report = {
                'admin_name': admin_name,
                'report': report_content,
                'timestamp': timestamp
            }

            # Append the new report to the reports array
            data['reports'].append(new_report)

            # Save the updated data back to data.json
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4)

            # Redirect to the same page or show a success message
            return redirect('add_reports')

    return render(request, 'add_reports.html')



def admin_logout(request):
    if 'admin_id' in request.session:
        request.session.flush()  # Clear all session data
        messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')  # Redirect to the login page

import json
from django.shortcuts import render

def contact(request):
    # Path to the JSON file
    import os
    json_file_path = os.path.join(os.path.dirname(__file__), '../data.json')
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        query = request.POST.get('query')

        # Create a new contact entry
        new_contact = {
            "name": name,
            "email": email,
            "contact": contact,
            "query": query,
            "resolved":"no"
        }

        # Load existing data from JSON
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        # Append the new contact to the 'contacts' array
        if 'contacts' not in data:
            data['contacts'] = []
        data['contacts'].append(new_contact)

        # Save updated data back to JSON
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

        # Redirect or render success message
        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')

def base(request):
    return render(request,'base.html')

import json
from django.shortcuts import render

def admin_list(request):
    # Path to the JSON file
    import os
    json_file_path = os.path.join(os.path.dirname(__file__), '../../drdo/data.json')
    
    # Load data from JSON file
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Pass data to the template
    return render(request, 'admin_list.html', {'data': data})

import json
import nltk
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import random

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load intents.json
with open('intents.json') as f:
    intents_data = json.load(f)

# Function to extract keywords from input using NLTK
def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalnum()]

def match_intent(user_input):
    query_embedding = model.encode(user_input, convert_to_tensor=True)
    highest_score = -1
    matched_intent = None

    for intent in intents_data['intents']:
        for example in intent['examples']:
            example_embedding = model.encode(example, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(query_embedding, example_embedding)[0][0].item()

            if similarity > highest_score:
                highest_score = similarity
                matched_intent = intent

    # Define a similarity threshold for meaningful responses
    similarity_threshold = 0.7
    if highest_score >= similarity_threshold:
        return matched_intent
    else:
        return None

# Handle incoming user input
@csrf_exempt
def chat(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()

        if not user_input:
            response = {
                'intent': 'unknown',
                'response': "Sorry, I couldn't understand your input. Please try again."
            }
        else:
            # Match the intent
            matched_intent = match_intent(user_input)

            if matched_intent:
                response = {
                    'intent': matched_intent['intent'],
                    'response': random.choice(matched_intent['responses'])  # Random response
                }
            else:
                response = {
                    'intent': 'unknown',
                    'response': "Sorry, I couldn't understand your query. Could you rephrase it?"
                }

        return JsonResponse(response)
    return render(request, 'user_base.html')  # Assuming you're rendering a basic chat interface
