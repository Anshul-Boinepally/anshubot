import os
import json
import firebase_admin
from firebase_admin import credentials, storage
import openai

class AudioProcessor:
    def __init__(self):
        # Initialize Firebase
        cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-project-id.appspot.com'
        })
        
        # Initialize OpenAI
        openai.api_key = os.environ['OPENAI_API_KEY']
        
    def process_audio(self, audio_data):
        try:
            # Step 1: Transcribe audio using Whisper
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data
            )
            
            # Step 2: Process transcription with GPT-4o mini
            chat_response = openai.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",  # Updated to use GPT-4o mini
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": transcription.text}
                ],
                max_tokens=1000  # Limit output tokens to control costs
            )
            
            result = {
                'transcription': transcription.text,
                'response': chat_response.choices[0].message.content,
                'usage': {
                    'transcription_duration': len(audio_data) / 44100,  # Estimate duration in seconds
                    'prompt_tokens': chat_response.usage.prompt_tokens,
                    'completion_tokens': chat_response.usage.completion_tokens,
                    'total_tokens': chat_response.usage.total_tokens
                }
            }
            
            # Store result in Firebase
            bucket = storage.bucket()
            result_path = f'results/{transcription.id}.json'
            blob = bucket.blob(result_path)
            blob.upload_from_string(
                json.dumps(result),
                content_type='application/json'
            )
            
            return {'status': 'success', **result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)
    
    processor = AudioProcessor()
    
    if event['event_type'] == 'process_audio':
        result = processor.process_audio(event['client_payload']['audio_data'])
    elif event['event_type'] == 'process_dataset':
        # Handle dataset processing
        pass
    
    print(json.dumps(result))
