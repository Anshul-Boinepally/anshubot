import json
import os
import re
from datetime import datetime

class MessageProcessor:
    def __init__(self, identity_map):
        self.identity_map = identity_map
        
    def process_messages(self, message_data):
        """Process different types of message exports"""
        if message_data['name'].endswith('.txt'):
            # WhatsApp export
            return self._process_whatsapp(message_data)
        elif message_data['name'].endswith('.json'):
            # iMessage export
            return self._process_imessage(message_data)
        return []

    def _process_whatsapp(self, message_data):
        messages = []
        pattern = r'\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.+)'
        
        for line in message_data['content'].split('\n'):
            match = re.match(pattern, line)
            if match:
                timestamp_str, sender, content = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y, %H:%M:%S')
                
                # Map sender to identity
                sender_identity = self.identity_map.get(sender, {'name': sender, 'relationship': 'unknown'})
                
                messages.append({
                    'timestamp': timestamp.isoformat(),
                    'sender': sender_identity['name'],
                    'relationship': sender_identity['relationship'],
                    'content': content,
                    'source': 'whatsapp'
                })
        
        return messages

    def _process_imessage(self, message_data):
        messages = []
        data = json.loads(message_data['content'])
        
        for msg in data['messages']:
            sender = msg.get('sender', '')
            sender_identity = self.identity_map.get(sender, {'name': sender, 'relationship': 'unknown'})
            
            messages.append({
                'timestamp': msg.get('date'),
                'sender': sender_identity['name'],
                'relationship': sender_identity['relationship'],
                'content': msg.get('text', ''),
                'source': 'imessage'
            })
        
        return messages
