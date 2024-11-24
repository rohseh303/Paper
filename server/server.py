import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from mongoengine import connect, StringField
from Document import Document
import openai
from dotenv import load_dotenv
from openai import OpenAI
from model import FeedbackAgentSystem
import os

app = Flask(__name__)

# Direct MongoEngine connection
connect(db="google-docs-clone", host="localhost", port=27017)

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

default_value = {}

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI()

# Helper function to find or create a document
def find_or_create_document(document_id):
    if document_id is None:
        return None
    document = Document.objects(_id=document_id).first()
    if document:
        return document
    else:
        return Document(_id=document_id, data=default_value).save()

# Helper function to get all document IDs
def get_all_document_ids():
    return [doc._id for doc in Document.objects.only('_id')]  # Fetch only the IDs

# Handle socket connection and events
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    # Emit the list of document IDs to the client upon connection
    document_ids = get_all_document_ids()
    emit("document-list", document_ids)

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

    # # Use OpenAI's GPT to generate suggestions
    # prompt = f"Here is the text: '{selected_text}'."
    # if desired_changes:
    #     prompt += f" The user wants to see these changes: '{desired_changes}'."
    # prompt += " Please provide the updated text."

    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     max_tokens=150
    # )

    # suggestions = response.choices[0].message.content.strip()
    # print("Suggestions:", suggestions)

    agent_system = FeedbackAgentSystem()
    suggestions = agent_system.process_user_input(selected_text, desired_changes)  # Changed from .run
    
    emit('feedback', {'suggestions': suggestions})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3001)
