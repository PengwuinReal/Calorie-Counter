import flask
from flask import render_template, request, jsonify
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import base64
import io
from api import get_nutrition

app = flask.Flask(__name__)

# Load the food classifier model
model = models.resnet50(pretrained=False, num_classes=101)
model.load_state_dict(torch.load('food101_model.pth', map_location=torch.device('cpu')))
model.eval()

# Define preprocessing transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Food classes
food_classes = [
    'apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare', 'beet_salad', 'beignets',
    'bibimbap', 'bread_pudding', 'breakfast_burrito', 'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad',
    'carrot_cake', 'ceviche', 'cheesecake', 'cheese_plate', 'chicken_curry', 'chicken_quesadilla', 'chicken_wings',
    'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder', 'club_sandwich', 'crab_cakes', 'creme_brulee',
    'croque_madame', 'cup_cakes', 'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict', 'escargots',
    'falafel', 'filet_mignon', 'fish_and_chips', 'foie_gras', 'french_fries', 'french_onion_soup', 'french_toast',
    'fried_calamari', 'fried_rice', 'frozen_yogurt', 'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich',
    'grilled_salmon', 'guacamole', 'gyoza', 'hamburger', 'hot_and_sour_soup', 'hot_dog', 'huevos_rancheros', 'hummus',
    'ice_cream', 'lasagna', 'lobster_bisque', 'lobster_roll_sandwich', 'macaroni_and_cheese', 'macarons', 'miso_soup',
    'mussels', 'nachos', 'omelette', 'onion_rings', 'oysters', 'pad_thai', 'paella', 'pancakes', 'panna_cotta',
    'peking_duck', 'pho', 'pizza', 'pork_chop', 'poutine', 'prime_rib', 'pulled_pork_sandwich', 'ramen', 'ravioli',
    'red_velvet_cake', 'risotto', 'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits', 'spaghetti_bolognese',
    'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake', 'sushi', 'tacos', 'takoyaki', 'tiramisu',
    'tuna_tartare', 'waffles'
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/classify', methods=['POST'])
def classify_image():
    try:
        # Get the image data from the request
        image_data = request.json['image']
        
        # Remove the data URL prefix
        image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transformations
        img_tensor = transform(image).unsqueeze(0)
        
        # Make prediction
        with torch.no_grad():
            output = model(img_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, predicted = torch.max(probabilities, 0)
        
        # Get the predicted class
        predicted_class = food_classes[predicted.item()]
        confidence_score = confidence.item()
        
        return jsonify({
            'success': True,
            'prediction': predicted_class,
            'confidence': round(confidence_score * 100, 2)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/analyze', methods=['POST'])
def get_calories():
    try:
        data = request.json
        food_name = data.get('food_name')
        if not food_name:
            return jsonify({'success': False,
                             'error': 'No food name provided'}), 400

        # Query your Spoonacular logic
        nutrition_info = get_nutrition(food_name)

        return jsonify({
            'success': True,
            'food_name': food_name,
            'nutrition': nutrition_info
        })

    except Exception as e:
        return jsonify({'success': False,
                         'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
