import pytest
from fastapi import status
from typing import Any

from saas.domain.users import UserAvailability, UserMotivation


@pytest.mark.xfail
class TestCreateEnterprizeAPI:
    uri_path = '/enterprizes'

    def test_create_success_201(self, http_client):
        enterprize_input = {'name': 'test', 'subdomain': 'test'}
        response = http_client.post(self.uri_path, json=enterprize_input)

        assert response.status_code == status.HTTP_201_CREATED
        assert {'subdomain': 'test'} == response.json()

    def test_create_subdomain_exists_400(self, http_client, enterprize):
        enterprize_input = {'name': enterprize.name, 'subdomain': enterprize.subdomain}
        response = http_client.post(self.uri_path, json=enterprize_input)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRetrieveProfileAPI:
    uri_path = '/profile'

    def test_retrieve_profile_unauthenticated_401(self, http_client):
        response = http_client.get(self.uri_path, headers={'Authorization': 'Bearer invalid'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_200(self, http_client, profile, access_token):
        response = http_client.get(self.uri_path, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert {
            'reference': profile.reference,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'email': profile.user.username,
            'gender': profile.gender,
            'birthdate': profile.birthdate,
            'activated': bool(profile.user.activated),
            'invited': bool(profile.user.invited),
            'street': profile.contact.address.street,
            'town': profile.contact.address.town,
            'zip_code': profile.contact.address.zip_code,
            'country': profile.contact.address.country,
            'phone_number': profile.contact.phone_number,
            'position': profile.company_status.position,
            'department': profile.company_status.department,
            'role': profile.user.type.name,
            'photo_url': profile.photo_url,
            'skills': profile.skills,
            'descriptions': profile.descriptions,
            'availability': profile.availability,
            'motivation': profile.motivation,
        } == response.json()


class TestUpdateProfileAPI:
    path = '/profile'
    request = {
        'phone_number': 'new_number',
        'street': 'new_street',
        'town': 'NewTown',
        'zip_code': 'n1234',
        'country': 'New',
        'position': 'new_position',
        'department': 'new_department',
        'skills': [{'test': 'test'}],
        'descriptions': ['test'],
        'availability': UserAvailability.available.value,
        'motivation': [UserMotivation.mentor.value, UserMotivation.lunch.value],
    }

    def test_update_200(self, http_client, profile, access_token):
        response = http_client.put(
            self.path,
            headers={'Authorization': f'Bearer {access_token}'},
            json=self.request,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_422(self, http_client, access_token):
        self.request['availability'] = 'not_permitted'
        response = http_client.put(
            self.path,
            headers={'Authorization': f'Bearer {access_token}'},
            json=self.request,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUploadPhotoAPI:
    path = '/profile/photo'

    @pytest.mark.xfail
    def test_upload_photo_200(self, http_client, photo, access_token):
        response = http_client.post(
            self.path,
            headers={'Authorization': f'Bearer {access_token}'},
            files={'photo': ('filename', photo)},
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestListPostsAPI:
    path = '/posts'

    def test_list_200(self, http_client, news_post, access_token):
        response = http_client.get(self.path, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert 'posts' in response.json()


class TestRetrievePostAPI:
    path = '/post'

    def test_retrieve_200(self, http_client, news_post, access_token):
        response = http_client.get(
            f'{self.path}/{news_post.reference}',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert {
            'reference': news_post.reference,
            'title': news_post.content.title,
            'body': news_post.content.body,
            'author': news_post.author.user.username,
            'created': news_post.created.isoformat(),
        } == response.json()


class TestListEventsAPI:
    path = '/events'

    def test_list_200(self, http_client, event, access_token):
        response = http_client.get(self.path, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert 'events' in response.json()
        assert event.reference == response.json()['events'][0]['reference']


class TestCreateQuestionAPI:
    path = '/questions'
    request: dict[str, Any] = {'title': 'New question', 'body': 'Question stuff'}

    def test_create_201(self, http_client, profile, access_token):
        response = http_client.post(self.path, headers={'Authorization': f'Bearer {access_token}'}, json=self.request)

        assert response.status_code == status.HTTP_201_CREATED
        assert {'id', 'author', 'created', 'tags'} == set(response.json().keys())
        assert response.json()['tags'] == []
        assert profile.user.username in response.json().values()

    def test_create_with_tags_201(self, http_client, profile, access_token):
        self.request['tags'] = ['tag1', 'tag2', 'tag3', 'tag1']
        response = http_client.post(self.path, headers={'Authorization': f'Bearer {access_token}'}, json=self.request)

        assert response.status_code == status.HTTP_201_CREATED
        assert {'id', 'author', 'created', 'tags'} == set(response.json().keys())
        assert set(response.json()['tags']) == {'tag1', 'tag2', 'tag3'}
        assert profile.user.username in response.json().values()


class TestCreateAnswerAPI:
    path = '/questions'
    request = {'title': 'New answer', 'body': 'Answer stuff'}

    def test_create_201(self, http_client, question, profile, access_token):
        response = http_client.post(
            f'{self.path}/{question.reference}', headers={'Authorization': f'Bearer {access_token}'}, json=self.request
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert {'id', 'question_id', 'author', 'created'} == set(response.json().keys())
        assert question.reference in response.json().values()
        assert profile.user.username in response.json().values()


class TestListQuestionAPI:
    path = '/questions'

    def test_list_200(self, http_client, question, access_token):
        response = http_client.get(self.path, headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == status.HTTP_200_OK
        assert {'questions'} == set(response.json().keys())


class TestRetrieveQuestionAPI:
    path = '/questions'

    def test_retrieve_200(self, http_client, question, access_token):
        response = http_client.get(
            f'{self.path}/{question.reference}', headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert question.reference in response.json().values()
        assert question.answers in response.json().values()
