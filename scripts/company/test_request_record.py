import unittest

from request_record import ATTACHMENT_TYPE, attachment_params, new_record, validate


class RequestRecordTests(unittest.TestCase):
    def test_new_project_valid(self):
        record = new_record("u1", "NEW_PROJECT", "Build a thing")
        self.assertIsNone(record["project_id"])
        self.assertNotIn("change_type", record)

    def test_modify_project_valid(self):
        record = new_record("u1", "MODIFY_PROJECT", "Fix it", project_id="p1", change_type="BUGFIX")
        params = attachment_params("t1", record)
        self.assertEqual(params["attachmentType"], ATTACHMENT_TYPE)
        self.assertEqual(params["identityKey"], record["request_id"])

    def test_rejections(self):
        bad = [
            dict(requested_by_user_id="", request_type="NEW_PROJECT", description="x"),
            dict(requested_by_user_id="u", request_type="OTHER", description="x"),
            dict(requested_by_user_id="u", request_type="NEW_PROJECT", description=" "),
            dict(requested_by_user_id="u", request_type="NEW_PROJECT", description="x", project_id="p"),
            dict(requested_by_user_id="u", request_type="NEW_PROJECT", description="x", change_type="BUGFIX"),
            dict(requested_by_user_id="u", request_type="MODIFY_PROJECT", description="x", project_id="p"),
            dict(requested_by_user_id="u", request_type="MODIFY_PROJECT", description="x", change_type="BUGFIX"),
            dict(requested_by_user_id="u", request_type="MODIFY_PROJECT", description="x", project_id="p", change_type="NOPE"),
            dict(requested_by_user_id="u", request_type="NEW_PROJECT", description="x", request_id="a" * 257),
        ]
        for kwargs in bad:
            with self.assertRaises(ValueError, msg=kwargs):
                new_record(**kwargs)

    def test_unknown_field_and_bad_date(self):
        record = new_record("u", "NEW_PROJECT", "x")
        with self.assertRaises(ValueError):
            validate({**record, "status": "OPEN"})
        with self.assertRaises(ValueError):
            validate({**record, "created_at": "yesterday"})


if __name__ == "__main__":
    unittest.main()
