import os
import json
import firebase_admin
from firebase_admin import credentials, storage
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import cv2
import numpy as np

class PhotoProcessor:
    def __init__(self):
        # Initialize Firebase
        cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-project-id.appspot.com'
        })
        
        # Initialize Azure Face API
        self.face_client = FaceClient(
            os.environ['AZURE_FACE_ENDPOINT'],
            CognitiveServicesCredentials(os.environ['AZURE_FACE_KEY'])
        )
        
        # Initialize relationship mappings
        self.relationships = {
            'Anshul': 'boyfriend',
            'Aarya': 'me'
        }
    
    def process_photo(self, photo_data, photo_path):
        try:
            # Detect faces
            with open(photo_path, 'rb') as image:
                faces = self.face_client.face.detect_with_stream(
                    image,
                    detection_model='detection_03',
                    recognition_model='recognition_04'
                )
            
            # Store results
            result = {
                'path': photo_path,
                'faces': [
                    {
                        'id': face.face_id,
                        'rectangle': {
                            'top': face.face_rectangle.top,
                            'left': face.face_rectangle.left,
                            'width': face.face_rectangle.width,
                            'height': face.face_rectangle.height
                        }
                    } for face in faces
                ]
            }
            
            # Store in Firebase
            bucket = storage.bucket()
            blob = bucket.blob(f'photos/{os.path.basename(photo_path)}')
            blob.upload_from_filename(photo_path)
            
            # Store metadata
            metadata_blob = bucket.blob(f'metadata/{os.path.basename(photo_path)}.json')
            metadata_blob.upload_from_string(
                json.dumps(result),
                content_type='application/json'
            )
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)
    
    processor = PhotoProcessor()
    results = []
    
    if event['event_type'] == 'process_photos':
        for photo in event['client_payload']['photos']:
            result = processor.process_photo(photo['file'], photo['path'])
            results.append(result)
    
    print(json.dumps(results))
