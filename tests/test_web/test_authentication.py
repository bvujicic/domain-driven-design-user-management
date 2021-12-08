from fastapi import status


class TestAuthenticationAPI:
    uri_path = '/users/actions/login'

    def test_return_200(self, http_client, active_user, credentials):
        files = {
            'username': (None, active_user.username),
            'password': (None, credentials.plain_password),
        }
        response = http_client.post(self.uri_path, files=files)

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json().keys()

    def test_case_insensitive_return_200(self, http_client, active_user, credentials):
        files = {
            'username': (None, active_user.username.upper()),
            'password': (None, credentials.plain_password),
        }
        response = http_client.post(self.uri_path, files=files)

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json().keys()

    def test_user_inactive_return_400(self, http_client, user, credentials):
        files = {
            'username': (None, user.username),
            'password': (None, credentials.plain_password),
        }
        response = http_client.post(self.uri_path, files=files)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_password_return_400(self, http_client, active_user):
        files = {
            'username': (None, active_user.username),
            'password': (None, 'wrong_password'),
        }
        response = http_client.post(self.uri_path, files=files)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_username_does_not_exist_return_400(self, http_client, credentials):
        files = {
            'username': (None, 'wrong_username'),
            'password': (None, credentials.plain_password),
        }
        response = http_client.post(self.uri_path, files=files)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestInitiateChangePasswordAPI:
    uri_path = '/users/actions/password/initiate-change'

    def test_return_200(self, http_client, user):
        request = {'username': user.username}
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_username_does_not_exist_return_400(self, http_client, credentials):
        request = {'username': credentials.username}
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestChangePasswordAPI:
    uri_path = '/users/actions/password/change'

    def test_return_200(self, http_client, active_user, credentials, password_change_token):
        request = {'password_change_token': password_change_token, 'new_password': 'new_password'}
        response = http_client.post(f'{self.uri_path}', json=request)

        assert response.status_code == status.HTTP_200_OK

    def test_wrong_token_return_401(self, http_client, active_user, credentials, access_token):
        request = {'password_change_token': access_token, 'new_password': 'new_password'}
        response = http_client.post(f'{self.uri_path}', json=request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bad_token_return_401(self, http_client, active_user, credentials):
        request = {'password_change_token': 'wrong_token', 'new_password': 'new_password'}
        response = http_client.post(f'{self.uri_path}', json=request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestInitiateChangeUsernameAPI:
    uri_path = '/users/actions/username/initiate-change'

    def test_return_200(self, http_client, user, access_token):
        request = {'new_username': 'new_username@example.com'}
        response = http_client.post(self.uri_path, headers={'Authorization': f'Bearer {access_token}'}, json=request)

        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_username_already_exists_return_400(self, http_client, user, access_token, other_user):
        request = {'new_username': other_user.username}
        response = http_client.post(self.uri_path, headers={'Authorization': f'Bearer {access_token}'}, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestChangeUsernameAPI:
    uri_path = '/users/actions/username/change'

    def test_return_200(self, http_client, other_credentials, username_change_token, other_access_token):
        request = {'username_change_token': username_change_token}
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_200_OK

    def test_wrong_token_return_401(self, http_client, access_token):
        request = {'username_change_token': access_token}
        response = http_client.post(f'{self.uri_path}', json=request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bad_token_return_404(self, http_client):
        request = {'username_change_token': 'bad_token'}
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
