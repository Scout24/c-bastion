# -*- coding: UTF-8 -*-

import unittest
from mock import patch, Mock
import os
import tempfile
import shutil
import stat
from c_bastion import index
from c_bastion.index import (store_pubkey,
                             username_valid,
                             check_and_add,
                             create_user_with_key,
                             )


class TestUsernameValid(unittest.TestCase):

    def test_username_happy_path(self):
        self.assertTrue(username_valid("monty"))

    def test_username_exception_on_root(self):
        self.assertFalse(username_valid("root"))

    def test_username_exception_on_filepath(self):
        self.assertFalse(username_valid("/"))

    def test_username_exception_on_non_text_chars(self):
        self.assertFalse(username_valid("%$§"))

    def test_username_exception_on_umlaut(self):
        self.assertFalse(username_valid("mönty"))


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch('sh.chown')
    def test_store_pubkey(self, chown_mock):
        store_pubkey('foo', self.tempdir, 'abc')
        chown_mock.assert_called_once_with('-R', 'foo:foo', self.tempdir)
        authorized_keys_file = os.path.join(self.tempdir,
                                            '.ssh/authorized_keys')
        authorized_keys = open(authorized_keys_file).read()
        self.assertEqual(authorized_keys, 'abc\n')
        file_stat = os.stat(authorized_keys_file).st_mode
        access = file_stat & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        self.assertEqual(access, 0o0600)

        ssh_dir = os.path.join(self.tempdir, '.ssh')
        filestat_ssh = os.stat(ssh_dir).st_mode
        access = filestat_ssh & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        self.assertEqual(access, 0o0700)


    @patch('c_bastion.index.username_exists')
    @patch('c_bastion.index.useradd')
    def test_check_and_add_works_with_no_user(self,
                                              useradd_mock,
                                              username_exists_mock,
                                              ):
        username_exists_mock.return_value = False
        self.assertTrue(check_and_add('auser'))
        useradd_mock.called_once_with('auser')

    @patch('c_bastion.index.username_exists')
    @patch('c_bastion.index.useradd')
    def test_check_and_add_works_with_existing_user(self,
                                                    useradd_mock,
                                                    username_exists_mock,
                                                    ):
        username_exists_mock.return_value = True
        self.assertFalse(check_and_add('auser'))
        useradd_mock.calls = 0


    @patch("c_bastion.index.username_from_request", Mock(return_value=None))
    def test_create_user_with_key_fails_for_missing_username(self):
        self.assertEqual(create_user_with_key(),
                         {'error': "Parameter 'username' not specified"})
        self.assertEqual(index.response.status, '422 Unprocessable Entity')


    @patch("c_bastion.index.username_from_request", Mock(return_value='any_user'))
    @patch("c_bastion.index.request")
    def test_create_user_with_key_fails_for_missing_pubkey(self, json_mock):
        json_mock.json.get.return_value = None
        self.assertEqual(create_user_with_key(),
                         {'error': "Parameter 'pubkey' not specified"})
        self.assertEqual(index.response.status, '422 Unprocessable Entity')
