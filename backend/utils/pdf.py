import os
from flask import render_template_string
from weasyprint import HTML, CSS
from datetime import datetime

def generate_pdf_report(
    user_details, numerology_data, report_content, left_palm_image_base64, right_palm_image_base64, language, report_type,
    person2_details=None, numerology_data_p2=None, person2_left_palm_image_base64=None, person2_right_palm_image_base64=None
):
    """
    Generates a PDF report for individual or couple, from AI-generated content and user details.
    Uses an HTML template to structure the PDF.
    """
    output_dir = "temp_reports"
    os.makedirs(output_dir, exist_ok=True)

    # --- Generate dynamic PDF filename ---
    if report_type == 'individual':
        sanitized_name = "".join(e for e in user_details['person1_name'] if e.isalnum())
        dob_for_filename = user_details['person1_dob'].replace('-', '')
        pdf_filename = f"Palm_Path_Report_{sanitized_name}_{dob_for_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    elif report_type == 'couple' and person2_details:
        sanitized_name1 = "".join(e for e in user_details['person1_name'] if e.isalnum())
        sanitized_name2 = "".join(e for e in person2_details['person2_name'] if e.isalnum())
        pdf_filename = f"Couple_Report_{sanitized_name1}_{sanitized_name2}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    else:
        pdf_filename = f"Report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf" # Fallback

    pdf_path = os.path.join(output_dir, pdf_filename)

    # --- Basic CSS for the PDF ---
    report_css = """
    @page { size: A4; margin: 1in; }
    body { font-family: 'Times New Roman', serif; line-height: 1.6; color: #333; }
    h1, h2, h3, h4 { color: #0056b3; font-family: 'Georgia', serif; margin-top: 1.5em; margin-bottom: 0.5em; }
    h1 { font-size: 2.5em; text-align: center; color: #003366; }
    h2 { font-size: 1.8em; border-bottom: 2px solid #0056b3; padding-bottom: 0.3em; }
    h3 { font-size: 1.4em; color: #007bff; }
    p { margin-bottom: 1em; text-align: justify; }
    .section { margin-bottom: 2em; page-break-inside: avoid; }
    .page-break { page-break-before: always; }
    .text-center { text-align: center; }
    .img-fluid { max-width: 100%; height: auto; display: block; margin: 1em auto; border: 1px solid #ddd; padding: 5px; background: #fff; }
    .card { border: 1px solid #eee; border-radius: 8px; padding: 1.5em; margin-bottom: 1.5em; background-color: #f9f9f9; }
    .footer { text-align: center; margin-top: 2em; font-size: 0.8em; color: #777; }
    .header-info { text-align: center; margin-bottom: 2em; }
    .premium-badge {
        display: inline-block;
        background-color: #ffc107;
        color: #333;
        padding: 0.3em 0.8em;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        margin-top: 1em;
    }
    .person-section { margin-top: 2em; border-left: 5px solid #007bff; padding-left: 1em; }
    """

    # Prepare data for the template
    template_data = {
        'user': user_details,
        'numerology': numerology_data,
        'report_content': report_content,
        'left_palm_image_base64': left_palm_image_base64,
        'right_palm_image_base64': right_palm_image_base64,
        'language': language,
        'report_type': report_type,
        'generated_date': datetime.now().strftime("%B %d, %Y"),
        'person2': person2_details, # For couple reports
        'numerology_p2': numerology_data_p2, # For couple reports
        'person2_left_palm_image_base64': person2_left_palm_image_base64,
        'person2_right_palm_image_base64': person2_right_palm_image_base64
    }

    # --- HTML Template for the PDF ---
    # IMPORTANT: Removed the 'f' prefix here. This is a regular multi-line string
    # that will be interpreted by Jinja2 via render_template_string.
    html_content = """
    <!DOCTYPE html>
    <html lang="{language}">
    <head>
        <meta charset="UTF-8">
        <title>Palm & Path AI Report - {% if report_type == 'individual' %}{{ user.person1_name }}{% else %}{{ user.person1_name }} & {{ person2.person2_name }}{% endif %}</title>
        <style>
            {report_css}
        </style>
    </head>
    <body>
        <div class="header-info">
            <h1>Palm & Path AI Report</h1>
            {% if report_type == 'individual' %}
                <p>A Personalized Journey of Self-Discovery</p>
                <p><strong>Generated for:</strong> {{ user.person1_name }}</p>
                <p><strong>Date of Birth:</strong> {{ user.person1_dob }}</p>
            {% else %}
                <p>A Shared Journey of Love & Destiny</p>
                <p><strong>Generated for:</strong> {{ user.person1_name }} & {{ person2.person2_name }}</p>
                <p><strong>Report Date:</strong> {{ generated_date }}</p>
            {% endif %}
            {% if report_type == 'premium' %}
            <span class="premium-badge">Premium Report</span>
            {% endif %}
        </div>

        <div class="page-break"></div>

        <div class="section">
            <h2>{{ report_content.introduction | safe }}</h2>
        </div>

        {% if report_type == 'individual' %}
            <div class="page-break"></div>
            <div class="section">
                <h2>Your Numerology Insights</h2>
                <h3>Life Path Number: {{ numerology.life_path_number }}</h3>
                <p>{{ numerology.interpretations.life_path_summary | safe }}</p>
                <h3>Detailed Numerology Analysis</h3>
                <p>{{ report_content.numerology_detailed | safe }}</p>
                <h3>Destiny Number: {{ numerology.destiny_number }}</h3>
                <p>{{ numerology.interpretations.destiny_summary | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Your Palmistry Insights</h2>
                {% if left_palm_image_base64 %}
                <h3 class="text-center">Left Palm Overview</h3>
                <img class="img-fluid" src="data:image/jpeg;base64,{{ left_palm_image_base64 }}" alt="Left Palm" />
                {% endif %}
                <h3>Detailed Left Palm Analysis</h3>
                <p>{{ report_content.left_palm_detailed | safe }}</p>

                {% if right_palm_image_base64 %}
                <h3 class="text-center">Right Palm Insights</h3>
                <img class="img-fluid" src="data:image/jpeg;base64,{{ right_palm_image_base64 }}" alt="Right Palm" />
                {% endif %}
                <h3>Detailed Right Palm Analysis</h3>
                <p>{{ report_content.right_palm_detailed | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Career Outlook</h2>
                <p>{{ report_content.career_outlook | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Relationship Traits</h2>
                <p>{{ report_content.relationship_traits | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Year-by-Year Forecast</h2>
                <p>{{ report_content.year_by_year_forecast | safe }}</p>
            </div>

        {% else %} {# Couple Report #}

            <div class="page-break"></div>
            <div class="section">
                <h2>Numerology Insights for {{ user.person1_name }}</h2>
                <div class="person-section">
                    <h3>Life Path Number: {{ numerology.life_path_number }}</h3>
                    <p>{{ numerology.interpretations.life_path_summary | safe }}</p>
                    <h3>Detailed Numerology Analysis</h3>
                    <p>{{ report_content.person1_numerology | safe }}</p>
                    <h3>Destiny Number: {{ numerology.destiny_number }}</h3>
                    <p>{{ numerology.interpretations.destiny_summary | safe }}</p>
                </div>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Palmistry Insights for {{ user.person1_name }}</h2>
                <div class="person-section">
                    {% if left_palm_image_base64 %}
                    <h3 class="text-center">Left Palm Overview</h3>
                    <img class="img-fluid" src="data:image/jpeg;base64,{{ left_palm_image_base64 }}" alt="Left Palm of {{ user.person1_name }}" />
                    {% endif %}
                    <h3>Detailed Left Palm Analysis</h3>
                    <p>{{ report_content.person1_left_palm | safe }}</p>

                    {% if right_palm_image_base64 %}
                    <h3 class="text-center">Right Palm Insights</h3>
                    <img class="img-fluid" src="data:image/jpeg;base64,{{ right_palm_image_base64 }}" alt="Right Palm of {{ user.person1_name }}" />
                    {% endif %}
                    <h3>Detailed Right Palm Analysis</h3>
                    <p>{{ report_content.person1_right_palm | safe }}</p>
                </div>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Numerology Insights for {{ person2.person2_name }}</h2>
                <div class="person-section">
                    <h3>Life Path Number: {{ numerology_p2.life_path_number }}</h3>
                    <p>{{ numerology_p2.interpretations.life_path_summary | safe }}</p>
                    <h3>Detailed Numerology Analysis</h3>
                    <p>{{ report_content.person2_numerology | safe }}</p>
                    <h3>Destiny Number: {{ numerology_p2.destiny_number }}</h3>
                    <p>{{ numerology_p2.interpretations.destiny_summary | safe }}</p>
                </div>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Palmistry Insights for {{ person2.person2_name }}</h2>
                <div class="person-section">
                    {% if person2_left_palm_image_base64 %}
                    <h3 class="text-center">Left Palm Overview</h3>
                    <img class="img-fluid" src="data:image/jpeg;base64,{{ person2_left_palm_image_base64 }}" alt="Left Palm of {{ person2.person2_name }}" />
                    {% endif %}
                    <h3>Detailed Left Palm Analysis</h3>
                    <p>{{ report_content.person2_left_palm | safe }}</p>

                    {% if person2_right_palm_image_base64 %}
                    <h3 class="text-center">Right Palm Insights</h3>
                    <img class="img-fluid" src="data:image/jpeg;base64,{{ person2_right_palm_image_base64 }}" alt="Right Palm of {{ person2.person2_name }}" />
                    {% endif %}
                    <h3>Detailed Right Palm Analysis</h3>
                    <p>{{ report_content.person2_right_palm | safe }}</p>
                </div>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Relationship Compatibility</h2>
                <p>{{ report_content.relationship_compatibility | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Combined Path & Purpose</h2>
                <p>{{ report_content.combined_path_purpose | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Challenges & Growth</h2>
                <p>{{ report_content.challenges_growth | safe }}</p>
            </div>

            <div class="page-break"></div>
            <div class="section">
                <h2>Shared Future Outlook</h2>
                <p>{{ report_content.shared_future_outlook | safe }}</p>
            </div>

        {% endif %}

        <div class="page-break"></div>
        <div class="section">
            <h2>Conclusion</h2>
            {% if report_type == 'individual' %}
            <p>{{ report_content.conclusion | safe }}</p>
            {% else %}
            <p>{{ report_content.conclusion_couple | safe }}</p>
            {% endif %}
        </div>

        <div class="footer">
            <p>Report generated by AuraPalm.in. For entertainment and self-reflection purposes only.</p>
            <p>Wishing you wisdom and clarity on your path.</p>
        </div>
    </body>
    </html>
    """
    rendered_html = render_template_string(html_content, **template_data)
    HTML(string=rendered_html).write_pdf(pdf_path, stylesheets=[CSS(string=report_css)])

    return pdf_path

if __name__ == '__main__':
    # This block allows you to test PDF generation directly
    from numerology import get_numerology_insights

    # Dummy image base64
    dummy_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    # --- INDIVIDUAL REPORT TEST DATA ---
    test_user_details_individual = {
        "person1_name": "Test Individual",
        "person1_dob": "1990-01-01",
        "person1_gender": "female"
    }
    test_numerology_individual = get_numerology_insights(test_user_details_individual['person1_dob'], test_user_details_individual['person1_name'])
    test_report_content_individual = {
        'introduction': "Welcome to your basic report. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 2,
        'numerology_detailed': "Detailed numerology analysis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'left_palm_detailed': "Detailed left palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'right_palm_detailed': "Detailed right palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'career_outlook': "Career outlook insights. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 3,
        'relationship_traits': "Relationship traits analysis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 3,
        'year_by_year_forecast': "Yearly forecast. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 3,
        'conclusion': "Thank you for your report. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    }

    # --- COUPLE REPORT TEST DATA ---
    test_user_details_couple = {
        "person1_name": "Arjun",
        "person1_dob": "1990-05-15",
        "person1_gender": "male",
        "person2_name": "Priya",
        "person2_dob": "1991-03-22",
        "person2_gender": "female"
    }
    test_numerology_p1 = get_numerology_insights(test_user_details_couple['person1_dob'], test_user_details_couple['person1_name'])
    test_numerology_p2 = get_numerology_insights(test_user_details_couple['person2_dob'], test_user_details_couple['person2_name'])
    test_report_content_couple = {
        'introduction': "Welcome to your joint report. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 2,
        'person1_numerology': "Arjun's detailed numerology analysis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'person1_left_palm': "Arjun's detailed left palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'person1_right_palm': "Arjun's detailed right palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'person2_numerology': "Priya's detailed numerology analysis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'person2_left_palm': "Priya's detailed left palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'person2_right_palm': "Priya's detailed right palm reading. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'relationship_compatibility': "Couple compatibility analysis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 8,
        'combined_path_purpose': "Combined path and purpose insights. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'challenges_growth': "Challenges and growth areas for the couple. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'shared_future_outlook': "Shared future outlook. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 5,
        'conclusion_couple': "Joint conclusion. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." * 2
    }


    print("--- Testing Individual PDF Generation ---")
    basic_pdf_path = generate_pdf_report(
        test_user_details_individual, test_numerology_individual, test_report_content_individual,
        dummy_image_base64, dummy_image_base64, 'en', 'individual'
    )
    print(f"Individual PDF generated at: {basic_pdf_path}")

    print("\n--- Testing Couple PDF Generation ---")
    couple_pdf_path = generate_pdf_report(
        test_user_details_couple, test_numerology_p1, test_report_content_couple,
        dummy_image_base64, dummy_image_base64, 'en', 'couple',
        person2_details=test_user_details_couple, # Pass the same dict, pdf.py extracts p2 data
        numerology_data_p2=test_numerology_p2,
        person2_left_palm_image_base64=dummy_image_base64,
        person2_right_palm_image_base64=dummy_image_base64
    )
    print(f"Couple PDF generated at: {couple_pdf_path}")