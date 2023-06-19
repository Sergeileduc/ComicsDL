from .utils import htmlsoup


def get_last_week(url: str):
    """Get time since last weekly pack.

    Args:
        url (str): getcomics tag url (/tag/*-week)
        editor (str): _description_
    """
    soup = htmlsoup.url2soup(url)
    last_post = soup.find_all('article', class_='type-post')[0]
    title = last_post.h1.a.text
    time = last_post.find('time')
    return f'{title} :\t{time.text}'
