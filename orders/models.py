from mongoengine import *

connect('servo')

class Order(Document):
  def pk(self):
    return self._id

class User(Document):
  email = StringField(max_length=128, required=True)
  username = StringField(max_length=64, required=True)
  username = StringField(max_length=128, required=True)
  password = StringField(max_length=64, required=True)
  role = StringField(max_length=64, required=True)

class Issue(Document):
  symptom = StringField(required=True)
  diagnosis = StringField()
  solution = StringField()
  solved_at = DateTimeField()
  solved_by = ReferenceField(User)

class Message(Document):
  subject = StringField()
  body = StringField()
  sender = StringField()
  recipient = StringField()
