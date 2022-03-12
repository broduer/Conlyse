from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from Bot_v2.sql.Models import Country, GameHasPlayer, Newspaper
from Bot_v2.sql.sql import engine


class Filler:
    def __init__(self, data):
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        self.data = data
        self.fillNewsPaper(data["newspaper"])
        self.session.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def fillNewsPaper(self, data):
        newspaper_all = [a for a in self.session.query(Newspaper).all()]
        countrys_all = [object_as_dict(c) for c in self.session.query(Country).join(GameHasPlayer).filter(
            GameHasPlayer.game_id == self.data["game"]["game_id"]).all()]

        articles_times = [a.time for a in newspaper_all]
        new_articles = list()
        for article in data:
            new = True
            article["country_id"] = [c for c in countrys_all if c["player_id"] == article.get("country_id")][0][
                "country_id"]
            for old_article in newspaper_all:
                if old_article.msg_typ == article.get("msg_typ") \
                        and int(old_article.time.timestamp()) == int(article.get("time").timestamp()) \
                        and old_article.country_id == article.get("country_id"):
                    new = False
            if new:
                new_articles.append(article)
        self.session.bulk_insert_mappings(Newspaper, new_articles)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
