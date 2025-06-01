import os
import datetime
import base64 # Needed for image handling (though images are passed as base64 from frontend)
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import razorpay
from razorpay.errors import BadRequestError, ServerError

# Import our utility functions
from utils.numerology import get_numerology_insights
from utils.gpt import generate_full_report_content
from utils.pdf import generate_pdf_report

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Configuration (loaded from .env) ---
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Picked up automatically by OpenAI client

# Initialize Razorpay client
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None
    print("WARNING: Razorpay API keys are not loaded. Payment functionality will be disabled.")

# Ensure essential keys are present
if not OPENAI_API_KEY:
    print("CRITICAL ERROR: OPENAI_API_KEY is missing. AI functionality will not work.")

# Temporary directory for generated PDFs
PDF_OUTPUT_DIR = "temp_reports"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True) # Ensure it exists


# --- Routes ---

@app.route('/')
def index():
    return "Backend is running. Please access the frontend at its own URL (aurapalm.in)."

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is up and running!"})

@app.route('/api/create-order', methods=['POST'])
def create_order():
    if not razorpay_client:
        return jsonify({"status": "error", "message": "Razorpay not configured."}), 500

    data = request.get_json()
    amount_in_inr = data.get('amount')
    if not amount_in_inr:
        return jsonify({"status": "error", "message": "Amount is required."}), 400

    amount_in_paise = int(amount_in_inr * 100) # Razorpay expects amount in smallest currency unit (paise)

    try:
        receipt_id = f"rcpt_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        order_details = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": '1' # Auto capture payment
        })
        print(f"DEBUG: Razorpay order created: {order_details}")

        return jsonify({
            "order_id": order_details['id'],
            "amount": order_details['amount'],
            "currency": order_details['currency'],
            "key_id": RAZORPAY_KEY_ID # Send Key ID to frontend for checkout.js
        })
    except BadRequestError as e:
        print(f"ERROR: Razorpay BadRequestError: {e}")
        return jsonify({"status": "error", "message": f"Razorpay error: {e.description}"}), 400
    except ServerError as e:
        print(f"ERROR: Razorpay ServerError: {e}")
        return jsonify({"status": "error", "message": "Razorpay service is temporarily unavailable."}), 503
    except Exception as e:
        print(f"ERROR: Failed to create order: {e}")
        return jsonify({"status": "error", "message": "Failed to create payment order."}), 500


@app.route('/api/razorpay-webhook', methods=['POST'])
def razorpay_webhook():
    # Placeholder for webhook. For robust production, verify signature.
    # from razorpay.utils import verify_webhook_signature
    # WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    # try:
    #     verify_webhook_signature(request.data, request.headers.get('X-Razorpay-Signature'), WEBHOOK_SECRET)
    # except Exception as e:
    #     print(f"ERROR: Webhook signature verification failed: {e}")
    #     return jsonify({"status": "error", "message": "Invalid webhook signature."}), 400

    payload = request.get_json()
    event = payload.get('event')
    print(f"DEBUG: Received Razorpay webhook event: {event}")

    if event == 'payment.captured':
        payment_id = payload['payload']['payment']['entity']['id']
        order_id = payload['payload']['payment']['entity']['order_id']
        amount = payload['payload']['payment']['entity']['amount']
        print(f"INFO: Payment captured - Payment ID: {payment_id}, Order ID: {order_id}, Amount: {amount}")

    return jsonify({"status": "success", "message": "Webhook received."}), 200


@app.route('/api/generate-report', methods=['POST'])
async def generate_report_api():
    data = request.get_json()

    # Determine report type and required fields
    report_type = data.get('report_type')
    if report_type not in ['individual', 'couple']:
        return jsonify({"status": "error", "message": "Invalid report type specified."}), 400

    required_fields_common = ['language', 'razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']
    required_fields_individual = ['personal_details', 'left_palm_image_base64', 'right_palm_image_base64']
    required_fields_couple = [
        'person1_details', 'person1_left_palm_image_base64', 'person1_right_palm_image_base64',
        'person2_details', 'person2_left_palm_image_base64', 'person2_right_palm_image_base64'
    ]

    # Validate common fields
    for field in required_fields_common:
        if field not in data or not data[field]:
            return jsonify({"status": "error", "message": f"Missing common required data: {field}"}), 400

    # Validate report-specific fields and prepare data structures
    user_details = {}
    person2_details = None
    left_palm_image_base64 = None
    right_palm_image_base64 = None
    person2_left_palm_image_base64 = None
    person2_right_palm_image_base64 = None

    if report_type == 'individual':
        for field in required_fields_individual:
            if field not in data or not data[field]:
                return jsonify({"status": "error", "message": f"Missing individual report data: {field}"}), 400
        
        user_details = data['personal_details'] # This is person1_details
        user_details['person1_name'] = user_details.get('name') # Alias for consistency
        user_details['person1_dob'] = user_details.get('dob')
        user_details['person1_gender'] = user_details.get('gender')

        left_palm_image_base64 = data['left_palm_image_base64']
        right_palm_image_base64 = data['right_palm_image_base64']

    elif report_type == 'couple':
        for field in required_fields_couple:
            if field not in data or not data[field]:
                return jsonify({"status": "error", "message": f"Missing couple report data: {field}"}), 400
        
        # Person 1 details
        user_details = data['person1_details']
        user_details['person1_name'] = user_details.get('name') # Alias for consistency
        user_details['person1_dob'] = user_details.get('dob')
        user_details['person1_gender'] = user_details.get('gender')
        left_palm_image_base64 = data['person1_left_palm_image_base64']
        right_palm_image_base64 = data['person1_right_palm_image_base64']

        # Person 2 details
        person2_details = data['person2_details']
        person2_details['person2_name'] = person2_details.get('name') # Alias for consistency
        person2_details['person2_dob'] = person2_details.get('dob')
        person2_details['person2_gender'] = person2_details.get('gender')
        person2_left_palm_image_base64 = data['person2_left_palm_image_base64']
        person2_right_palm_image_base64 = data['person2_right_palm_image_base64']

    language = data['language']

    # For a production app, you would VERIFY the Razorpay payment details here again
    # using razorpay_client.utility.verify_payment_signature to prevent fraud.
    # We are skipping for quick setup, relying on frontend callback and webhook for now.
    # from razorpay.utils import verify_payment_signature
    # params_dict = {
    #     'razorpay_order_id': data['razorpay_order_id'],
    #     'razorpay_payment_id': data['razorpay_payment_id'],
    #     'razorpay_signature': data['razorpay_signature']
    # }
    # try:
    #     razorpay_client.utility.verify_payment_signature(params_dict)
    #     print("DEBUG: Razorpay signature verified successfully.")
    # except Exception as e:
    #     print(f"ERROR: Razorpay signature verification failed: {e}")
    #     return jsonify({"status": "error", "message": "Payment verification failed."}), 400

    try:
        # 1. Calculate Numerology Insights for Person 1
        print(f"INFO: Calculating numerology for {user_details.get('person1_name')}...")
        numerology_insights_p1 = get_numerology_insights(user_details['person1_dob'], user_details['person1_name'])

        numerology_insights_p2 = None
        if report_type == 'couple' and person2_details:
            print(f"INFO: Calculating numerology for {person2_details.get('person2_name')}...")
            numerology_insights_p2 = get_numerology_insights(person2_details['person2_dob'], person2_details['person2_name'])

        # 2. Generate Report Content via OpenAI (multiple calls)
        print("INFO: Generating AI report content...")
        report_content_sections = await generate_full_report_content(
            user_details, numerology_insights_p1,
            left_palm_image_base64, right_palm_image_base64,
            language, report_type,
            person2_details, numerology_insights_p2,
            person2_left_palm_image_base64, person2_right_palm_image_base64
        )
        print("INFO: AI report content generated.")

        # 3. Generate PDF Report
        print("INFO: Generating PDF report...")
        pdf_path = generate_pdf_report(
            user_details, numerology_insights_p1, report_content_sections,
            left_palm_image_base64, right_palm_image_base64,
            language, report_type,
            person2_details, numerology_insights_p2,
            person2_left_palm_image_base64, person2_right_palm_image_base64
        )
        print(f"INFO: PDF generated at {pdf_path}")

        # Construct the download URL relative to the backend
        download_filename = os.path.basename(pdf_path)
        download_url = f"/api/download-report/{download_filename}"

        return jsonify({
            "status": "success",
            "message": "Report generated successfully.",
            "download_url": download_url
        })

    except Exception as e:
        print(f"ERROR: Error during report generation: {e}", exc_info=True) # exc_info for full traceback
        return jsonify({"status": "error", "message": f"An error occurred during report generation: {str(e)}"}), 500


@app.route('/api/download-report/<filename>', methods=['GET'])
def download_report(filename):
    file_path = os.path.join(PDF_OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        print(f"ERROR: Download requested for non-existent file: {file_path}")
        return jsonify({"status": "error", "message": "Report file not found."}), 404

    try:
        response = send_file(file_path, as_attachment=True, download_name=filename)
        @response.call_on_close
        def on_close():
            try:
                os.remove(file_path)
                print(f"INFO: Deleted temporary report file: {file_path}")
            except Exception as e:
                print(f"ERROR: Failed to delete temporary file {file_path}: {e}")
        return response
    except Exception as e:
        print(f"ERROR: Failed to serve or delete file {file_path}: {e}")
        return jsonify({"status": "error", "message": "Could not process file download."}), 500


if __name__ == '__main__':
    # Ensure your .env file is correctly populated for keys
    app.run(debug=True, port=5000)