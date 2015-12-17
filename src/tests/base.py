import os
os.environ['PYAGG_TESTING'] = 'true'

import unittest
from bootstrap import db
import runserver
from tests.fixtures import populate_db, reset_db
from werkzeug.exceptions import NotFound


class BasePyaggTest(unittest.TestCase):
    _contr_cls = None

    def _get_from_contr(self, obj_id, user_id=None):
        return self._contr_cls(user_id).get(id=obj_id).dump()

    def _test_controller_rights(self, obj, user_id):
        obj_id = obj['id']
        self.assertEquals(obj, self._get_from_contr(obj_id))
        self.assertEquals(obj, self._get_from_contr(obj_id, user_id))
        # fetching non existent object
        self.assertRaises(NotFound, self._get_from_contr, 99, user_id)
        # fetching object with inexistent user
        self.assertRaises(NotFound, self._get_from_contr, obj_id, 99)
        # fetching object with wrong user
        self.assertRaises(NotFound, self._get_from_contr, obj_id, user_id + 1)
        self.assertRaises(NotFound, self._contr_cls().delete, 99)
        self.assertRaises(NotFound, self._contr_cls(user_id).delete, 99)
        self.assertEquals(obj['id'],
                self._contr_cls(user_id).delete(obj_id).id)
        self.assertRaises(NotFound, self._contr_cls(user_id).delete, obj_id)

    def setUp(self):
        populate_db(db)

    def tearDown(self):
        reset_db(db)


if __name__ == '__main__':
    unittest.main()
