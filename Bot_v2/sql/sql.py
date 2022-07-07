from sqlalchemy import create_engine
connection_string = "mysql+mysqlconnector://testing:JGVCDwuwXvmO@192.168.20.75/testing?charset=utf8mb4"

engine = create_engine(connection_string, echo=False)