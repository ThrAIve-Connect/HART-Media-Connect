from flask import Flask, request, render_template, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import openai
import random
import os

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Template directory for font and style assets
TEMPLATE_DIR = "templates"

# Load available fonts
fonts = {
    "header": os.path.join(TEMPLATE_DIR, "BoldFont.ttf"),
    "body": os.path.join(TEMPLATE_DIR, "RegularFont.ttf")
}

# Route for the homepage with form
@app.route('/')
def index():
    return render_template('index.html')

# Route to process form data and generate flyer
@app.route('/generate-flyer', methods=['POST'])
def generate_flyer():
    try:
        # Get user input: description and uploaded images
        description = request.form.get('description')
        images = request.files.getlist('images')

        # Step 1: Enhance description text using GPT
        prompt = f"Write an engaging, catchy description based on this context: {description}"
        ai_response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        enhanced_text = ai_response['choices'][0]['text'].strip()

        # Step 2: Choose a random template layout
        template_choice = random.choice(["template1", "template2", "template3"])

        # Step 3: Create the flyer image
        flyer_image = create_flyer(images, enhanced_text, template_choice)

        # Save the flyer to a BytesIO object to serve directly
        flyer_io = io.BytesIO()
        flyer_image.save(flyer_io, format="JPEG")
        flyer_io.seek(0)

        # Return the generated flyer image as a downloadable file
        return send_file(flyer_io, mimetype='image/jpeg', as_attachment=True, download_name="flyer.jpg")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_flyer(images, text, template):
    # Load a background or start a blank image
    flyer_bg = Image.new("RGB", (1080, 1080), "white")

    # Position images based on template
    for idx, image_file in enumerate(images):
        img = Image.open(image_file)
        img.thumbnail((500, 500))

        # Example image positions for different templates
        if template == "template1":
            flyer_bg.paste(img, (50 + idx * 550, 200))  # Top row layout
        elif template == "template2":
            flyer_bg.paste(img, (100, 200 + idx * 600))  # Column layout
        elif template == "template3":
            flyer_bg.paste(img, (150 + idx * 450, 400))  # Diagonal layout

    # Add text overlay
    draw = ImageDraw.Draw(flyer_bg)

    # Header and body font sizes
    header_font = ImageFont.truetype(fonts["header"], size=60)
    body_font = ImageFont.truetype(fonts["body"], size=40)

    # Draw text in template-specific positions
    if template == "template1":
        draw.text((100, 50), "Event", fill="black", font=header_font)
        draw.text((100, 850), text, fill="black", font=body_font)
    elif template == "template2":
        draw.text((100, 50), "Special Event", fill="black", font=header_font)
        draw.text((100, 900), text, fill="black", font=body_font)
    elif template == "template3":
        draw.text((100, 50), "Join Us", fill="black", font=header_font)
        draw.text((100, 850), text, fill="black", font=body_font)

    return flyer_bg

if __name__ == '__main__':
    app.run(debug=True)
