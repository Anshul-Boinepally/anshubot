import os
import json

try:
    # Try to read and parse the credentials
    creds = os.environ.get('FIREBASE_CREDENTIALS', '')
    if not creds:
        print("❌ FIREBASE_CREDENTIALS environment variable is empty")
    else:
        # Try to parse as JSON
        json.loads(creds)
        print("✅ Firebase credentials are valid JSON")
        
except json.JSONDecodeError as e:
    print(f"❌ Firebase credentials are not valid JSON: {str(e)}")
    print("\nCredentials start with:", creds[:50] if creds else "EMPTY")
