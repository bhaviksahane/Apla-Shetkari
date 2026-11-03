"""
AI Service Module for Apla Shetkari
Handles interactions with Google Gemini AI API for:
1. Agricultural Advisory Chatbot (English, Hindi, Marathi)
2. Intelligent Crop Recommendation Engine
"""

import json
import logging
import re
import requests
from config import Config

logger = logging.getLogger(__name__)

# Base Gemini API endpoint with verified working models and automatic fallback
GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

SYSTEM_PROMPT_CHATBOT = """
You are "Apla Shetkari AI" (आपला शेतकरी / Aapla Shetkari), an expert, compassionate, and experienced Indian Agricultural Advisor and Krishi Scientist.

Your Mission:
Help Indian farmers with clear, practical, accurate, and easy-to-implement agricultural guidance.

Core Guidelines:
1. Context & Tone:
   - Speak respectfully, warmly, and clearly like an experienced village agricultural officer or Krishi Vigyan Kendra (KVK) scientist.
   - Use simple language that a farmer with basic technical knowledge can readily understand.
   - Emphasize sustainable, cost-effective, and safe farming methods.

2. Indian Agricultural Conditions:
   - Understand Indian soil types (Black cotton/Regur, Alluvial, Red, Laterite, Sandy loam, Clayey).
   - Understand Indian seasons (Kharif, Rabi, Zaid/Summer) and major agro-climatic zones (Maharashtra, Punjab, MP, UP, Karnataka, Gujarat, etc.).
   - Tailor guidance according to the farmer's region, season, soil, and water availability.

3. Language Support:
   - Fluent in English, Hindi (हिंदी), and Marathi (मराठी).
   - If the user asks in Marathi, respond primarily in natural, authentic Marathi with clear Marathi agricultural terms (e.g., खरीप, रब्बी, काळी माती, खत व्यवस्थापन, कीड नियंत्रण).
   - If the user asks in Hindi, respond in fluent Hindi (हिंदी).
   - If the user asks in English or another language, respond in English.
   - If requested in a specific language, always follow that language preference.

4. Safety & Responsibility:
   - NEVER invent or guess chemical pesticide or dangerous chemical dosages. Recommend standard integrated pest management (IPM), neem oil / biological controls first, and if chemical is required, mention standard approved active ingredients or advise consulting the local Krishi Vigyan Kendra (KVK) / local Agriculture Extension Officer.
   - For serious crop diseases, wilt, or sudden epidemics, clearly advise the farmer to bring a physical leaf/root sample to the nearest KVK or Taluka Agricultural Officer (तालुका कृषी अधिकारी).

5. Formatting for Readability:
   - Use clear formatting with bullet points, bold key terms, numbered steps, and relevant emojis (🌱, 🌾, 💧, 🚜, 🐛, ☀️, ⚠️).
   - Keep answers structured: Problem Summary -> Actionable Steps / Solution -> Preventive Tips.
   - When key details (such as soil type, irrigation source, or plant stage) are missing, provide the general solution and ask 1-2 friendly follow-up questions to give more precise advice.

6. Scope:
   - Focus strictly on agriculture, farming, crops, soil, fertilizers, irrigation, cattle/dairy integration, weather planning, and government farmer schemes (PM-Kisan, PM Fasal Bima, etc.).
   - Politely steer off-topic non-farming questions back to agriculture.
"""

def check_api_key():
    """Checks whether a valid Gemini API key is configured."""
    key = Config.GEMINI_API_KEY
    if not key or key == 'your_gemini_api_key_here' or len(key) < 10:
        return False, (
            "⚠️ **Gemini API Key Required**\n\n"
            "To activate live AI farming guidance, please configure your free Gemini API key:\n"
            "1. Visit [Google AI Studio](https://aistudio.google.com/) and create a free API key.\n"
            "2. Open the `.env` file in the project directory.\n"
            "3. Set `GEMINI_API_KEY=your_actual_api_key`.\n"
            "4. Restart the web server.\n\n"
            "Once configured, Apla Shetkari will provide real-time AI agricultural advice in English, Hindi, and Marathi!"
        )
    return True, ""

def call_gemini_api(prompt, system_instruction=None, temperature=0.5):
    """
    Calls the Google Gemini REST API using available models in order of priority.
    Returns (success: bool, response_text: str).
    """
    is_valid, msg = check_api_key()
    if not is_valid:
        return False, msg

    api_key = Config.GEMINI_API_KEY
    headers = {"Content-Type": "application/json"}
    
    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"[SYSTEM INSTRUCTION / ROLE]:\n{system_instruction}\n\n[USER INSTRUCTION]:\n{prompt}"}]
        })
    else:
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2048,
            "topP": 0.95
        }
    }

    last_error = ""
    for model_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return True, parts[0].get("text", "")
                return False, "Received empty response from AI service. Please try again."
            elif response.status_code == 400:
                # Might be bad request or unsupported model
                err_data = response.json()
                last_error = err_data.get("error", {}).get("message", f"Bad Request ({response.status_code})")
                logger.warning(f"Gemini API 400 with model {model_name}: {last_error}")
            elif response.status_code in (404, 503):
                # Model not found or experiencing temporary demand spike, try next available model
                logger.info(f"Model {model_name} returned {response.status_code}, trying next model...")
                continue
            elif response.status_code == 429:
                return False, "⚠️ API quota or rate limit exceeded. Please wait a minute before sending another query."
            else:
                last_error = f"API error ({response.status_code}): {response.text[:200]}"
                logger.error(f"Gemini API error with {model_name}: {last_error}")
        except requests.exceptions.Timeout:
            last_error = "The AI service timed out. Please verify your internet connection and try again."
        except requests.exceptions.RequestException as e:
            last_error = f"Network communication error: {str(e)}"

    return False, f"⚠️ Unable to connect to AI Service: {last_error}"

def get_chat_response(user_message, language="English", chat_history=None):
    """
    Generates an agricultural advisory answer for a farmer's inquiry.
    Supports English, Hindi, and Marathi with language conditioning.
    """
    lang_prompt_modifier = ""
    if language.lower() in ("marathi", "mr"):
        lang_prompt_modifier = "IMPORTANT: Respond completely in clean, natural MARATHI (मराठी) with proper Devanagari script. Use common Marathi agricultural terms understandable by rural farmers in Maharashtra."
    elif language.lower() in ("hindi", "hi"):
        lang_prompt_modifier = "IMPORTANT: Respond completely in clean, natural HINDI (हिंदी) with proper Devanagari script. Use common Indian agricultural terms."
    else:
        lang_prompt_modifier = "Respond in clear English. If the user's question is in Hindi or Marathi, you may answer in their question's language or provide English with Hindi/Marathi terminology."

    # Build conversation context if available
    context_str = ""
    if chat_history and len(chat_history) > 0:
        context_str = "\n[RECENT CONVERSATION CONTEXT]:\n"
        # Take last 4 messages for context
        for turn in chat_history[-4:]:
            context_str += f"Farmer: {turn['user_message']}\nApla Shetkari AI: {turn['ai_response']}\n"

    full_prompt = f"""
{lang_prompt_modifier}
{context_str}
Farmer's Question:
"{user_message}"

Provide an empathetic, scientifically sound, and practical response formatted with bullet points and emojis.
"""
    return call_gemini_api(full_prompt, system_instruction=SYSTEM_PROMPT_CHATBOT, temperature=0.4)

def get_crop_recommendations_ai(state, district, soil_type, land_area, season, water_availability, previous_crop=None, language="English"):
    """
    Generates intelligent crop recommendations based on farmer's parameters.
    Returns: (success: bool, data: list of crop dictionaries, message: str)
    """
    is_valid, msg = check_api_key()
    if not is_valid:
        return False, [], msg

    lang_instruction = "English"
    if language.lower() in ("marathi", "mr"):
        lang_instruction = "Marathi (मराठी) with English crop names in parentheses"
    elif language.lower() in ("hindi", "hi"):
        lang_instruction = "Hindi (हिंदी) with English crop names in parentheses"

    prompt = f"""
You are an expert Indian Agronomist analyzing land for crop recommendations.

Parameters provided by the farmer:
- State: {state}
- District / Region: {district}
- Soil Type: {soil_type}
- Land Area: {land_area}
- Sowing Season: {season}
- Water / Irrigation Availability: {water_availability}
- Previous Crop Grown: {previous_crop or 'None / Fallow'}
- Preferred Response Language: {lang_instruction}

TASK:
Analyze these local agro-climatic conditions and recommend at least 3-4 best-suited, high-viability crops.
For each crop, provide realistic agricultural guidance tailored to Indian farming realities.

OUTPUT FORMAT:
Return ONLY a valid JSON array of objects (do NOT wrap in markdown explanation, just the raw JSON array or ```json ... ``` codeblock).
Each object must contain these exact keys:
[
  {{
    "crop_name": "Name of crop (e.g., Soybean / सोयाबीन)",
    "suitability_reason": "1-2 sentences explaining why this crop thrives in {soil_type} soil in {district}, {state} during {season}",
    "suitable_soil": "{soil_type} & related soil requirements",
    "growing_season": "{season} (Best Sowing Window: e.g. June 15 to July 10)",
    "water_requirement": "Specific irrigation frequency, drip suitability, or water needs matching '{water_availability}'",
    "cultivation_tips": "Key cultivation practices (Seed treatment, basal NPK fertilizer, spacing, weed control)",
    "expected_duration": "Duration in days/months (e.g. 90-105 Days)",
    "estimated_yield_market": "Expected average yield per acre and market demand overview",
    "pest_disease_alert": "Common pest or disease to watch out for and early preventive measure"
  }}
]
"""
    success, raw_text = call_gemini_api(prompt, system_instruction="You are an expert Indian agricultural scientist. Output only valid JSON.", temperature=0.3)
    if not success:
        return False, [], raw_text

    # Extract JSON array from response
    crops_list = parse_json_crops(raw_text)
    if crops_list and len(crops_list) >= 1:
        return True, crops_list, "Recommendations generated successfully."
    else:
        # If parsing JSON strictly failed, attempt to construct structured data or return error
        logger.warning(f"Could not parse JSON from Gemini response: {raw_text[:300]}")
        return False, [], "Could not format AI crop recommendations into structured cards. Please try submitting again."

def parse_json_crops(raw_text):
    """
    Robust JSON parser for extracting crop recommendation arrays from LLM response.
    Handles markdown code fences, leading/trailing text, and unicode.
    """
    text = raw_text.strip()
    
    # Try finding json code block
    match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Try finding bracket bounds
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx+1]

    try:
        data = json.loads(text)
        if isinstance(data, list):
            # Validate essential fields exist
            cleaned = []
            for item in data:
                if isinstance(item, dict) and "crop_name" in item:
                    cleaned.append({
                        "crop_name": item.get("crop_name", "Recommended Crop"),
                        "suitability_reason": item.get("suitability_reason", ""),
                        "suitable_soil": item.get("suitable_soil", "Compatible"),
                        "growing_season": item.get("growing_season", "Current Season"),
                        "water_requirement": item.get("water_requirement", "Moderate"),
                        "cultivation_tips": item.get("cultivation_tips", "Follow standard package of practices."),
                        "expected_duration": item.get("expected_duration", "90 - 120 Days"),
                        "estimated_yield_market": item.get("estimated_yield_market", "Good market demand"),
                        "pest_disease_alert": item.get("pest_disease_alert", "Monitor regularly for pests.")
                    })
            return cleaned
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
    return None
