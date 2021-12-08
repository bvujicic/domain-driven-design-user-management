from fastapi import status


class TestRegistrationAPI:
    uri_path = '/users/actions/registration'

    @staticmethod
    def get_user_input(credentials, enterprize):
        return {
            'email': credentials.username,
            'password': credentials.plain_password,
            'enterprize_subdomain': enterprize.subdomain,
        }

    def test_return_201(self, http_client, credentials, enterprize):
        request = self.get_user_input(credentials, enterprize)
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_201_CREATED
        assert {'email': credentials.username} == response.json()

    def test_preregistered_username_exists_return_201(
        self, http_client, credentials, preregistered_profile, enterprize
    ):
        request = self.get_user_input(credentials, enterprize)
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_201_CREATED
        assert {'email': credentials.username} == response.json()

    def test_user_already_exists_return_400(self, http_client, credentials, enterprize, active_user):
        request = self.get_user_input(credentials, enterprize)
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_case_insensitive_user_already_exists_return_400(self, http_client, credentials, enterprize, active_user):
        request = self.get_user_input(credentials, enterprize)
        request['email'] = credentials.username.upper()
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_already_exists_but_inactive_return_400(self, http_client, credentials, enterprize, user):
        request = self.get_user_input(credentials, enterprize)
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_enterprize_does_not_exist_return_400(self, http_client, credentials, enterprize):
        request = self.get_user_input(credentials, enterprize)
        request['enterprize_subdomain'] = f'wrong_{enterprize.subdomain}'
        response = http_client.post(self.uri_path, json=request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestActivationAPI:
    uri_path = '/users/actions/activation'

    def test_return_200(self, http_client, profile, profile_activation_token):
        user_input = {'activation_code': profile_activation_token}

        response = http_client.post(self.uri_path, json=user_input)

        assert response.status_code == status.HTTP_200_OK
        assert {'email': profile.user.username, 'is_active': True} == response.json()

    def test_invalid_activation_code_return_404(self, http_client):
        user_input = {'activation_code': 'invalid'}

        response = http_client.post(self.uri_path, json=user_input)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_already_active_return_400(self, http_client, active_profile_activation_token):
        user_input = {'activation_code': active_profile_activation_token}

        http_client.post(self.uri_path, json=user_input)
        response = http_client.post(self.uri_path, json=user_input)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
