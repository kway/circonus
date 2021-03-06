#!/usr/bin/env python

# pylint: disable=W0212

from uuid import uuid4

import unittest

from circonus import CirconusClient, tag, util
from circonus.client import API_BASE_URL, get_api_url


class CirconusClientTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_app_name = "TEST"
        cls.api_token = str(uuid4())
        cls.c = CirconusClient(cls.api_app_name, cls.api_token)

    def test_api_headers(self):
        expected = {
            "Accept": "application/json",
            "X-Circonus-App-Name": self.api_app_name,
            "X-Circonus-Auth-Token": self.api_token
        }
        actual = self.c.api_headers
        self.assertEqual(expected, actual)

    def test_get_api_url(self):
        expected = API_BASE_URL + "/path/to/resource"
        self.assertEqual(expected, get_api_url("path/to/resource"))
        self.assertEqual(expected, get_api_url("path/to/resource/"))
        self.assertEqual(expected, get_api_url("/path/to/resource"))
        self.assertEqual(expected, get_api_url("/path/to/resource/"))


class UtilTestCase(unittest.TestCase):

    def test_get_resource_from_cid(self):
        expected = "check"
        cid = "%s/123456" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))
        cid = "/%s/123456" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))
        cid = "/%s/123456/" % expected
        self.assertEqual(expected, util.get_resource_from_cid(cid))

    def test_get_check_id_from_cid(self):
        expected = 123456
        cid = "/check_bundle/%d" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))
        cid = "check_bundle/%d" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))
        cid = "check_bundle/%d/" % expected
        self.assertEqual(expected, util.get_check_id_from_cid(cid))


class TagTestCase(unittest.TestCase):

    def test_get_updated_tags(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        new_tags = ["cat:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        self.assertItemsEqual(existing_tags + new_tags, tag._get_updated_tags(set.union, check_bundle, new_tags))
        self.assertItemsEqual(new_tags, tag._get_updated_tags(set.union, {"tags": []}, new_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, existing_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, [existing_tags[0]]))
        self.assertIsNone(tag._get_updated_tags(set.union, check_bundle, []))
        self.assertIsNone(tag._get_updated_tags(set.union, {"tags": []}, []))
        self.assertIsNone(tag._get_updated_tags(set.union, {}, new_tags))
        self.assertIsNone(tag._get_updated_tags(set.union, {}, []))

        remove_tags = ["environment:development"]
        expected = ["region:us-east-1"]
        self.assertItemsEqual(expected, tag._get_updated_tags(set.difference, check_bundle, remove_tags))
        self.assertItemsEqual([existing_tags[1]], tag._get_updated_tags(set.difference, check_bundle,
                                                                        [existing_tags[0]]))
        self.assertEqual([], tag._get_updated_tags(set.difference, check_bundle, existing_tags))
        self.assertIsNone(tag._get_updated_tags(set.difference, check_bundle, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, check_bundle, ["test:new"]))
        self.assertIsNone(tag._get_updated_tags(set.difference, {"tags": []}, ["test:new"]))
        self.assertIsNone(tag._get_updated_tags(set.difference, {"tags": []}, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, remove_tags))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, []))
        self.assertIsNone(tag._get_updated_tags(set.difference, {}, ["test:new"]))

    def test_get_tags_with(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        tags = ["cat:tag"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        self.assertItemsEqual(existing_tags + tags, tag.get_tags_with(check_bundle, tags))
        self.assertItemsEqual(tags, tag.get_tags_with({"tags": []}, tags))
        self.assertIsNone(tag.get_tags_with(check_bundle, existing_tags))
        self.assertIsNone(tag.get_tags_with(check_bundle, [existing_tags[0]]))
        self.assertIsNone(tag.get_tags_with(check_bundle, []))
        self.assertIsNone(tag.get_tags_with({"tags": []}, []))
        self.assertIsNone(tag.get_tags_with({}, tags))
        self.assertIsNone(tag.get_tags_with({}, []))

    def test_get_tags_without(self):
        existing_tags = ["environment:development", "region:us-east-1"]
        tags = ["environment:development"]
        check_bundle = {"_checks": ["/check/92625"],
                        "_cid": "/check_bundle/70681",
                        "_created": 1403892322,
                        "_last_modified": 1416419829,
                        "_last_modified_by": "/user/2640",
                        "brokers": ["/broker/301"],
                        "config": {"acct_id": "999",
                                   "api_key": "deadbeef",
                                   "application_id": "999"},
                        "display_name": "Service",
                        "metrics": [{"name": "DB", "status": "active", "type": "numeric"}],
                        "notes": None,
                        "period": 60,
                        "status": "active",
                        "tags": existing_tags,
                        "target": "10.1.2.3",
                        "timeout": 10,
                        "type": "newrelic_rpm"}
        expected = ["region:us-east-1"]
        self.assertItemsEqual(expected, tag.get_tags_without(check_bundle, tags))
        self.assertItemsEqual([existing_tags[1]], tag.get_tags_without(check_bundle, [existing_tags[0]]))
        self.assertEqual([], tag.get_tags_without(check_bundle, existing_tags))
        self.assertIsNone(tag.get_tags_without(check_bundle, []))
        self.assertIsNone(tag.get_tags_without(check_bundle, ["test:new"]))
        self.assertIsNone(tag.get_tags_without({"tags": []}, ["test:new"]))
        self.assertIsNone(tag.get_tags_without({"tags": []}, []))
        self.assertIsNone(tag.get_tags_without({}, tags))
        self.assertIsNone(tag.get_tags_without({}, []))
        self.assertIsNone(tag.get_tags_without({}, ["test:new"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
