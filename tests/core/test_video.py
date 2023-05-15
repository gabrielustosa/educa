import pytest
from django.core.exceptions import ValidationError

from educa.apps.core.video import get_video_length


@pytest.mark.parametrize(
    'video_url, seconds',
    [
        ('https://www.youtube.com/watch?v=OZgQnRcGZXs', 212),
        ('https://www.youtube.com/watch?v=kCLyivl080g', 217),
        ('https://www.youtube.com/watch?v=m226f2reF28', 264),
    ],
)
def test_video_length(video_url, seconds):
    video_length = get_video_length(video_url)

    assert video_length == seconds


def test_video_length_with_invalid_url():
    with pytest.raises(ValidationError):
        get_video_length('https://www.youtube.com/watch?v=zz00z0z0z0z0')
