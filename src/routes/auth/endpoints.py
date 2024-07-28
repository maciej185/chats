"""Endpoints for the auth package."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, HTTPException, Path, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import FilePath
from sqlalchemy.orm import Session

from src.db.models import DB_Profile, DB_User
from src.dependencies import RoleChecker, get_current_user, get_db
from src.roles import Roles
from src.tags import Tags
from src.utils import FileStorageManager

from .crud import (
    create_user,
    get_profile_from_db,
    get_user_from_db,
    update_profile_in_db,
    update_users_profile_pic_path,
)
from .models import Profile, ProfileAdd, ProfileUpdate, Token, UserAdd, UserInResponse
from .utils import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=[Tags.auth])


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Return access token if the user is authenticated.

    ### Args
    - **form_data**: An instance of the OAuth2PasswordRequestForm, containing the
            username and password (among other things) that are sent with
            the content type of 'form-data'.
    - **db**: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.

    ### Returns
    - Instance of the Token pydantic model with the token type
        and the authentication token itself.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserInResponse,
    dependencies=[Depends(RoleChecker(allowed_roles=[Roles.USER.value, Roles.ADMIN.value]))],
)
async def read_users_me(
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> DB_User:
    """Get the currently logged in User.

    ### Args
    - current_user: An instance of the DB_User model,
            representing the currently logged in (authenticated)
            user. The user is returned from the annotated dependency
            function.

    ### Returns
    - An instance of the DB_User model with the info about
        the currently logged in (authenticated) user.
    """
    return current_user


@router.get("/me/profile_picture", response_class=FileResponse)
def get_current_users_profile_pic(
    current_user: Annotated[DB_User, Depends(get_current_user)]
) -> FilePath:
    """Return profile picture of the currently logged in user.

    ### Args
    - current_user: An instance of the DB_User model,
            representing the currently logged in (authenticated)
            user. The user is returned from the annotated dependency
            function.

    ### Returns
    - A path to the profile picture of the currently logged in
        (authenticated) user.s
    """
    return current_user.profile.profile_pic_path


@router.post("/register", response_model=UserInResponse, status_code=201)
def register(
    user_data: Annotated[UserAdd, Body()],
    profile_data: Annotated[ProfileAdd, Body()],
    db: Annotated[Session, Depends(get_db)],
) -> DB_User:
    """Register the given User.

    ### Args
    - user_data: An instance of the UserAdd model with info
                    about the newly created User.
    - db: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.

    ### Returns
    - Instance of the DB_User model representing the newly
        created user.
    """
    return create_user(db=db, user_data=user_data, profile_data=profile_data)


@router.put(
    "/register/profile_picture/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(allowed_roles=[Roles.USER.value, Roles.ADMIN.value]))],
)
async def upload_picture(
    user_id: Annotated[int, Path()],
    profile_pic_file: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Upload a profile picture for a given profile.

    ### Args
    - user_id: ID of the user whose profile picture is mean to be
                    updated.
    - profile_pic_file: An instance of the UploadFile class, representing
                        file sent in an HTTP request with 'multipart/form-data'
                        content type.
    - db: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.
    """
    saved_profile_pic_path = FileStorageManager.save_profile_picture(
        user_id=user_id, profile_pic_file=profile_pic_file
    )
    update_users_profile_pic_path(db=db, user_id=user_id, profile_pic_path=saved_profile_pic_path)


@router.put("/update", response_model=Profile)
def update_profile(
    profile_data: Annotated[ProfileUpdate, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> DB_Profile:
    """Update given User's with the provided information.

    ### Args
    - profile_data: An instance of the UpdateProfile model with
                        the new profile information.
    - db: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.
    - current_user: An instance of the DB_User model,
            representing the currently logged in (authenticated)
            user. The user is returned from the annotated dependency
            function.

    ### Raises
        HTTPException: Raised when no valid info was provided.
    """
    updated_profile = update_profile_in_db(db, current_user.user_id, profile_data)
    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No valid profile information, profile not updated.",
        )
    return updated_profile


@router.get("/profile_picture/{user_id}", response_class=FileResponse)
def get_given_users_profile_pic(
    user_id: Annotated[int, Path()], db: Annotated[Session, Depends(get_db)]
) -> FilePath:
    """Return profile picture of the user with the given ID.

    ### Args
    - user_id: ID of the user whose profile pic is mean to be returned.


    ### Returns
    - A path to the profile picture of the given user.
    """
    user = get_user_from_db(db=db, user_id=user_id)
    return user.profile.profile_pic_path


@router.get("/profile/{profile_id}", response_model=Profile)
def get_given_users_profile(
    profile_id: Annotated[int, Path()], db: Annotated[Session, Depends(get_db)]
) -> DB_Profile:
    """Get profile with the given ID.

    ### Args:
    - profile_id: ID of the profile that is meant to be returned.
    - db: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.

    ### Returns
    - An instance of the DB_Profile model representing the profile
    with the given ID.
    """
    return get_profile_from_db(db=db, profile_id=profile_id)
