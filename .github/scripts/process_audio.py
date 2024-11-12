import os
import json
import openai
from firebase_admin import credentials, storage
import firebase_admin
from face_processor import FaceProcessor

class AudioProcessor:
    def __init__(self):
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        # Initialize OpenAI
        openai.api_key = os.environ['OPENAI_API_KEY']
        
        # Initialize face processor
        self.face_processor = FaceProcessor()
    
    def process_audio(self, audio_data):
        try:
            # Use GPT-4o mini for transcription and understanding
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data
            )
            
            # Process the transcription
            response = openai.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that processes photo-related queries."},
                    {"role": "user", "content": transcription.text}
                ]
            )
            
            # Check if it's a photo query
            query = transcription.text.lower()
            if "show" in query and ("picture" in query or "photo" in query):
                photos = self.face_processor.handle_query(query)
                return {
                    'status': 'success',
                    'type': 'photo_query',
                    'query': query,
                    'photos': photos,
                    'response': response.choices[0].message.content
                }
            
            return {
                'status': 'success',
                'type': 'general_query',
                'transcription': transcription.text,
                'response': response.choices[0].message.content
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)
    
    processor = AudioProcessor()
    
    if event['event_type'] == 'process_audio':
        result = processor.process_audio(event['client_payload']['audio_data'])
        print(json.dumps(result))
