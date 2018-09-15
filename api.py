import datetime
import jenkins
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseDB = declarative_base()

class User_Jobs(BaseDB):
    __tablename__ = 'User_Jobs'

    id = Column(Integer, primary_key = True)
    job_id = Column(Integer)
    name = Column(String)
    created_at = Column(DateTime)
    result = Column(String)
    building = Column(String)

def connect_jenkins(username, password):
    
    server = jenkins.Jenkins('http://localhost:8080', 
    username=username, password=password)
    return server

def initialize_DB():
    engine = create_engine('sqlite:///jenkins.db', echo=False)
    session = sessionmaker(bind=engine)()
    BaseDB.metadata.create_all(engine)
    return session

def get_last_job_id(session, name):
    try:
        last_job = session.query(User_Jobs).filter_by(name=name).order_by(User_Jobs.job_id.desc()).first()
        return last_job.job_id
    except:
        return None

def add_jobs(start_build_number, last_build_number, jobName,session):

    for curr_build_number in range(start_build_number , last_build_number ):
        current = server.get_build_info(jobName, curr_build_number)
        curr_job = User_Jobs()
        curr_job.job_id = current['id']
        curr_job.building = current['building']
        curr_job.name = jobName
        curr_job.result = current['result']
        curr_job.created_at = datetime.datetime.fromtimestamp(long(current['timestamp'])/1000)
        session.add(curr_job)

    session.commit()


username = raw_input('Enter username: ')
password = raw_input('Enter password: ')
server = connect_jenkins(username, password)

try:
    server.get_whoami()
    session = initialize_DB()
    jobs = server.get_all_jobs()

    for curr_job in jobs:
        last_job_id = get_last_job_id(session, curr_job['name'] ) 
        start_build_number = last_job_id + 1 if last_job_id else 1
        last_build_number = server.get_job_info(curr_job['name'] )['lastBuild']['number'] + 1
        add_jobs(start_build_number, last_build_number, curr_job['name'] ,session)
    print 'Done'
except:
    print 'Error'
    
