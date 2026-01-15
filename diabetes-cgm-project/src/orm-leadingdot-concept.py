import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Use modern SQLAlchemy 2.0 base
Base = declarative_base()

class Customer(Base):
    # This exactly matches your requirement for leading dots
    # SQLite will create a table named: [sales.".customers"]
    __tablename__ = 'sales.".customers"' 
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# 2. Use 'echo=True' to see the generated SQL in your terminal
engine = create_engine('sqlite:///orm-leadingdot-check.sqlite.db', echo=True)

# 3. Create the table
Base.metadata.create_all(engine)

# 4. Verify insertion
Session = sessionmaker(bind=engine)
with Session() as session:
    new_user = Customer(full_name="Anitha Varghese")
    session.add(new_user)
    session.commit()
    print("\nSuccess! Data inserted into the dotted table.")