from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, status, Depends, HTTPException, File, UploadFile, Response

from saas.database.models import ProfileRepository, PostRepository, EventRepository
from saas.domain.exceptions import EnterprizeExists, PostDoesNotExist
from saas.domain.posts import PostContent
from saas.domain.users import User, Profile
from saas.service.enterprize import create_enterprize
from saas.service.event import list_events_by_enterprize
from saas.domain.exceptions import EnterprizeExists, PostDoesNotExist
from saas.service.post import post_question, create_answer
from saas.service.profile import update_profile, upload_user_photo, delete_user_photo
from saas.web.security import get_profile, get_super_admin_profile
from saas.web.serializers import (
    CreateEnterprizeRequest,
    CreateEnterprizeResponse,
    RetrieveProfileResponse,
    UpdateProfileResponse,
    UpdateProfileRequest,
    UploadPhotoResponse,
    ListPostsResponse,
    RetrievePostResponse,
    Post,
    CreateQuestionRequest,
    CreateQuestionResponse,
    CreateAnswerRequest,
    CreateAnswerResponse,
    Question,
    Answer,
    ListQuestionsResponse,
    RetrieveQuestionResponse,
    EventSerializer,
    ListEventsResponse,
)
from saas.web.session import profile_database, post_database, event_database

users_router = APIRouter()


@users_router.post(
    path='/enterprizes',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateEnterprizeResponse,
    name='Create enterprize',
    tags=['enterprizes'],
)
def create_enterprize_controller(
    request: 'CreateEnterprizeRequest',
    profile: 'Profile' = Depends(get_super_admin_profile),
    repository: 'ProfileRepository' = Depends(profile_database),
):
    try:
        enterprize = create_enterprize(name=request.name, subdomain=request.subdomain, repository=repository)
    except EnterprizeExists as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)

    return CreateEnterprizeResponse(subdomain=enterprize.subdomain)


@users_router.get(
    path='/profile',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveProfileResponse,
    name='Retrieve user profile',
    tags=['profiles'],
)
def retrieve_profile_controller(profile: 'Profile' = Depends(get_profile)):
    return RetrieveProfileResponse(
        reference=profile.reference,
        first_name=profile.first_name,
        last_name=profile.last_name,
        email=profile.user.username,
        gender=profile.gender,
        birthdate=profile.birthdate,
        role=profile.user.type.name,
        activated=bool(profile.user.activated),
        invited=bool(profile.user.invited),
        street=profile.contact.address.street,
        town=profile.contact.address.town,
        zip_code=profile.contact.address.zip_code,
        country=profile.contact.address.country,
        phone_number=profile.contact.phone_number,
        position=profile.company_status.position,
        department=profile.company_status.department,
        photo_url=profile.photo_url,
        skills=profile.skills,
        availability=profile.availability,
        motivation=profile.motivation,
        descriptions=profile.descriptions,
    )


@users_router.put(
    path='/profile',
    status_code=status.HTTP_200_OK,
    response_model=UpdateProfileResponse,
    response_model_exclude_unset=True,
    name='Update user profile',
    tags=['profiles'],
)
def update_profile_controller(
    request: 'UpdateProfileRequest',
    profile: 'Profile' = Depends(get_profile),
    user_repo: 'ProfileRepository' = Depends(profile_database),
):
    cleaned_request = request.dict(exclude_unset=True)

    profile = update_profile(username=profile.user.username, repository=user_repo, **cleaned_request)

    return UpdateProfileResponse.from_orm(profile)


@users_router.post(
    path='/profile/photo',
    status_code=status.HTTP_201_CREATED,
    response_model=UploadPhotoResponse,
    name='Upload user photo',
    tags=['profiles'],
)
def upload_photo_controller(
    photo: UploadFile = File(...),
    authenticated_user: User = Depends(get_profile),
    user_repo: ProfileRepository = Depends(profile_database),
):
    try:
        Image.open(fp=photo.file)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='File probably not a valid image.',
        )
    finally:
        photo.file.seek(0)

    photo_url = upload_user_photo(username=authenticated_user.username, photo=photo, repository=user_repo)

    return UploadPhotoResponse(photo_url=photo_url)


@users_router.delete(
    path='/profile/photo', status_code=status.HTTP_204_NO_CONTENT, name='Delete user photo', tags=['profiles']
)
def delete_uploaded_photo_controller(
    authenticated_user: User = Depends(get_profile), user_repo: ProfileRepository = Depends(profile_database)
):
    delete_user_photo(username=authenticated_user.username, repository=user_repo)

    return Response()


@users_router.get(
    path='/posts',
    status_code=status.HTTP_200_OK,
    response_model=ListPostsResponse,
    name='List all news posts',
    tags=['newsfeed'],
)
def list_posts_controller(
    profile: 'Profile' = Depends(get_profile),
    post_repo: 'PostRepository' = Depends(post_database),
):
    posts = post_repo.list_for_enterprize(enterprize=profile.enterprize)

    posts_response = [
        Post(
            reference=post.reference,
            author=post.author.user.username,
            title=post.content.title,
            body=post.content.body,
            created=post.created,
        )
        for post in posts
        if post
    ]
    return ListPostsResponse(posts=posts_response)


@users_router.get(
    path='/post/{post_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrievePostResponse,
    name='Retrieve a news post',
    tags=['newsfeed'],
)
def retrieve_post_controller(
    post_id: str,
    profile: 'Profile' = Depends(get_profile),
    post_repo: 'PostRepository' = Depends(post_database),
):
    try:
        post = post_repo.retrieve_news_post(reference=post_id)
    except PostDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    return RetrievePostResponse(
        reference=post.reference,
        author=post.author.user.username,
        title=post.content.title,
        body=post.content.body,
        created=post.created,
    )


@users_router.post(
    path='/questions',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateQuestionResponse,
    name='Create Q&A question',
    tags=['Q&A'],
)
def create_question_controller(
    request: 'CreateQuestionRequest',
    profile: 'Profile' = Depends(get_profile),
    post_repo: 'PostRepository' = Depends(post_database),
):
    question_content = PostContent(title=request.title, body=request.body)
    question = post_question(author=profile, content=question_content, repository=post_repo, tags=request.tags)

    return CreateQuestionResponse(
        id=question.reference, author=question.author.user.username, tags=question.tags, created=question.created
    )


@users_router.post(
    path='/questions/{question_id}',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateAnswerResponse,
    name='Create Q&A answer',
    tags=['Q&A'],
)
def create_answer_controller(
    question_id: str,
    request: 'CreateAnswerRequest',
    profile: 'Profile' = Depends(get_profile),
    post_repo: 'PostRepository' = Depends(post_database),
):
    answer_content = PostContent(title=None, body=request.body)

    question = post_repo.retrieve_question(reference=question_id)
    answer = create_answer(author=profile, content=answer_content, question=question, repository=post_repo)

    return CreateAnswerResponse(
        id=answer.reference,
        question_id=answer.question.reference,
        author=answer.author.user.username,
        created=answer.created,
    )


@users_router.get(
    path='/questions',
    status_code=status.HTTP_200_OK,
    response_model=ListQuestionsResponse,
    name='List all Q&A questions',
    tags=['Q&A'],
)
def list_questions_controller(
    profile: 'Profile' = Depends(get_profile), post_repo: 'PostRepository' = Depends(post_database)
):
    questions = post_repo.list_questions_for_enterprize(enterprize=profile.enterprize)

    questions_response = [
        Question(
            id=question.reference,
            title=question.title,
            body=question.body,
            author=question.author.user.username,
            answers=[
                Answer(
                    id=answer.reference, body=answer.body, author=answer.author.user.username, created=answer.created
                )
                for answer in question.answers
            ],
            created=question.created,
        )
        for question in questions
    ]
    return ListQuestionsResponse(questions=questions_response)


@users_router.get(
    path='/questions/{question_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveQuestionResponse,
    name='Retrieve Q&A question',
    tags=['Q&A'],
)
def retrieve_question_controller(
    question_id: str, profile: 'Profile' = Depends(get_profile), post_repo: 'PostRepository' = Depends(post_database)
):
    question = post_repo.retrieve_question(reference=question_id)

    return RetrieveQuestionResponse(
        id=question.reference,
        title=question.title,
        body=question.body,
        author=question.author.user.username,
        answers=[
            Answer(id=answer.reference, body=answer.body, author=answer.author.user.username, created=answer.created)
            for answer in question.answers
        ],
        created=question.created,
    )


@users_router.get(
    path='/events',
    status_code=status.HTTP_200_OK,
    response_model=ListEventsResponse,
    name='List all events',
    tags=['events'],
)
def list_events_controller(
    profile: 'Profile' = Depends(get_profile),
    event_repo: 'EventRepository' = Depends(event_database),
):
    events = list_events_by_enterprize(enterprize=profile.enterprize, repository=event_repo)

    return ListEventsResponse(events=[EventSerializer.from_orm(event) for event in events])
