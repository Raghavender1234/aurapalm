import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import httpx # <--- ADD THIS IMPORT: import httpx

load_dotenv() # <--- THIS LINE MUST BE HERE, *OUTSIDE* THE if __name__ block

# Initialize OpenAI client
client = OpenAI(
    http_client=httpx.Client(
        trust_env=False # <--- ADD THIS LINE to prevent automatic proxy detection
    )
)


# --- Base Prompts and Instructions ---
BASE_INSTRUCTIONS = (
    "You are an empathetic, insightful, and encouraging AI assistant specialized in providing "
    "personalized palmistry and numerology reports. Your tone should be warm, wise, and supportive, "
    "never negative or fatalistic. Always focus on potential, strengths, and guidance for growth. "
    "Structure your responses clearly with headings and bullet points where appropriate. "
    "Ensure all interpretations are delivered with a kind and hopeful demeanor."
)

# --- Report Section Prompts ---

def get_introduction_prompt(user_details, report_type, language='en'):
    """Generates the prompt for the introduction section."""
    if report_type == 'individual':
        name = user_details.get('name', 'valued client')
        return [
            {"role": "system", "content": f"{BASE_INSTRUCTIONS} Provide a welcoming and intriguing introduction to a personalized palmistry and numerology report in {language}. Set a positive and insightful tone for the journey ahead. Address the user by their name: {name}."}
        ]
    elif report_type == 'couple':
        name1 = user_details.get('person1_name', 'first valued client')
        name2 = user_details.get('person2_name', 'second valued client')
        return [
            {"role": "system", "content": f"{BASE_INSTRUCTIONS} Provide a welcoming and intriguing introduction to a joint palmistry and numerology report for a couple in {language}. Set a positive and insightful tone for their shared journey. Address them as: {name1} and {name2}."}
        ]
    return []

def get_numerology_insight_prompt(user_details, numerology_data, person_prefix, language='en', detailed=False):
    """Generates the prompt for numerology insights for an individual (or person in a couple)."""
    name = user_details.get(f'{person_prefix}_name', 'valued client')
    dob = user_details.get(f'{person_prefix}_dob', 'their date of birth')
    life_path = numerology_data.get(f'{person_prefix}_life_path_number')
    destiny = numerology_data.get(f'{person_prefix}_destiny_number')

    detail_level = "Provide a concise overview" if not detailed else "Provide a detailed and comprehensive analysis"

    prompt_content = (
        f"{detail_level} of the numerological significance for {name} (Born: {dob}). "
        f"Their Life Path Number is {life_path}. Their Destiny (Expression) Number is {destiny}. "
        "Explain what each number represents (core essence, talents/potential) and how they interact. "
        "Discuss their strengths, challenges, and life purpose based on these numbers. "
        f"Output should be in {language}."
    )
    return [
        {"role": "system", "content": BASE_INSTRUCTIONS},
        {"role": "user", "content": prompt_content}
    ]

def get_palm_reading_prompt(user_details, image_base64, hand_type, person_prefix, language='en', detailed=False):
    """
    Generates the prompt for a palm reading section for an individual (or person in a couple).
    Uses Vision API if image_base64 is provided.
    """
    name = user_details.get(f'{person_prefix}_name', 'valued client')
    gender = user_details.get(f'{person_prefix}_gender', 'individual')
    dob_str = user_details.get(f'{person_prefix}_dob')
    current_year = datetime.datetime.now().year
    age = current_year - int(dob_str.split('-')[0]) if dob_str else 'their age'

    detail_level = "Provide a concise overview" if not detailed else "Provide a detailed and comprehensive analysis"

    prompt_messages = [
        {"role": "system", "content": f"{BASE_INSTRUCTIONS} You are analyzing a {hand_type} palm for {name} ({gender}, approximately {age} years old). Provide a {detail_level.lower()} palm reading focusing on key lines (life, head, heart) and mounts (e.g., Venus, Jupiter) as they would typically appear. Interpret these features in a positive, guiding, and encouraging manner. Focus on general tendencies, potential, and areas for growth. Do not make any negative predictions. Your interpretation should be insightful and supportive. Output should be in {language}."}
    ]

    if image_base64:
        prompt_messages.append(
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze this {hand_type} palm image for {name} and provide your insights based on typical palmistry principles. Focus on overall shape, prominent features, and the flow of the main lines (Life, Head, Heart)."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}
        )
    else:
        prompt_messages.append(
            {"role": "user", "content": f"No image provided. Please provide a general {detail_level.lower()} palm reading for a {hand_type} hand, considering the user's name ({name}), gender ({gender}), and age ({age}). Focus on common positive interpretations."}
        )
    return prompt_messages

def get_relationship_compatibility_prompt(user_details, numerology_data_p1, numerology_data_p2, language='en'):
    """Generates the prompt for couple relationship compatibility."""
    name1 = user_details.get('person1_name', 'Partner 1')
    name2 = user_details.get('person2_name', 'Partner 2')
    lp1 = numerology_data_p1.get('life_path_number')
    lp2 = numerology_data_p2.get('life_path_number')
    dt1 = numerology_data_p1.get('destiny_number')
    dt2 = numerology_data_p2.get('destiny_number')

    prompt_content = (
        f"You are providing a relationship compatibility analysis for {name1} (Life Path: {lp1}, Destiny: {dt1}) "
        f"and {name2} (Life Path: {lp2}, Destiny: {dt2}). "
        "Analyze their combined numerological profiles. Discuss their potential strengths as a couple, "
        "areas where they complement each other, and potential challenges to be aware of. "
        "Offer constructive advice on fostering deeper understanding and harmony. "
        "Maintain a positive, encouraging, and supportive tone throughout. "
        f"Output should be a detailed analysis in {language}."
    )
    return [
        {"role": "system", "content": BASE_INSTRUCTIONS},
        {"role": "user", "content": prompt_content}
    ]

def get_sectional_prompt(section_name, user_details, numerology_data, language='en'):
    """Generates a prompt for other specific report sections for individual reports."""
    name = user_details.get('name', 'valued client')
    life_path = numerology_data.get('life_path_number')
    destiny = numerology_data.get('destiny_number')

    prompts = {
        'career_outlook': (
            f"Based on numerological insights (Life Path: {life_path}, Destiny: {destiny}), "
            f"provide a detailed career outlook for {name}. Focus on suitable professions, "
            f"strengths in the workplace, and advice for career growth. "
            f"Output should be in {language}."
        ),
        'relationship_traits': (
            f"Based on numerological insights (Life Path: {life_path}, Destiny: {destiny}), "
            f"describe {name}'s general relationship traits. Focus on how they interact with others, "
            f"what they seek in relationships, and advice for harmonious connections. "
            f"Output should be in {language}."
        ),
        'year_by_year_forecast': (
            f"Provide a positive year-by-year forecast for {name} for the next 3 years, starting from {datetime.datetime.now().year}. "
            f"Base this on general numerological cycles and provide encouraging advice for each year. "
            f"Highlight potential opportunities and areas of focus. Output should be in {language}."
        ),
        'conclusion': (
            f"Write an uplifting and encouraging conclusion for {name}'s personalized report in {language}. "
            f"Summarize the essence of the report and provide a final message of empowerment and optimism. "
            f"Encourage them to embrace their unique path."
        )
    }
    content = prompts.get(section_name.lower(), f"Provide insightful analysis for the {section_name} section for {name} in {language}.")
    return [
        {"role": "system", "content": BASE_INSTRUCTIONS},
        {"role": "user", "content": content}
    ]

def get_couple_sectional_prompt(section_name, user_details, numerology_data_p1, numerology_data_p2, language='en'):
    """Generates a prompt for other specific report sections for couple reports."""
    name1 = user_details.get('person1_name', 'Partner 1')
    name2 = user_details.get('person2_name', 'Partner 2')
    lp1 = numerology_data_p1.get('life_path_number')
    lp2 = numerology_data_p2.get('life_path_number')
    dt1 = numerology_data_p1.get('destiny_number')
    dt2 = numerology_data_p2.get('destiny_number')

    prompts = {
        'combined_path_purpose': (
            f"Based on the combined numerological profiles of {name1} (LP:{lp1}, DT:{dt1}) "
            f"and {name2} (LP:{lp2}, DT:{dt2}), discuss their shared life path and collective purpose. "
            f"Highlight their joint strengths and how they can best support each other's individual and shared goals. "
            f"Output should be in {language}."
        ),
        'challenges_growth': (
            f"For {name1} and {name2}, analyze potential areas of growth or challenges within their relationship, "
            f"drawing from their numerological numbers (LP1:{lp1}, DT1:{dt1}, LP2:{lp2}, DT2:{dt2}) and general palmistry principles. "
            f"Provide compassionate and practical advice for navigating disagreements and fostering mutual understanding. "
            f"Output should be in {language}."
        ),
        'shared_future_outlook': (
            f"Provide a positive and encouraging outlook on the shared future for {name1} and {name2}. "
            f"Based on their combined profiles, offer insights into their potential for long-term happiness, "
            f"growth, and success as a couple. Focus on harmonious development. "
            f"Output should be in {language}."
        ),
        'conclusion_couple': (
            f"Write an uplifting and encouraging conclusion for {name1} and {name2}'s joint report in {language}. "
            f"Summarize the essence of their combined insights and provide a final message of unity, empowerment, and optimism for their shared journey."
        )
    }
    content = prompts.get(section_name.lower(), f"Provide insightful analysis for the {section_name} section for {name1} and {name2} in {language}.")
    return [
        {"role": "system", "content": BASE_INSTRUCTIONS},
        {"role": "user", "content": content}
    ]


# --- Main API Call Function ---
async def call_openai_api(messages, model="gpt-4o", max_tokens=1500, temperature=0.7):
    """
    Calls the OpenAI API with the given messages and configuration.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        return f"AI generation failed for this section due to an error: {e}"

# --- Report Generation Orchestration ---

async def generate_full_report_content(user_details, numerology_data, left_palm_image_base64, right_palm_image_base64,
                                        language='en', report_type='individual',
                                        person2_details=None, numerology_data_p2=None,
                                        person2_left_palm_image_base64=None, person2_right_palm_image_base64=None):
    """
    Orchestrates the multiple OpenAI API calls to generate the full report content,
    supporting both individual and couple reports.
    """
    report_sections = {}
    model_to_use = "gpt-4o" # GPT-4o is powerful and can handle images for basic insights

    # Intro is always first
    report_sections['introduction'] = await call_openai_api(
        get_introduction_prompt(user_details, report_type, language),
        model=model_to_use, max_tokens=500
    )

    if report_type == 'individual':
        print("INFO: Generating content for INDIVIDUAL report...")
        report_sections['numerology_detailed'] = await call_openai_api(
            get_numerology_insight_prompt(user_details, numerology_data, 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        report_sections['left_palm_detailed'] = await call_openai_api(
            get_palm_reading_prompt(user_details, left_palm_image_base64, 'left', 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        report_sections['right_palm_detailed'] = await call_openai_api(
            get_palm_reading_prompt(user_details, right_palm_image_base64, 'right', 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        # Premium sections
        if report_type == 'premium' or True: # Force premium sections for now if no basic/premium logic is set
            report_sections['career_outlook'] = await call_openai_api(
                get_sectional_prompt('career_outlook', user_details, numerology_data, language),
                model=model_to_use, max_tokens=1000
            )
            report_sections['relationship_traits'] = await call_openai_api(
                get_sectional_prompt('relationship_traits', user_details, numerology_data, language),
                model=model_to_use, max_tokens=1000
            )
            report_sections['year_by_year_forecast'] = await call_openai_api(
                get_sectional_prompt('year_by_year_forecast', user_details, numerology_data, language),
                model=model_to_use, max_tokens=1200
            )
        report_sections['conclusion'] = await call_openai_api(
            get_sectional_prompt('conclusion', user_details, numerology_data, language),
            model=model_to_use, max_tokens=500
        )

    elif report_type == 'couple' and person2_details and numerology_data_p2:
        print("INFO: Generating content for COUPLE report...")

        # Numerology for Person 1
        report_sections['person1_numerology'] = await call_openai_api(
            get_numerology_insight_prompt(user_details, numerology_data, 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        # Palmistry for Person 1 (left)
        report_sections['person1_left_palm'] = await call_openai_api(
            get_palm_reading_prompt(user_details, left_palm_image_base64, 'left', 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        # Palmistry for Person 1 (right)
        report_sections['person1_right_palm'] = await call_openai_api(
            get_palm_reading_prompt(user_details, right_palm_image_base64, 'right', 'person1', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )

        # Numerology for Person 2
        report_sections['person2_numerology'] = await call_openai_api(
            get_numerology_insight_prompt(person2_details, numerology_data_p2, 'person2', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        # Palmistry for Person 2 (left)
        report_sections['person2_left_palm'] = await call_openai_api(
            get_palm_reading_prompt(person2_details, person2_left_palm_image_base64, 'left', 'person2', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )
        # Palmistry for Person 2 (right)
        report_sections['person2_right_palm'] = await call_openai_api(
            get_palm_reading_prompt(person2_details, person2_right_palm_image_base64, 'right', 'person2', language, detailed=True),
            model=model_to_use, max_tokens=1500
        )

        # Couple-specific sections
        report_sections['relationship_compatibility'] = await call_openai_api(
            get_relationship_compatibility_prompt(user_details, numerology_data, numerology_data_p2, language),
            model=model_to_use, max_tokens=2000 # Longer for compatibility
        )
        report_sections['combined_path_purpose'] = await call_openai_api(
            get_couple_sectional_prompt('combined_path_purpose', user_details, numerology_data, numerology_data_p2, language),
            model=model_to_use, max_tokens=1000
        )
        report_sections['challenges_growth'] = await call_openai_api(
            get_couple_sectional_prompt('challenges_growth', user_details, numerology_data, numerology_data_p2, language),
            model=model_to_use, max_tokens=1000
        )
        report_sections['shared_future_outlook'] = await call_openai_api(
            get_couple_sectional_prompt('shared_future_outlook', user_details, numerology_data, numerology_data_p2, language),
            model=model_to_use, max_tokens=1200
        )
        report_sections['conclusion_couple'] = await call_openai_api(
            get_couple_sectional_prompt('conclusion_couple', user_details, numerology_data, numerology_data_p2, language),
            model=model_to_use, max_tokens=600
        )

    return report_sections

if __name__ == '__main__':
    import asyncio
    from dotenv import load_dotenv
    from numerology import get_numerology_insights # Assuming numerology.py is in the same dir

    load_dotenv()

    async def test_gpt_module():
        # --- Individual Test Data ---
        user_test_details_individual = {
            "name": "Aisha Khan",
            "dob": "1992-07-21",
            "gender": "female",
            "person1_name": "Aisha Khan", # For consistency with couple data structure
            "person1_dob": "1992-07-21",
            "person1_gender": "female"
        }
        numerology_test_data_individual = get_numerology_insights(user_test_details_individual['dob'], user_test_details_individual['name'])

        # --- Couple Test Data ---
        user_test_details_couple = {
            "person1_name": "Arjun Sharma",
            "person1_dob": "1990-05-15",
            "person1_gender": "male",
            "person2_name": "Priya Verma",
            "person2_dob": "1991-03-22",
            "person2_gender": "female"
        }
        numerology_test_data_p1 = get_numerology_insights(user_test_details_couple['person1_dob'], user_test_details_couple['person1_name'])
        numerology_test_data_p2 = get_numerology_insights(user_test_details_couple['person2_dob'], user_test_details_couple['person2_name'])

        # A tiny blank image base64 for testing (replace with actual image data for real AI test)
        dummy_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        print("--- Testing Individual Report Content Generation (Premium sections forced) ---")
        individual_content = await generate_full_report_content(
            user_test_details_individual, numerology_test_data_individual,
            dummy_image_base64, dummy_image_base64,
            language='en', report_type='individual' # 'individual' report
        )
        for section, content in individual_content.items():
            print(f"\n--- {section.upper()} (Individual) ---")
            print(content[:500] + "..." if len(content) > 500 else content) # Print first 500 chars

        print("\n--- Testing Couple Report Content Generation ---")
        couple_content = await generate_full_report_content(
            user_test_details_couple, numerology_test_data_p1,
            dummy_image_base64, dummy_image_base64,
            language='en', report_type='couple', # 'couple' report
            person2_details=user_test_details_couple, # Pass the same dict, gpt.py extracts p2 data
            numerology_data_p2=numerology_test_data_p2,
            person2_left_palm_image_base64=dummy_image_base64,
            person2_right_palm_image_base64=dummy_image_base64
        )
        for section, content in couple_content.items():
            print(f"\n--- {section.upper()} (Couple) ---")
            print(content[:500] + "..." if len(content) > 500 else content) # Print first 500 chars


    asyncio.run(test_gpt_module())