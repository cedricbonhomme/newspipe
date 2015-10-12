from bootstrap import db


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def dump(self):
        return {key: getattr(self, key) for key in ('id', 'name', 'user_id')}
