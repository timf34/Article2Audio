from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

Base = declarative_base()


class AudioFile(Base):
    __tablename__ = 'audio_files'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)  # Make sure to enforce non-null for essential fields
    creation_date = Column(DateTime, default=datetime.utcnow)  # Timestamp for when the entry is created

# Configuration of the database engine and session
engine = create_engine('sqlite:///article2audio.db', echo=True)  # 'echo=True' is useful for debugging
Session = scoped_session(sessionmaker(bind=engine))


class DatabaseManager:
    def __init__(self):
        Base.metadata.create_all(engine)

    def add_audio_file(self, file_name):
        session = Session()
        new_file = AudioFile(file_name=file_name)
        session.add(new_file)
        session.commit()
        return new_file.id

    def get_audio_file(self, file_id):
        session = Session()
        return session.query(AudioFile).filter(AudioFile.id == file_id).first()

    def list_audio_files(self):
        session = Session()
        return session.query(AudioFile).order_by(AudioFile.creation_date.desc()).all()
