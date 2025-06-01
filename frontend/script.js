document.addEventListener('DOMContentLoaded', () => {
    const reportForm = document.getElementById('reportForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const individualReportRadio = document.getElementById('individualReport');
    const coupleReportRadio = document.getElementById('coupleReport');
    const individualSection = document.getElementById('individualSection');
    const coupleSection = document.getElementById('coupleSection');
    const individualReportTypeRadios = document.getElementById('individualReportTypeRadios');
    const paymentAmountSpan = document.getElementById('paymentAmount');

    // Make sure this matches your Flask backend URL.
    // When deploying, this will need to be the deployed backend URL (e.g., 'https://api.aurapalm.in').
    const BACKEND_URL = 'http://127.0.0.1:5000'; // For local development

    const PRICES = {
        individual_basic: 50,
        individual_premium: 150,
        couple_premium: 200 // Couple report is always premium and comprehensive
    };

    // --- UI Toggle Logic ---
    function toggleReportSections() {
        if (individualReportRadio.checked) {
            individualSection.classList.remove('d-none');
            coupleSection.classList.add('d-none');
            individualReportTypeRadios.classList.remove('d-none'); // Show individual report type options
            updatePaymentAmount(); // Update for individual options
            setRequiredAttributes(true);
            setRequiredAttributesCouple(false); // Make couple fields not required
        } else {
            individualSection.classList.add('d-none');
            coupleSection.classList.remove('d-none');
            individualReportTypeRadios.classList.add('d-none'); // Hide individual report type options
            document.getElementById('premiumReport').checked = true; // Force premium for couple
            updatePaymentAmount(); // Update for couple
            setRequiredAttributes(false); // Make individual fields not required
            setRequiredAttributesCouple(true); // Make couple fields required
        }
    }

    function updatePaymentAmount() {
        let amount = 0;
        if (individualReportRadio.checked) {
            const selectedIndividualType = document.querySelector('input[name="individualReportType"]:checked').value;
            amount = PRICES[`individual_${selectedIndividualType}`];
        } else {
            amount = PRICES.couple_premium; // Couple report is always premium
        }
        paymentAmountSpan.textContent = `₹${amount}`;
    }

    function setRequiredAttributes(isIndividual) {
        // Individual fields
        document.getElementById('fullName1').required = isIndividual;
        document.getElementById('dob1').required = isIndividual;
        document.getElementById('gender1').required = isIndividual;
        document.getElementById('leftPalm1').required = isIndividual;
        document.getElementById('rightPalm1').required = isIndividual;
    }

    function setRequiredAttributesCouple(isCouple) {
        // Partner 1 fields
        document.getElementById('fullNameP1').required = isCouple;
        document.getElementById('dobP1').required = isCouple;
        document.getElementById('genderP1').required = isCouple;
        document.getElementById('leftPalmP1').required = isCouple;
        document.getElementById('rightPalmP1').required = isCouple;
        // Partner 2 fields
        document.getElementById('fullNameP2').required = isCouple;
        document.getElementById('dobP2').required = isCouple;
        document.getElementById('genderP2').required = isCouple;
        document.getElementById('leftPalmP2').required = isCouple;
        document.getElementById('rightPalmP2').required = isCouple;
    }


    individualReportRadio.addEventListener('change', toggleReportSections);
    coupleReportRadio.addEventListener('change', toggleReportSections);

    // Update payment amount based on individual report type selection
    document.querySelectorAll('input[name="individualReportType"]').forEach(radio => {
        radio.addEventListener('change', updatePaymentAmount);
    });

    // Initial setup
    toggleReportSections(); // Set initial visibility and required fields

    // --- Form Submission Logic ---
    reportForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Reset UI state
        submitBtn.setAttribute('disabled', 'true');
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        errorMessage.textContent = '';

        try {
            const reportType = document.querySelector('input[name="reportOption"]:checked').value;
            const language = document.getElementById('language').value;
            let amount = 0;
            let payload = {};

            // Helper to convert file to Base64
            const getBase64 = (file) => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = error => reject(error);
                });
            };

            if (reportType === 'individual') {
                const selectedIndividualType = document.querySelector('input[name="individualReportType"]:checked').value;
                amount = PRICES[`individual_${selectedIndividualType}`];

                const fullName1 = document.getElementById('fullName1').value;
                const dob1 = document.getElementById('dob1').value;
                const gender1 = document.getElementById('gender1').value;
                const leftPalm1 = document.getElementById('leftPalm1').files[0];
                const rightPalm1 = document.getElementById('rightPalm1').files[0];

                if (!leftPalm1 || !rightPalm1) throw new Error('Please upload both left and right palm images for yourself.');

                payload = {
                    report_type: 'individual',
                    language: language,
                    personal_details: {
                        name: fullName1,
                        dob: dob1,
                        gender: gender1
                    },
                    left_palm_image_base64: await getBase64(leftPalm1),
                    right_palm_image_base64: await getBase64(rightPalm1)
                };

            } else if (reportType === 'couple') {
                amount = PRICES.couple_premium; // Couple is always premium

                const fullNameP1 = document.getElementById('fullNameP1').value;
                const dobP1 = document.getElementById('dobP1').value;
                const genderP1 = document.getElementById('genderP1').value;
                const leftPalmP1 = document.getElementById('leftPalmP1').files[0];
                const rightPalmP1 = document.getElementById('rightPalmP1').files[0];

                const fullNameP2 = document.getElementById('fullNameP2').value;
                const dobP2 = document.getElementById('dobP2').value;
                const genderP2 = document.getElementById('genderP2').value;
                const leftPalmP2 = document.getElementById('leftPalmP2').files[0];
                const rightPalmP2 = document.getElementById('rightPalmP2').files[0];

                if (!leftPalmP1 || !rightPalmP1 || !leftPalmP2 || !rightPalmP2) {
                    throw new Error('Please upload all four palm images for the couple report.');
                }

                payload = {
                    report_type: 'couple',
                    language: language,
                    person1_details: {
                        name: fullNameP1,
                        dob: dobP1,
                        gender: genderP1
                    },
                    person1_left_palm_image_base64: await getBase64(leftPalmP1),
                    person1_right_palm_image_base64: await getBase64(rightPalmP1),
                    person2_details: {
                        name: fullNameP2,
                        dob: dobP2,
                        gender: genderP2
                    },
                    person2_left_palm_image_base64: await getBase64(leftPalmP2),
                    person2_right_palm_image_base64: await getBase64(rightPalmP2)
                };
            }

            // 2. Initiate Razorpay order on the backend
            const orderResponse = await fetch(`${BACKEND_URL}/api/create-order`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: amount })
            });

            if (!orderResponse.ok) {
                const errorData = await orderResponse.json();
                throw new Error(errorData.message || 'Failed to create order. Please check backend console.');
            }
            const orderData = await orderResponse.json();
            const { order_id, amount: razorpayAmount, currency, key_id } = orderData;

            // 3. Open Razorpay Checkout
            const options = {
                key: key_id,
                amount: razorpayAmount,
                currency: currency,
                name: 'AuraPalm.in',
                description: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
                order_id: order_id,
                handler: async function (response) {
                    console.log('Payment successful:', response);
                    loadingSpinner.querySelector('p').textContent = 'Payment successful! Generating your personalized report. This may take a few moments...';

                    // Add Razorpay details to payload for server-side verification (optional for simple flow, but good to pass)
                    payload.razorpay_payment_id = response.razorpay_payment_id;
                    payload.razorpay_order_id = response.razorpay_order_id;
                    payload.razorpay_signature = response.razorpay_signature;

                    // 4. On successful payment, trigger report generation on backend
                    const generateReportResponse = await fetch(`${BACKEND_URL}/api/generate-report`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (!generateReportResponse.ok) {
                        const errorData = await generateReportResponse.json();
                        throw new Error(errorData.message || 'Failed to generate report. Please check backend console.');
                    }
                    const reportResult = await generateReportResponse.json();

                    // 5. Trigger PDF download
                    if (reportResult.download_url) {
                        alert('Report generated! Your download will start shortly.');
                        window.location.href = `${BACKEND_URL}${reportResult.download_url}`;
                        reportForm.reset(); // Clear form after successful download
                        toggleReportSections(); // Reset UI state after form reset
                    } else {
                        throw new Error('Report generated, but no download URL provided.');
                    }
                },
                prefill: {
                    name: (reportType === 'individual' ? document.getElementById('fullName1').value : document.getElementById('fullNameP1').value + ' & ' + document.getElementById('fullNameP2').value),
                },
                notes: {
                    address: 'AuraPalm.in Service'
                },
                theme: {
                    color: '#007bff'
                }
            };

            const rzp = new Razorpay(options);
            rzp.on('razorpay_payment_failed', function (response) {
                console.error('Payment failed:', response.error);
                errorMessage.textContent = `Payment failed: ${response.error.description || 'Unknown error.'}`;
                errorMessage.classList.remove('d-none');
                alert(`Payment failed: ${response.error.description}`);
            });
            rzp.open();

        } catch (error) {
            console.error('Error during report process:', error);
            errorMessage.textContent = error.message || 'An unexpected error occurred. Please try again.';
            errorMessage.classList.remove('d-none');
        } finally {
            submitBtn.removeAttribute('disabled');
            loadingSpinner.classList.add('d-none');
        }
    });
});