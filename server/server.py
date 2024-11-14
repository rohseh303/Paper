import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
from mongoengine import connect
from Document import Document  # Adjust this import based on your file structure

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
    join_room(document_id)
    emit("load-document", document.data, room=request.sid)

@socketio.on("send-changes")
def handle_send_changes(data):
    document_id, delta = data['document_id'], data['delta']
    emit("receive-changes", delta, room=document_id, include_self=False)

@socketio.on("save-document")
def handle_save_document(data):
    print("Saving document: ", data)
    document_id, content = data['document_id'], data['content']
    print(document_id, content)
    Document.objects(_id=document_id).update(data=content)

if __name__ == "__main__":
    print("Server is running on port 3001")
    socketio.run(app, host="0.0.0.0", port=3001)
