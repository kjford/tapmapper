from sqlalchemy import Integer, BigInteger, Column, DateTime, Float, String, Text
from sqlalchemy.dialects.mysql.types import TINYINT
from tapmapper.database import Base


class RateBeer(Base):
    __tablename__ = 'RateBeer'

    id = Column(Integer, primary_key=True)
    beer_brewerid = Column(Integer)
    review_time = Column(Integer)
    review_overall = Column(Float(asdecimal=True))
    review_text = Column(Text)
    review_aroma = Column(Float(asdecimal=True))
    review_appearance = Column(Float(asdecimal=True))
    review_profilename = Column(String(100))
    beer_style = Column(String(150))
    review_palate = Column(Float(asdecimal=True))
    review_taste = Column(Float(asdecimal=True))
    beer_name = Column(String(200))
    beer_abv = Column(Float(asdecimal=True))
    beer_beerid = Column(Integer)


class Beer(Base):
    __tablename__ = 'beers'

    id = Column(Integer, primary_key=True)
    brewerid = Column(Integer)
    beername = Column(String(200))
    styleid = Column(Integer)


class BeersUnique(Base):
    __tablename__ = 'beers_unique'

    id = Column(Integer, primary_key=True)
    ubeername = Column(String(200))


class Brewer(Base):
    __tablename__ = 'brewers'

    brewerid = Column(Integer, primary_key=True)
    brewername = Column(String(200))
    location = Column(String(200))


class Procbintweet(Base):
    __tablename__ = 'procbintweets'

    procbinid = Column(Integer, primary_key=True)
    proctweetid = Column(Integer)
    beerid = Column(Integer)
    cityid = Column(Integer)
    locbinid = Column(Integer)


class Processedtweet(Base):
    __tablename__ = 'processedtweets'

    proctwid = Column(Integer, primary_key=True)
    rawid = Column(BigInteger)
    tweetid = Column(BigInteger)
    tweetloc = Column(String(150))
    tweettext = Column(Text)
    tweettime = Column(DateTime)
    hasgeo = Column(TINYINT(1))
    beerid = Column(Integer)
    cityid = Column(Integer)


class Proctweet(Base):
    __tablename__ = 'proctweets'

    proctwid = Column(Integer, primary_key=True)
    rawid = Column(BigInteger)
    tweetid = Column(BigInteger)
    tweetloc = Column(String(150))
    tweettext = Column(Text)
    tweettime = Column(DateTime)
    hasgeo = Column(TINYINT(1))
    beerid = Column(Integer)


class Rawtweet(Base):
    __tablename__ = 'rawtweets'

    rawid = Column(BigInteger, primary_key=True)
    tweetid = Column(BigInteger)
    tweetloc = Column(String(150))
    tweettext = Column(Text)
    tweettime = Column(DateTime)
    hasgeo = Column(TINYINT(1))


class Revstat(Base):
    __tablename__ = 'revstats'

    id = Column(Integer, primary_key=True)
    nreviews = Column(Integer)
    avgoverall = Column(Float)


class Style(Base):
    __tablename__ = 'style'

    styleid = Column(Integer, primary_key=True)
    stylename = Column(String(200))


class Tfidf(Base):
    __tablename__ = 'tfidf'

    tfidfid = Column(Integer, primary_key=True)
    beerid = Column(Integer)
    locbinid = Column(Integer)
    TF = Column(Float(asdecimal=True))
    IDF = Column(Float(asdecimal=True))
    TFIDF = Column(Float)


class Uscity(Base):
    __tablename__ = 'uscities'

    cityid = Column(Integer, primary_key=True)
    city = Column(String(150))
    state = Column(String(2))
    fullname = Column(String(152))
    lat = Column(Float(asdecimal=True))
    lng = Column(Float(asdecimal=True))


class CityRegion(Base):
    __tablename__ = 'city_to_region'
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer)
    locbin_id = Column(Integer)


class Zips(Base):
    __tablename__ = 'zips'

    zip = Column(Integer, primary_key=True)
    state = Column(String(2))
    city = Column(String(16))
    lat = Column(Float(asdecimal=True))
    lng = Column(Float(asdecimal=True))

