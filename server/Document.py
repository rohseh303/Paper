from mongoengine import Document as MongoDocument, StringField, DictField

class Document(MongoDocument):
    _id = StringField(required=True, primary_key=True)
    data = DictField() 