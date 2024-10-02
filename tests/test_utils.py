import pytest
from contextlib import nullcontext

from vlrscraper.utils import get_url_segment, epoch_from_timestamp


@pytest.mark.parametrize(
    "url,index,rtype,result,err",
    [
        ("/", 0, str, "", None),
        ("/", 1, str, "", None),
        ("/api/", 2, str, "", None),
        ("/api/", 1, str, "api", None),  # Basic success cases
        ("", 1, str, "", IndexError),
        ("/api/", 10, str, "", IndexError),  # Index out of bounds cases
        ("/id/1234", 2, int, 1234, None),  # Type casting cases
        ("/id/test", 2, int, "", ValueError),  # Invalid casting case
    ],
)
def test_get_url_segment(url, index, rtype, result, err):
    with pytest.raises(err) if err else nullcontext():
        assert get_url_segment(url, index, rtype=rtype) == result


@pytest.mark.parametrize(
    "ts, fmt, epoch, err",
    [
        (
            "01:01:1970 00:00:00 -0000",
            "%d:%m:%Y %H:%M:%S %z",
            0,
            None,
        ),  # The epoch case
        (
            "01:01:1970 00:00:00 -0100",
            "%d:%m:%Y %H:%M:%S %z",
            3600,
            None,
        ),  # UTC offsets
        ("01:01:1970 00:00:00 +0100", "%d:%m:%Y %H:%M:%S %z", -3600, None),
        ("", "%J", 0, ValueError),
        ("", "asjflas", 0, ValueError),  # Invalid formats
        (
            "50:01:1970 00:00:00 +0100",
            "%d:%m:%Y %H:%M:%S %z",
            -3600,
            ValueError,
        ),  # Valid format, invalid date
    ],
)
def test_epoch_from_timestamp(ts, fmt, epoch, err):
    with pytest.raises(err) if err else nullcontext():
        assert epoch_from_timestamp(ts, fmt) == epoch
