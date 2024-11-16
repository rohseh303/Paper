import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from mongoengine import connect, StringField
from Document import Document

app = Flask(__name__)

# Direct MongoEngine connection
connect(db="google-docs-clone", host="localhost", port=27017)

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

default_value = {}

# Helper function to find or create a document
def find_or_create_document(document_id):
    if document_id is None:
        return None
    document = Document.objects(_id=document_id).first()
    if document:
        print("Document found: ", document.data)
        return document
    else:
        print("Document not found, creating new document")
        return Document(_id=document_id, data=default_value).save()

# Handle socket connection and events
@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("get-document")
def handle_get_document(document_id):
    print("Document ID:", document_id)
    document = find_or_create_document(document_id)
    print("Document: ", document.data)
    join_room(document_id)
    print("room:", request.sid)
    emit("load-document", document.data, room=request.sid)

@socketio.on("send-changes")
def handle_send_changes(data, document_id):
    print("Sending changes:", data, document_id)
    
    # Extract the delta from the incoming data
    delta = data['ops']  # This is the structure you provided

    # Convert `delta` to a single text string if needed
    # Assuming `delta` is in the format of Quill's Delta
    content = "".join([op.get('insert', '') for op in delta if 'insert' in op])
    
    # Update the document in MongoDB
    print("Updating document:", content)
    Document.objects(_id=document_id).update_one(set__data=content)
    
    # Emit the changes to the room
    emit("receive-changes", data, room=document_id, include_self=False)

@socketio.on("save-document")
def handle_save_document(data, document_id):
    # Check for `document_id` and `ops` keys in the received data
    if not document_id not in data or 'ops' not in data:
        print("Error: Missing 'document_id' or 'ops' in data.")
        return

    # Convert `ops` to a single text string if needed
    ops = data['ops']
    content = "".join([op.get('insert', '') for op in ops if 'insert' in op]).strip()

    if not content:
        print(f"Ignoring save for document ID: {document_id} due to empty content.")
        return

    # Update the document in MongoDB with the Delta
    print("Saving document:", data, document_id)
    Document.objects(_id=document_id).update_one(set__data={"ops": ops})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3001)
