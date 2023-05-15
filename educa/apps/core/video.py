from django.core.exceptions import ValidationError
from pytube import YouTube
from pytube.exceptions import RegexMatchError


def get_video_length(video_url):
    try:
        video = YouTube(video_url)
        return video.length
    except (TypeError, RegexMatchError):
        raise ValidationError('invalid youtube video')
