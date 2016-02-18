from web.models import db_create, db_empty, User, Article, Feed


def populate_db(db):
    role_admin, role_user = db_create(db)
    user1, user2 = [User(nickname=name, email="%s@test.te" % name,
                         pwdhash=name, roles=[role_user], enabled=True)
                    for name in ["user1", "user2"]]
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    for user in (user1, user2):
        for feed_name in ['feed1', 'feed2', 'feed3']:
            feed = Feed(link=feed_name, user_id=user.id,
                        title="%r %r" % (user.nickname, feed_name))
            db.session.add(feed)
            db.session.commit()
            for article in ['article1', 'article2', 'article3']:
                entry = "%s %s %s" % (user.nickname, feed.title, article)
                article = Article(entry_id=entry, link=article,
                                  feed_id=feed.id, user_id=user.id,
                                  title=entry, content=article)
                db.session.add(article)
            db.session.commit()

    db.session.commit()


def reset_db(db):
    db_empty(db)
