import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from mongoengine import connect, StringField
from Document import Document
import openai

app = Flask(__name__)

# Direct MongoEngine connection
connect(db="google-docs-clone", host="localhost", port=27017)

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

default_value = {}

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key'

# Helper function to find or create a document
def find_or_create_document(document_id):
    if document_id is None:
        return None
    document = Document.objects(_id=document_id).first()
    if document:
        return document
    else:
        return Document(_id=document_id, data=default_value).save()

# Handle socket connection and events
@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("get-document")
def handle_get_document(document_id):
    document = find_or_create_document(document_id)
    print("Document ID:", document_id, " data: ", document.data)
    join_room(document_id)
    emit("load-document", document.data, room=request.sid)

@socketio.on("send-changes")
def handle_send_changes(data, document_id):
    # Extract the delta from the incoming data
    delta = data['ops']  # This is the structure you provided

    # Convert `delta` to a single text string if needed
    content = "".join([op.get('insert', '') for op in delta if 'insert' in op])
    
    # Update the document in MongoDB
    Document.objects(_id=document_id).update_one(set__data=content)
    
    # Emit the changes to the room
    emit("receive-changes", data, room=document_id, include_self=False)

@socketio.on("save-document")
def handle_save_document(data, document_id):
    # Check for `document_id` and `ops` keys in the received data
    if not document_id not in data or 'ops' not in data:
        return

    # Convert `ops` to a single text string if needed
    ops = data['ops']
    content = "".join([op.get('insert', '') for op in ops if 'insert' in op]).strip()

    if not content:
        return

    # Update the document in MongoDB with the Delta
    Document.objects(_id=document_id).update_one(set__data={"ops": ops})

@socketio.on("text-selection")
def handle_text_selection(data):
    document_id = data.get('documentId')
    selected_text = data.get('text')
    desired_changes = data.get('changes', '')
    
    if not document_id or not selected_text:
        return

    # Use OpenAI's GPT to generate suggestions
    prompt = f"Here is the text: '{selected_text}'."
    if desired_changes:
        prompt += f" The user wants to see these changes: '{desired_changes}'."
    prompt += " Please provide the updated text."

    response = openai.Completion.create(
        engine="text-davinci-003",  # You can choose a different engine if needed
        prompt=prompt,
        max_tokens=150
    )
    
    suggestions = response.choices[0].text.strip()

    # Emit the suggestions back to the client
    emit("text-suggestion", {"suggestions": suggestions}, room=document_id)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3001)
