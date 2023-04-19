import pytest

from utils.tools import remove_tag


@pytest.mark.parametrize("old_name, new_name",
                         [("Doomsday Clock 09 (of 12) (2019) (Webrip) (The Last Kryptonian-DCP).cbr",  # noqa: E501
                           "Doomsday Clock 09 (of 12) (2019).cbr"),
                          ("X-Force 038 (2023) (Digital) (Zone-Empire).cbr",
                           "X-Force 038 (2023).cbr"),
                          ("Sonic The Hedgehog 058 (2023) (Digital) (AnHeroGold-Empire).cbz",
                           "Sonic The Hedgehog 058 (2023).cbz")])
def test_remove_tag(old_name: str, new_name: str):
    """Test remove tag."""
    remove_tag_name = remove_tag(old_name)
    assert remove_tag_name == new_name
