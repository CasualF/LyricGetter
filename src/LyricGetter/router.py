from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from src.LyricGetter.schemas import SongBase, ArtistSchema, ArtistInDB
from fastapi.responses import FileResponse
from src.account.models import Account
from src.tasks.tasks import process_pic
from src.deps import get_current_user
from src.config import settings
from src import crud

import os
from random import randint
from pathlib import Path
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.wavpack import WavPack
from mutagen.oggvorbis import OggVorbis


router = APIRouter()


@router.post('/upload', response_model=SongBase)
async def upload_song(file: UploadFile, artist_id: int = None):
    allowed_extensions = (".mp3", ".ogg", ".wv", ".wav", ".m4a", "mp4")
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(detail="Invalid file format. Only .mp3, .ogg, .wv, and .wav are supported.",
                            status_code=status.HTTP_400_BAD_REQUEST)

    songs_path = os.path.join(settings.MEDIA_DIR, 'songs')
    file_path = os.path.join(songs_path, file.filename)

    if os.path.isfile(file_path):
        raise HTTPException(detail='File with this name already exists',
                            status_code=status.HTTP_409_CONFLICT)

    with open(file_path, "wb") as f:
        file_content = file.file.read()
        f.write(file_content)

    random_nums = [str(randint(0, 10)) for _ in range(6)]
    title = file.filename.replace(file_ext, '')
    img_title = title + '_' + ''.join(random_nums)

    duration = None
    audio = None
    image_path = None

    if file_ext == ".mp3":
        audio = MP3(file_path)
        duration = audio.info.length
    elif file_ext == ".m4a" or file_ext == ".mp4":
        audio = MP4(file_path)
        duration = audio.info.length
    elif file_ext == ".ogg":
        audio = OggVorbis(file_path)
        duration = audio.info.length
    elif file_ext == ".wv" or file_ext == '.wav':
        audio = WavPack(file_path)
        duration = audio.info.length
    tags = audio.tags
    if 'covr' in tags.keys():
        image_data = tags["covr"]
        process_pic.delay(image_data, img_title)

    media_dir = os.path.join(settings.MEDIA_DIR, 'images')
    image_path = media_dir + '/' + img_title + '.jpg'

    file_size = os.path.getsize(file_path)
    file_size_kb = file_size / 1024
    file_size_mb = file_size_kb / 1024

    song_info = {
        "file_link": file_path,
        "file_size": file_size_mb,
        "title": title,
        "duration": duration,
        "cover": image_path,
    }

    if artist_id:
        song_info.update({"artist_id": artist_id})

    song = await crud.song.create(song_info)

    return song


@router.get('', response_model=list[SongBase])
async def get_songs(search_param: str = None):
    if search_param:
        songs = await crud.song.search_song(param=search_param)
    else:
        songs = await crud.song.get_list()
    return songs


@router.post('/become_artist', response_model=ArtistInDB)
async def become_artist(artist_data: ArtistSchema, current_user: Account = Depends(get_current_user)):
    artist_data = artist_data.model_dump()
    artist_data['user_id'] = current_user.id
    artist = await crud.song.create_artist(artist_data)
    return artist
