import pytest
from fastapi import status


class TestInvitationAPI:
    uri_path = '/users/actions/invitation'
    username = 'boris@mail.com'
    request = {'email': username}

    def test_invitation_returns_invited_user_200(self, http_client, admin_access_token):
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': f'Bearer {admin_access_token}'},
            json=self.request,
        )
        assert response.status_code == status.HTTP_200_OK
        assert {'email': self.username} == response.json()

    def test_authentication_invalid_credentials_401(self, http_client):
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': 'Bearer invalid'},
            json=self.request,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forbidden_403(self, http_client, access_token):
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': f'Bearer {access_token}'},
            json=self.request,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_invitations_200(self, http_client, admin_access_token):
        response = http_client.get(self.uri_path, headers={'Authorization': f'Bearer {admin_access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert 'invitations' in response.json()


class TestListProfilesAPI:
    uri_path = '/users/profiles'

    def test_list_profiles_200(self, http_client, admin_access_token):
        response = http_client.get(self.uri_path, headers={'Authorization': f'Bearer {admin_access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert 'profiles' in response.json()

    def test_authentication_invalid_credentials_401(self, http_client):
        response = http_client.get(self.uri_path, headers={'Authorization': 'Bearer invalid'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forbidden_403(self, http_client, access_token):
        response = http_client.get(self.uri_path, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRetrieveProfileAPI:
    uri_path = '/users/profile'

    def test_retrieve_profile_200(self, http_client, active_profile, admin_access_token):
        response = http_client.get(
            f'{self.uri_path}/{active_profile.reference}', headers={'Authorization': f'Bearer {admin_access_token}'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert {
            'reference': active_profile.reference,
            'first_name': active_profile.first_name,
            'last_name': active_profile.last_name,
            'email': active_profile.user.username,
            'gender': active_profile.gender,
            'birthdate': active_profile.birthdate,
            'activated': bool(active_profile.user.activated),
            'invited': bool(active_profile.user.invited),
            'street': active_profile.contact.address.street,
            'town': active_profile.contact.address.town,
            'zip_code': active_profile.contact.address.zip_code,
            'country': active_profile.contact.address.country,
            'phone_number': active_profile.contact.phone_number,
            'position': active_profile.company_status.position,
            'department': active_profile.company_status.department,
            'role': active_profile.user.type.name,
            'photo_url': active_profile.photo_url,
            'skills': active_profile.skills,
            'descriptions': active_profile.descriptions,
            'availability': active_profile.availability,
            'motivation': active_profile.motivation,
            'legal_status': active_profile.legal_status,
            'exit_notes': active_profile.exit_notes,
            'enter_date': active_profile.enter_date,
            'exit_date': active_profile.exit_date,
        } == response.json()

    def test_authentication_invalid_credentials_401(self, http_client, user):
        response = http_client.get(f'{self.uri_path}/{user.reference}', headers={'Authorization': 'Bearer invalid'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forbidden_not_admin_403(self, http_client, profile, access_token):
        response = http_client.get(
            f'{self.uri_path}/{profile.reference}', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_forbidden_different_enterprize_403(self, http_client, other_profile, admin_access_token):
        response = http_client.get(
            f'{self.uri_path}/{other_profile.reference}', headers={'Authorization': f'Bearer {admin_access_token}'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_found_404(self, http_client, admin_access_token):
        response = http_client.get(
            f'{self.uri_path}/wrong_reference', headers={'Authorization': f'Bearer {admin_access_token}'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateNewsPostAPI:
    uri_path = '/posts'

    def test_return_201(self, http_client, admin_profile, admin_access_token, post_content):
        request = {'title': post_content.title, 'body': post_content.body}
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': f'Bearer {admin_access_token}'},
            json=request,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert admin_profile.user.username in response.json().values()

    def test_no_permission_return_403(self, http_client, access_token, post_content):
        request = {'title': post_content.title, 'body': post_content.body}
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': f'Bearer {access_token}'},
            json=request,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteNewsPostAPI:
    uri_path = '/posts'

    def test_return_204(self, http_client, news_post, admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/{news_post.reference}', headers={'Authorization': f'Bearer {admin_access_token}'}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert news_post.deleted is not None

    def test_not_found_return_404(self, http_client, admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/wrong_id', headers={'Authorization': f'Bearer {admin_access_token}'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_wrong_enterpize_return_404(self, http_client, news_post, other_admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/{news_post.reference}', headers={'Authorization': f'Bearer {other_admin_access_token}'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateEventAPI:
    uri_path = '/events'

    def test_return_201(self, http_client, admin_profile, admin_access_token, event_content):
        request = {
            'title': event_content.title,
            'body': event_content.body,
            'location': event_content.location,
            'starts_at': event_content.starts_at.isoformat(),
            'ends_at': event_content.ends_at.isoformat(),
        }
        response = http_client.post(
            self.uri_path, headers={'Authorization': f'Bearer {admin_access_token}'}, json=request
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert admin_profile.user.username in response.json().values()


class TestDeleteEventAPI:
    uri_path = '/events'

    def test_return_204(self, http_client, event, admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/{event.reference}', headers={'Authorization': f'Bearer {admin_access_token}'}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert event.deleted is not None

    def test_not_found_return_404(self, http_client, admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/wrong_id', headers={'Authorization': f'Bearer {admin_access_token}'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_wrong_enterpize_return_404(self, http_client, event, other_admin_access_token):
        response = http_client.delete(
            f'{self.uri_path}/{event.reference}', headers={'Authorization': f'Bearer {other_admin_access_token}'}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDashboardAPI:
    uri_path = '/dashboard'

    def test_retrieve_dashboard_200(self, http_client, admin_access_token):
        response = http_client.get(self.uri_path, headers={'Authorization': f'Bearer {admin_access_token}'})

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.xfail
class TestUploadFileAPI:
    uri_path = '/users/actions/upload'

    def test_upload_file_200(self, http_client, admin_access_token, test_file):
        response = http_client.post(
            self.uri_path,
            headers={'Authorization': f'Bearer {admin_access_token}'},
            files={'document': ('filename', test_file)},
        )
        assert response.status_code == status.HTTP_202_ACCEPTED


class TestUpdateProfileAPI:
    uri_path = '/users/profile'

    @staticmethod
    def user_input(enterprize_notes):
        return {
            'legal_status': enterprize_notes.legal_status.value,
            'exit_notes': enterprize_notes.exit_notes,
            'enter_date': enterprize_notes.enter_date.isoformat(),
            'exit_date': enterprize_notes.exit_date.isoformat(),
        }

    def test_return_200(self, http_client, profile, enterprize_notes, admin_access_token):
        request = self.user_input(enterprize_notes=enterprize_notes)
        response = http_client.put(
            f'{self.uri_path}/{profile.reference}',
            headers={'Authorization': f'Bearer {admin_access_token}'},
            json=request,
        )
        assert response.status_code == status.HTTP_200_OK
        assert profile.user.username in response.json().values()
        assert profile.exit_notes == enterprize_notes.exit_notes
        assert profile.enter_date == enterprize_notes.enter_date
        assert profile.exit_date == enterprize_notes.exit_date
        assert profile.legal_status == enterprize_notes.legal_status

    def test_profile_does_not_exist(self, http_client, profile, enterprize_notes, admin_access_token):
        request = self.user_input(enterprize_notes=enterprize_notes)
        response = http_client.put(
            f'{self.uri_path}/wrong_{profile.reference}',
            headers={'Authorization': f'Bearer {admin_access_token}'},
            json=request,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_forbidden_403(self, http_client, profile, enterprize_notes, access_token):
        request = self.user_input(enterprize_notes=enterprize_notes)
        response = http_client.put(
            f'{self.uri_path}/{profile.reference}', headers={'Authorization': f'Bearer {access_token}'}, json=request
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
