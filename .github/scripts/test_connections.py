import os
import json
import firebase_admin
from firebase_admin import credentials
import openai

def test_connections():
    try:
        # Test Firebase
        print("Testing Firebase connection...")
        cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase connection successful!")

        # Test OpenAI
        print("\nTesting OpenAI connection...")
        openai.api_key = os.environ['OPENAI_API_KEY']
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print("✅ OpenAI connection successful!")
        
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connections()
    if not success:
        exit(1)
