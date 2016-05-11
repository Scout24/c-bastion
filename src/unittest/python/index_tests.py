# -*- coding: UTF-8 -*-

import unittest
from mock import patch, Mock
import sh
import os
import tempfile
import shutil
import stat
from c_bastion import index
from c_bastion.index import (store_pubkey, check_username, check_and_add,
                             check_and_delete, delete_user, UsernameException,
                             create_user_with_key,
                             )


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

    def test_username_happy_path(self):
        self.assertIsNone(check_username("monty"))

    def test_username_exception_on_none(self):
        with self.assertRaises(UsernameException):
            check_username(None)

    def test_username_exception_on_root(self):
        with self.assertRaises(UsernameException):
            check_username("root")

    def test_username_exception_on_filepath(self):
        with self.assertRaises(UsernameException):
            check_username("/")

    def test_username_exception_on_non_text_chars(self):
        with self.assertRaises(UsernameException):
            check_username("%$§")

    def test_username_exception_on_umlaut(self):
        with self.assertRaises(UsernameException):
            check_username("mönty")

    @patch('c_bastion.index.username_exists')
    @patch('c_bastion.index.useradd')
    def test_check_and_add_successful(self,
                                      useradd_mock,
                                      username_exists_mock,
                                     ):
        username_exists_mock.return_value = False
        check_and_add('auser')
        useradd_mock.called_once_with('auser')


    @patch('c_bastion.index.username_exists')
    def test_check_and_add_user_exists(self, username_exists_mock):
        username_exists_mock.return_value = True
        self.assertRaises(UsernameException, check_and_add, 'auser')

    @patch('sh.id')
    @patch('sh.userdel', create=True)
    @patch('sh.pkill')
    def test_deletion_of_existing_user(self, pkill_mock, userdel_mock, id_mock):
        username = "MPython"
        check_and_delete(username)
        id_mock.assert_called_once_with(username)
        pkill_mock.assert_called_once_with('-u', username, '-9')
        userdel_mock.assert_called_once_with('-r', username)

    def test_deletion_throw_exception_for_nonexistant_user(self):
        with self.assertRaises(UsernameException):
            check_and_delete('MPython')

    @patch("c_bastion.index.username_from_request",
           Mock(return_value="MPython"))
    def test_delete_user_with_nonexistent_user(self):
        self.assertEqual(
            delete_user(), {'error': 'Username MPython does not exist.'})
        self.assertEqual(index.response.status, "400 Bad Request")

    @patch("c_bastion.index.username_from_request", Mock(return_value=None))
    def test_delete_user_with_bad_auth_response(self):
        self.assertEqual(delete_user(), {'error': 'Permission denied'})
        self.assertEqual(index.response.status, "403 Forbidden")

    @patch("c_bastion.index.username_from_request", Mock(return_value=None))
    def test_create_user_with_key_fails_for_missing_username(self):
        self.assertEqual(create_user_with_key(), {'error': 'Permission denied'})
        self.assertEqual(index.response.status, "403 Forbidden")


    @patch("c_bastion.index.username_from_request", Mock(return_value='any_user'))
    @patch("c_bastion.index.request")
    def test_create_user_with_key_fails_for_missing_pubkey(self, json_mock):
        json_mock.json.get.return_value = None
        self.assertEqual(create_user_with_key(),
                         {'error': 'Parameter \'pubkey\' not specified'})
        self.assertEqual(index.response.status, "400 Bad Request")
