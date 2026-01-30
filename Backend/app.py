from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model and scaler
MODEL_PATH = r'S:\College\Mini Project\Phishing Dectection\Model\random_forest_model.pkl'
SCALER_PATH = r'S:\College\Mini Project\Phishing Dectection\Model\scaler.pkl'

model = pickle.load(open(MODEL_PATH, 'rb'))
scaler = pickle.load(open(SCALER_PATH, 'rb'))

def extract_features(url):
    features = []
    
    # 1. IP Address
    domain = url.split('/')[2]
    features.append(-1 if any(c.isdigit() for c in domain if c not in '.:') else 1)
    
    # 2. URL Length
    url_len = len(url)
    features.append(1 if url_len < 54 else (0 if url_len <= 75 else -1))
    
    # 3. Shortening Service
    features.append(-1 if any(x in url for x in ['tinyurl', 'bit.ly']) else 1)
    
    # 4. @ Symbol
    features.append(-1 if '@' in url else 1)
    
    # 5. Double slash
    features.append(-1 if url.count('//') > 1 else 1)
    
    # 6. Prefix/Suffix
    features.append(-1 if '-' in domain else 1)
    
    # 7. Sub domains
    dots = domain.count('.')
    features.append(1 if dots == 1 else (0 if dots == 2 else -1))
    
    # Fill remaining 23 features
    for i in range(23):
        features.append(0)
    
    return np.array(features).reshape(1, -1)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'No URL', 'status': 'error'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Get features and predict
        features = extract_features(url)
        features_scaled = scaler.transform(features)
        
        pred = model.predict(features_scaled)[0]
        proba = model.predict_proba(features_scaled)[0]
        
        # SIMPLE FIX: If confidence_phishing > confidence_legitimate, it's phishing
        is_phishing = proba[0] > proba[1]
        
        return jsonify({
            'url': url,
            'is_phishing': bool(is_phishing),
            'confidence_phishing': float(proba[0]),
            'confidence_legitimate': float(proba[1]),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
