from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File, Response
from google.cloud import storage

from saas.core.config import configuration
from saas.database.models import ProfileRepository, PostRepository, EventRepository
from saas.domain.events import EventContent
from saas.domain.exceptions import UserDoesNotExist, EventDoesNotExist, PostDoesNotExist
from saas.domain.posts import PostContent
from saas.domain.users import Profile
from saas.service.event import create_event, delete_event
from saas.service.post import create_post, delete_news_post
from saas.service.profile import retrieve_profiles, invite_user_to_register, update_non_public_profile
from saas.web.security import get_admin_profile
from saas.web.serializers import (
    InviteUserRequest,
    InviteUserResponse,
    UserInvitationResponse,
    ListProfilesResponse,
    ProfileSerializer,
    CreatePostRequest,
    CreatePostResponse,
    ListUserInvitationsResponse,
    AdminDashboardResponse,
    CreateEventRequest,
    CreateEventResponse,
    RetrieveAdminProfileResponse,
    AdminUpdateProfileRequest,
    AdminUpdateProfileResponse,
)
from saas.web.session import profile_database, post_database, event_database

admin_router = APIRouter()


@admin_router.post(
    path='/users/actions/invitation',
    status_code=status.HTTP_200_OK,
    response_model=InviteUserResponse,
    name='Invite new user',
    tags=['administration'],
)
def invite_user_controller(
    request: 'InviteUserRequest',
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    admin_profile = invite_user_to_register(username=request.email, creator=admin_profile, repository=repository)

    return InviteUserResponse(email=admin_profile.user.username)


@admin_router.get(
    path='/users/actions/invitation',
    status_code=status.HTTP_200_OK,
    response_model=ListUserInvitationsResponse,
    name='List all invitations',
    tags=['administration'],
)
def list_invitations_controller(
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    profiles = repository.retrieve_invited_profiles_for_admin(admin_username=admin_profile.user.username)

    user_invitations_response = [
        UserInvitationResponse(
            email=profile.user.username,
            registered=bool(profile.user.password),
            activated=profile.user.is_active,
            invited=bool(profile.user.invited),
        )
        for profile in profiles
        if profile.user is not None
    ]
    return ListUserInvitationsResponse(invitations=user_invitations_response)


@admin_router.get(
    path='/users/profiles',
    status_code=status.HTTP_200_OK,
    response_model=ListProfilesResponse,
    name='List all user profiles',
    tags=['administration'],
)
def list_profiles_controller(
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    profiles = retrieve_profiles(admin_username=admin_profile.user.username, repository=repository)
    profiles_response = [
        ProfileSerializer(
            reference=profile.reference,
            first_name=profile.first_name,
            last_name=profile.last_name,
            email=profile.user.username if profile.user is not None else None,
            role=profile.user.type.name if profile.user is not None else None,
            activated=bool(profile.user.activated) if profile.user is not None else None,
            invited=bool(profile.user.invited) if profile.user is not None else None,
            street=profile.contact.address.street,
            town=profile.contact.address.town,
            zip_code=profile.contact.address.zip_code,
            country=profile.contact.address.country,
            phone_number=profile.contact.phone_number,
            position=profile.company_status.position,
            department=profile.company_status.department,
            photo_url=profile.photo_url,
            skills=profile.skills,
            descriptions=profile.descriptions,
            availability=profile.availability,
            motivation=profile.motivation,
            legal_status=profile.legal_status,
            exit_notes=profile.exit_notes,
            enter_date=profile.enter_date,
            exit_date=profile.exit_date,
        )
        for profile in profiles
    ]
    return ListProfilesResponse(profiles=profiles_response)


@admin_router.get(
    path='/users/profile/{profile_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveAdminProfileResponse,
    name='Retrieve user profile',
    tags=['administration'],
)
def retrieve_profile_controller(
    profile_id: str,
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    try:
        profile = repository.retrieve_profile(reference=profile_id)
    except UserDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    if admin_profile.enterprize is not profile.enterprize:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin permission required.',
        )

    return RetrieveAdminProfileResponse(
        reference=profile.reference,
        first_name=profile.first_name,
        last_name=profile.last_name,
        email=profile.user.username if profile.user is not None else None,
        gender=profile.gender,
        birthdate=profile.birthdate,
        role=profile.user.type.name if profile.user is not None else None,
        activated=bool(profile.user.activated) if profile.user is not None else None,
        invited=bool(profile.user.invited) if profile.user is not None else None,
        street=profile.contact.address.street,
        town=profile.contact.address.town,
        zip_code=profile.contact.address.zip_code,
        country=profile.contact.address.country,
        phone_number=profile.contact.phone_number,
        position=profile.company_status.position,
        department=profile.company_status.department,
        photo_url=profile.photo_url,
        skills=profile.skills,
        descriptions=profile.descriptions,
        availability=profile.availability,
        motivation=profile.motivation,
        legal_status=profile.legal_status,
        exit_notes=profile.exit_notes,
        enter_date=profile.enter_date,
        exit_date=profile.exit_date,
    )


@admin_router.put(
    path='/users/profile/{profile_id}',
    status_code=status.HTTP_200_OK,
    response_model=AdminUpdateProfileResponse,
    name='Update non-public user profile',
    tags=['administration'],
)
def update_non_public_profile_controller(
    profile_id: str,
    request: AdminUpdateProfileRequest,
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    try:
        profile = update_non_public_profile(profile_id=profile_id, repository=repository, **dict(request))
    except UserDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)

    return AdminUpdateProfileResponse.from_orm(profile)


@admin_router.post(
    path='/posts',
    status_code=status.HTTP_201_CREATED,
    response_model=CreatePostResponse,
    name='Create a news post',
    tags=['newsfeed'],
)
def create_post_controller(
    request: 'CreatePostRequest',
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'PostRepository' = Depends(post_database),
):
    content = PostContent(title=request.title, body=request.body)
    post = create_post(author=admin_profile, content=content, repository=repository)

    return CreatePostResponse(author=admin_profile.user.username, created=post.created)


@admin_router.delete(
    path='/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT, name='Delete a news post', tags=['newsfeed']
)
def delete_news_post_controller(
    post_id: str,
    admin_profile: Profile = Depends(get_admin_profile),
    repository: PostRepository = Depends(post_database),
):
    try:
        delete_news_post(news_post_id=post_id, admin_username=admin_profile.username, repository=repository)
    except PostDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.post(
    path='/events',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateEventResponse,
    name='Create an event',
    tags=['events'],
)
def create_event_controller(
    request: 'CreateEventRequest',
    admin_profile: 'Profile' = Depends(get_admin_profile),
    event_repo: 'EventRepository' = Depends(event_database),
):
    content = EventContent(
        title=request.title,
        body=request.body,
        location=request.location,
        starts_at=request.starts_at,
        ends_at=request.ends_at,
    )
    event = create_event(organizer=admin_profile, content=content, repository=event_repo)

    return CreateEventResponse(organizer=admin_profile.user.username, created=event.created)


@admin_router.delete(
    path='/events/{event_id}', status_code=status.HTTP_204_NO_CONTENT, name='Delete an event', tags=['events']
)
def delete_event_controller(
    event_id: str,
    admin_profile: Profile = Depends(get_admin_profile),
    repository: EventRepository = Depends(event_database),
):
    try:
        delete_event(event_id=event_id, admin_username=admin_profile.username, repository=repository)
    except EventDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.get(
    path='/dashboard',
    status_code=status.HTTP_200_OK,
    response_model=AdminDashboardResponse,
    name='Dashboard statistics',
    tags=['administration'],
)
def dashboard_controller(
    admin_profile: 'Profile' = Depends(get_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    dashboard_statistics = repository.retrieve_dashboard_statistics(admin_username=admin_profile.user.username)
    return dashboard_statistics


@admin_router.post(path='/users/actions/upload', status_code=status.HTTP_202_ACCEPTED)
def upload_file_controller(admin_profile: 'Profile' = Depends(get_admin_profile), document: UploadFile = File(...)):
    client = storage.Client()
    bucket = client.bucket(bucket_name=configuration.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)
    blob = storage.Blob(name=f'{admin_profile.enterprize.subdomain}/{document.filename}', bucket=bucket)
    blob.upload_from_file(file_obj=document.file, content_type=document.content_type)
    blob.make_private()
