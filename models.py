from peewee import Model, IntegerField, TextField, BareField


class Config(Model):
    id = IntegerField(primary_key=True)
    api_id = IntegerField(null=True)
    api_hash = TextField(null=True)
    ibb_key = TextField(null=True)
    ibb_expiration = IntegerField(default=7)
    max_size = IntegerField(default=10)


class Chat(Model):
    id = IntegerField(primary_key=True)
    comment = TextField(null=True)
    ignore_users = BareField(null=True)
    channels = BareField(null=False)
