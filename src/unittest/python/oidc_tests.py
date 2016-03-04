import unittest
from mock import patch, Mock


from c_bastion.oidc import (validate_user_info,
                            fetch_user_info,
                            username_from_request,
                            )


class OIDCTestsValidateUserInfo(unittest.TestCase):

    def setUp(self):
        self.timegm_patcher = patch("c_bastion.oidc.timegm",
                                    Mock(return_value=3))
        self.timegm_patcher.start()
        self.auth_url_patcher = patch("c_bastion.oidc.AUTH_URL",
                                      'http://auth-server.example')
        self.auth_url_patcher.start()

    def tearDown(self):
        self.timegm_patcher.stop()
        self.auth_url_patcher.stop()

    @staticmethod
    def _make_user_info(aud='jumpauth',
                        exp=5,
                        iat=0,
                        iss=u'http://auth-server.example',
                        scope=[u'any_scope'],
                        sub=u'any_user'
                        ):

        return {u'aud': aud,
                u'exp': exp,
                u'iat': iat,
                u'iss': iss,
                u'scope': scope,
                u'sub': sub,
                }

    def test_validate_user_info_works(self):
        user_info = self._make_user_info()
        self.assertTrue(validate_user_info(user_info))

    def test_validate_user_info_fail_for_expired_token(self):
        user_info = self._make_user_info(exp=2)
        self.assertFalse(validate_user_info(user_info))

    def test_validate_user_info_fail_for_invalid_audience(self):
        user_info = self._make_user_info(aud='invalid_audience')
        self.assertFalse(validate_user_info(user_info))

    def test_validate_user_info_fail_for_incorrect_issuer(self):
        user_info = self._make_user_info(iss=u'http://no-auth-server.example')
        self.assertFalse(validate_user_info(user_info))


class TestFetchUserInfo(unittest.TestCase):

    @patch("c_bastion.oidc.request")
    @patch("c_bastion.oidc.AUTH_URL", 'http://auth-server.example')
    def test_fetch_user_info(self, request_mock):
        response_mock = Mock()
        response_mock.json.return_value = 'any_user_info'
        request_mock.return_value = response_mock
        token = 'any_old_access_token'
        user_info = fetch_user_info(token)
        self.assertEqual(user_info, 'any_user_info')
        request_mock.assert_called_once_with(
            'GET',
            'http://auth-server.example/oauth/user_info',
            headers={'Authorization': 'Bearer any_old_access_token'}
        )


class TestUsernameFromRequest(unittest.TestCase):

    def test_username_from_request_fails_for_missing_authorization_header(self):
        mock_http_request = Mock()
        mock_http_request.headers = {}
        self.assertIsNone(username_from_request(mock_http_request))

    def test_username_from_request_fails_for_invalid_authorization_header(self):
        mock_http_request = Mock()
        mock_http_request.headers = {'Authorization': 'RANDOM'}
        self.assertIsNone(username_from_request(mock_http_request))

    @patch('c_bastion.oidc.fetch_user_info')
    @patch('c_bastion.oidc.validate_user_info')
    def test_username_from_request_fails_for_missing_user_info(self,
                                                               validate_mock,
                                                               fetch_mock):
        mock_http_request = Mock()
        mock_http_request.headers = {'Authorization': 'Bearer any_access_token'}
        validate_mock.return_value = False
        self.assertIsNone(username_from_request(mock_http_request))

    @patch('c_bastion.oidc.fetch_user_info')
    @patch('c_bastion.oidc.validate_user_info')
    def test_username_from_request_succeds(self, validate_mock, fetch_mock):
        mock_http_request = Mock()
        mock_http_request.headers = {'Authorization':
                                     'Bearer any_access_token'}
        fetch_mock.return_value = {'sub': 'any_user'}
        validate_mock.return_value = True
        self.assertEqual('any_user', username_from_request(mock_http_request))

