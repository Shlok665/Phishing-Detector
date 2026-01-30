import requests
import json

# Test URLs
urls = {
    'Legitimate': [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.amazon.com',
        'https://www.facebook.com',
        'https://www.stackoverflow.com',
    ],
    'Phishing': [
        'https://www-amazon-verify-account.com',
        'https://secure-banking-confirm-identity.com',
        'https://microsoft-account-securityverify.com',
        'https://accounts-google-signin.com',
        'https://apple-support-verify-appleid.com',
    ]
}

API_URL = 'http://127.0.0.1:5000/predict'

print("=" * 80)
print("PHISHING DETECTOR - TEST RESULTS")
print("=" * 80)

results = {'legitimate': [], 'phishing': []}

for category, url_list in urls.items():
    print(f"\n🔍 Testing {category} URLs:")
    print("-" * 80)
    
    for url in url_list:
        try:
            response = requests.post(API_URL, json={'url': url})
            data = response.json()
            
            is_phishing = data['is_phishing']
            confidence_phishing = round(data['confidence_phishing'] * 100)
            confidence_legit = round(data['confidence_legitimate'] * 100)
            
            status = "⚠️ PHISHING" if is_phishing else "✅ SAFE"
            
            print(f"{status} | {url}")
            print(f"       └─ Phishing: {confidence_phishing}% | Legitimate: {confidence_legit}%")
            
            # Track results
            if category == 'Legitimate':
                results['legitimate'].append({
                    'url': url,
                    'correct': not is_phishing,
                    'confidence_safe': confidence_legit
                })
            else:
                results['phishing'].append({
                    'url': url,
                    'correct': is_phishing,
                    'confidence_phishing': confidence_phishing
                })
        
        except Exception as e:
            print(f"❌ ERROR | {url}")
            print(f"       └─ {str(e)}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

legit_correct = sum(1 for r in results['legitimate'] if r['correct'])
phishing_correct = sum(1 for r in results['phishing'] if r['correct'])
total_correct = legit_correct + phishing_correct
total_tests = len(results['legitimate']) + len(results['phishing'])

accuracy = (total_correct / total_tests) * 100

print(f"✅ Legitimate URLs Correctly Identified: {legit_correct}/{len(results['legitimate'])}")
print(f"✅ Phishing URLs Correctly Identified: {phishing_correct}/{len(results['phishing'])}")
print(f"\n📊 Overall Accuracy: {accuracy:.1f}% ({total_correct}/{total_tests})")
print("=" * 80)
