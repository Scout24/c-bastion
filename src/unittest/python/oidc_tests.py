import unittest
from mock import patch, Mock


from c_bastion.oidc import validate_user_info


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
