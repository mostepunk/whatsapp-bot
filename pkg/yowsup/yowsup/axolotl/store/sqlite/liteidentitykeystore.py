from axolotl.state.identitykeystore import IdentityKeyStore
from axolotl.identitykey import IdentityKey
from axolotl.identitykeypair import IdentityKeyPair
from axolotl.util.keyhelper import KeyHelper
from axolotl.ecc.djbec import *
import sys
import logging
from threading import Lock


class LiteIdentityKeyStore(IdentityKeyStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        self.db_locker = Lock()
        dbConn.execute("CREATE TABLE IF NOT EXISTS identities (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "recipient_id INTEGER UNIQUE,"
                       "registration_id INTEGER, public_key BLOB, private_key BLOB,"
                       "next_prekey_id INTEGER, timestamp INTEGER);")

        if self.getLocalRegistrationId() is None or self.getIdentityKeyPair() is None:
            identity = KeyHelper.generateIdentityKeyPair()
            registration_id = KeyHelper.generateRegistrationId(True)
            self._storeLocalData(registration_id, identity)

    def getIdentityKeyPair(self):
        with self.db_locker:
            q = "SELECT public_key, private_key FROM identities WHERE recipient_id = -1"
            c = self.dbConn.cursor()
            c.execute(q)
            result = c.fetchone()

            if result:
                publicKey, privateKey = result
                return IdentityKeyPair(IdentityKey(DjbECPublicKey(publicKey[1:])), DjbECPrivateKey(privateKey))
            return None

    def getLocalRegistrationId(self):
        with self.db_locker:
            q = "SELECT registration_id FROM identities WHERE recipient_id = -1"
            c = self.dbConn.cursor()
            try:
                c.execute(q)
                result = c.fetchone()
                return result[0] if result else None
            except Exception as e:
                logging.exception(e)


    def _storeLocalData(self, registrationId, identityKeyPair):
        with self.db_locker:
            q = "INSERT INTO identities(recipient_id, registration_id, public_key, private_key) VALUES(-1, ?, ?, ?)"
            c = self.dbConn.cursor()
            pubKey = identityKeyPair.getPublicKey().getPublicKey().serialize()
            privKey = identityKeyPair.getPrivateKey().serialize()

            if sys.version_info < (2,7):
                pubKey = buffer(pubKey)
                privKey = buffer(privKey)

            try:
                c.execute(q, (registrationId,
                              pubKey,
                              privKey))

                self.dbConn.commit()
            except Exception as e:
                logging.exception(e)

    def saveIdentity(self, recipientId, identityKey):
        with self.db_locker:
            q = "DELETE FROM identities WHERE recipient_id=?"
            self.dbConn.cursor().execute(q, (recipientId,))
            self.dbConn.commit()


            q = "INSERT INTO identities (recipient_id, public_key) VALUES(?, ?)"
            c = self.dbConn.cursor()

            pubKey = identityKey.getPublicKey().serialize()
            try:
                c.execute(q, (recipientId, buffer(pubKey) if sys.version_info < (2,7) else pubKey))
                self.dbConn.commit()
            except Exception as e:
                logging.exception(e)

    def isTrustedIdentity(self, recipientId, identityKey):
        with self.db_locker:
            q = "SELECT public_key from identities WHERE recipient_id = ?"
            c = self.dbConn.cursor()
            try:
                c.execute(q, (recipientId,))
                result = c.fetchone()
                if not result:
                    return True

                pubKey = identityKey.getPublicKey().serialize()

                if sys.version_info < (2, 7):
                    pubKey = buffer(pubKey)

                return result[0] == pubKey
            except Exception as e:
                logging.exception(e)


