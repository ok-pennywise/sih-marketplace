from ninja import Router

from users import schemas
from users.models import Address, User


router = Router()


@router.post("/create", response=schemas.UserOut)
def create_user(request, payload: schemas.UserIn):
    return User.objects.create(**payload.dict())


@router.get("/{id}", response={200: schemas.UserOut, 404: None})
def get_user(request, id: str):
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        return 404, None


@router.post("/address/add", response=schemas.AddressInOut)
def add_address(request, payload: schemas.AddressInOut):
    return Address(**payload.dict())


@router.delete("/address/delete/{id}", response={200: None, 404: None})
def delete_address(request, id: str):
    try:
        return Address.objects.get(id=id).delete()
    except Address.DoesNotExist:
        return 404, None


@router.patch("/change/{id}/{new_type}", response={400: str, 200: schemas.UserOut})
def change_user_type(request, id: str, new_type: str):
    if not any(new_type in row for row in User.USER_TYPE_CHOICES):
        return (
            400,
            f"Invalid user type. Choices are {' and '.join([i[0] for i in User.USER_TYPE_CHOICES])}",
        )
    try:
        user = User.objects.get(id=id)
        if user.user_type != new_type:
            user.user_type = new_type
            user.save()
        return user
    except User.DoesNotExist:
        return 404, None
