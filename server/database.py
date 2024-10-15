import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

from config import MP3_DATA_DIR_PATH, DATABASE_FILE_PATH

Base = declarative_base()


class AudioFile(Base):
    __tablename__ = 'audio_files'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)  # Make sure to enforce non-null for essential fields
    file_path = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)


# Configuration of the database engine and session
engine = create_engine(f'sqlite:///{DATABASE_FILE_PATH}', echo=True)  # 'echo=True' is useful for debugging
Session = scoped_session(sessionmaker(bind=engine))


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class DatabaseManager:
    def __init__(self):
        Base.metadata.create_all(engine)

    def add_audio_file(self, file_name, user_id):
        session = Session()
        new_file = AudioFile(
            file_name=file_name,
            file_path=os.path.join(MP3_DATA_DIR_PATH, f"user_{user_id}", f"{file_name}"),
            user_id=user_id
        )
        session.add(new_file)
        session.commit()
        return new_file.id

    def get_audio_file(self, file_id, user_id):
        session = Session()
        return session.query(AudioFile).filter(
            AudioFile.id == file_id,
            AudioFile.user_id == user_id
        ).first()

    def list_audio_files(self, user_id):
        session = Session()
        return session.query(AudioFile).filter(
            AudioFile.user_id == user_id
        ).order_by(AudioFile.creation_date.desc()).all()
