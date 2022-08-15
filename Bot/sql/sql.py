from sqlalchemy import create_engine
from Bot.constants import DB_NAME, DB_ADDRESS, DB_USERNAME, DB_PASSWORD
connection_string = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(connection_string, echo=False)