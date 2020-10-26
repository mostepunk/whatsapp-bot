from axolotl.state.sessionstore import SessionStore
from axolotl.state.sessionrecord import SessionRecord
import sys
import logging
from threading import Lock
class LiteSessionStore(SessionStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        self.db_locker = Lock()
        dbConn.execute("CREATE TABLE IF NOT EXISTS sessions (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "recipient_id INTEGER UNIQUE, device_id INTEGER, record BLOB, timestamp INTEGER);")


    def loadSession(self, recipientId, deviceId):
        with self.db_locker:
            q = "SELECT record FROM sessions WHERE recipient_id = ? AND device_id = ?"
            c = self.dbConn.cursor()
            try:
                c.execute(q, (recipientId, deviceId))
                result = c.fetchone()

                if result:
                    return SessionRecord(serialized=result[0])
                else:
                    return SessionRecord()
            except Exception as e:
                logging.exception(e)

    def getSubDeviceSessions(self, recipientId):
        with self.db_locker:
            q = "SELECT device_id from sessions WHERE recipient_id = ?"
            c = self.dbConn.cursor()
            try:
                c.execute(q, (recipientId,))
                result = c.fetchall()

                deviceIds = [r[0] for r in result]
                return deviceIds
            except Exception as e:
                logging.exception(e)

    def storeSession(self, recipientId, deviceId, sessionRecord):
        self.deleteSession(recipientId, deviceId)
        with self.db_locker:

            q = "INSERT INTO sessions(recipient_id, device_id, record) VALUES(?,?,?)"
            c = self.dbConn.cursor()
            serialized = sessionRecord.serialize()
            # logging.info('RECIPIENT_ID - {} Serialized - {}'.format(recipientId, serialized))
            try:
                c.execute(q, (recipientId, deviceId, buffer(serialized) if sys.version_info < (2,7) else serialized))
                self.dbConn.commit()
            except Exception as e:
                logging.exception(e)

    def containsSession(self, recipientId, deviceId):
        with self.db_locker:
            q = "SELECT record FROM sessions WHERE recipient_id = ? AND device_id = ?"
            c = self.dbConn.cursor()
            try:
                c.execute(q, (recipientId, deviceId))
                result = c.fetchone()

                return result is not None
            except Exception as e:
                logging.exception(e)

    def deleteSession(self, recipientId, deviceId):
        with self.db_locker:
            q = "DELETE FROM sessions WHERE recipient_id = ? AND device_id = ?"
            self.dbConn.cursor().execute(q, (recipientId, deviceId))
            self.dbConn.commit()

    def deleteAllSessions(self, recipientId):
        with self.db_locker:
            q = "DELETE FROM sessions WHERE recipient_id = ?"
            self.dbConn.cursor().execute(q, (recipientId,))
            self.dbConn.commit()
