import sqlite3
import os

DB_NAME='analysis.db'
analysis_start_block=10000000 # TODO: decide proper start for this

class Contract():
    def __init__(self, creator, address, isEOA):
        self.creator = creator
        self.address = address
        self.created = 0
        self.isEOA = isEOA
        self.contractIncarnations = 0
        self.ephemeralIncarnations = 0
        self.exists = True
        self.invocations = 0
        self.aggregateGasUsage = 0

class DB():
    def __init__(self):
        pass

    @staticmethod
    def create_or_new():
        already_exists = False
        if os.path.exists(DB_NAME):
            already_exists = True

        db = DB()
        db.connection = sqlite3.connect(DB_NAME)
        db.cursor = db.connection.cursor()

        if not already_exists:
            print("creating new db")
            db.createHeadBlockTable()
            db.createCallTable()
            db.SetHeadBlockNumber(ANALYSIS_START_BLOCK) # no precompile calls happen until a bit after 49000
        else:
            print("opened existing db")

        return db

    def createContractTable(self):
        self.cursor.execute('''
                CREATE TABLE contract (
                    FOREIGN KEY(creator) REFERENCES contract(address),
                    address TEXT NOT NULL PRIMARY KEY,
                    created INTEGER,
                    isEOA BOOL,
                    contractIncarnations INTEGER,
                    ephemeralIncarnations INTEGER,
                    exists BOOL,
                    invocations BOOL,
                    aggregateGasUsage INTEGER,
                )''')
        self.connection.commit()

    def GetContract(self, address):
        pass

    def InsertContract(self, address):
        pass

    def createHeadBlockTable(self):
        self.cursor.execute('CREATE TABLE headblock (id TEXT NOT NULL, number TEXT NOT NULL, PRIMARY KEY (id) )')
        self.connection.commit()

    def SetHeadBlockNumber(self, number: int):
        self.head_number = number
        self.cursor.execute('REPLACE INTO headblock (id, number) values ("headblock", "{}")'.format(number))
        self.connection.commit()

    def HeadBlockNumber(self) -> int:
        result = self.cursor.execute('SELECT * FROM headblock').fetchall()
        return int(result[0][1])
