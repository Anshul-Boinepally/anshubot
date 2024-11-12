import json
import os
from face_processor import FaceProcessor
from message_processor import MessageProcessor

def process_dataset(event_data):
    try:
        data = event_data['client_payload']['data']
        
        # Initialize processors
        face_processor = FaceProcessor()
        message_processor = MessageProcessor(data['identityMap'])
        
        # Process reference photos
        if data['references'].get('anshul'):
            face_processor.add_reference_photo(data['references']['anshul'], 'anshul')
        if data['references'].get('aarya'):
            face_processor.add_reference_photo(data['references']['aarya'], 'aarya')
        
        # Process photo collection
        processed_photos = []
        for photo in data['photos']:
            result = face_processor.process_photo(photo['content'])
            if result:
                result['metadata'] = photo['metadata']
                processed_photos.append(result)
        
        # Process messages
        processed_messages = []
        for message_file in data['messages']:
            messages = message_processor.process_messages(message_file)
            processed_messages.extend(messages)
        
        # Store results in Firebase
        store_results(processed_photos, processed_messages)
        
        return {
            'status': 'success',
            'photos_processed': len(processed_photos),
            'messages_processed': len(processed_messages)
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def store_results(photos, messages):
    # Initialize Firebase storage
    bucket = storage.bucket()
    
    # Store photos data
    photos_blob = bucket.blob('data/photos.json')
    photos_blob.upload_from_string(
        json.dumps(photos),
        content_type='application/json'
    )
    
    # Store messages data
    messages_blob = bucket.blob('data/messages.json')
    messages_blob.upload_from_string(
        json.dumps(messages),
        content_type='application/json'
    )

if __name__ == "__main__":
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)
    
    result = process_dataset(event)
    print(json.dumps(result))
