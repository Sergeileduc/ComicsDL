from comicsdl.temp import get_last_week

DC_URL = "https://getcomics.info/tag/dc-week/"


def test_bizarre():
    """Test find_last_weekly."""
    time = get_last_week(DC_URL)
    print(time)
