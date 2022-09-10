import os
import aiofiles
from fastapi import APIRouter, Response, HTTPException, UploadFile
from beanie import WriteRules, DeleteRules, PydanticObjectId
from pathlib import Path
from .models import *

router = APIRouter(prefix='/submitData', tags=['MountainPass'])

upload_dir = Path(os.environ.get('FSTR_UPLOAD_DIR'))


@router.post('/')
async def submit_data(data: MountainPass, photo_files: list[UploadFile] | None = None) -> dict:

    person_db = await Person.get_by_email(data.person.email)
    if person_db:
        data.person = person_db

    if data.status and data.status != Status.NEW:
        return {'state': 0,
                'message': 'Status not New'}

    if len(data.photos) != len(photo_files):
        return {'state': 0,
                'message': 'Photo count mismatch'}


    for photo in zip(photo_files, data.photos):
        try:
            photo_id: UUID = photo[1].id
            suffix = Path(photo[0].filename).suffix
            uploaded_file: Path = upload_dir / Path(photo_id.hex).with_suffix(suffix)
            async with aiofiles.open(uploaded_file, 'wb') as f:
                while chunk := await photo[0].read(2**20):
                    await f.write(chunk)
        except Exception as e:
            return {'state': 0,
                    'message': f'Photo saving error: {e}'}
        finally:
            await photo[0].close()

    await data.save(link_rule=WriteRules.WRITE)
    return {'state': 1,
            'message': 'OK',
            '_id': data.id}


@router.get('/{_id}', response_model=MountainPassOut)
async def get_data_by_id(_id: PydanticObjectId) -> MountainPass | dict:
    """Return MountainPass data with given id or 404"""
    data = await MountainPass.get(_id, fetch_links=True)
    if not data:
        return {'state': 0,
                'message': 'Data not found'}
    return data


@router.get('/', response_model=List[MountainPassOut])
async def get_data_by_email(user__email: str) -> List[MountainPass] | dict:
    """Return List of MountainPass data for Person with given user__email or empty List"""

    data = await MountainPass.find(MountainPass.person.email == user__email, fetch_links=True).to_list()
    if not data:
        return {'state': 0,
                'message': 'Data not found'}
    return data


@router.patch('/{_id}')
async def edit_data_by_id(_id: PydanticObjectId,
                          req: MountainPass,
                          photo_files: list[UploadFile] | None = None) -> dict:

    data = await MountainPass.get(_id, fetch_links=True)
    if not data:
        return {'state': 0,
                'message': 'Data not found'}

    if data.status != Status.NEW:
        return {'state': 0,
                'message': 'Status not New'}

    req.person = data.person

    if len(req.photos) != len(photo_files):
        return {'state': 0,
                'message': 'Invalid photo count'}

    for photo in zip(photo_files, req.photos):
        try:
            photo_id: UUID = photo[1].id
            suffix = Path(photo[0].filename).suffix
            uploaded_file: Path = upload_dir / Path(photo_id.hex).with_suffix(suffix)
            # TODO: check if file already exists
            # TODO: delete unreferenced files
            async with aiofiles.open(uploaded_file, 'wb') as f:
                while chunk := await photo[0].read(2**20):
                    await f.write(chunk)
        except Exception as e:
            return {'state': 0,
                    'message': f'Photo saving error: {e}'}
        finally:
            await photo[0].close()

    await data.delete(link_rule=DeleteRules.DELETE_LINKS)
    await req.save(link_rule=WriteRules.WRITE)

    return {'state': 1,
            'message': 'OK',
            '_id': req.id}
