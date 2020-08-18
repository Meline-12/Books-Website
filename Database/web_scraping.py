from mysql import SQLInsert, SQLCheck
from urllib.request import urlopen
from urllib import error
from bs4 import BeautifulSoup, NavigableString


def crawler(start: int, end: int):
    while start <= end:
        book = Book(start)
        book.run()
        start += 1


class Book:
    def __init__(self, number: int):
        self.number = number
        self.url = f'https://www.goodreads.com/book/show/{self.number}'
        self.info = {"title": None, "year": None, "isbn": None, "pages": None,
                     "average_rating": None, "rating_count": None, "publisher": None,
                     "language": None, "price": None,
                     "description": None, "img": None, "src_id": self.number}
        self.authors = []
        self.characters = []
        self.genres = []
        self.insert = SQLInsert()
        self.check = SQLCheck()

    def run(self):
        try:
            with urlopen(self.url) as res:
                html = res.read()
                self.scraper(html)
                self.insert_into_db()
        except (error.URLError, error.HTTPError, error.ContentTooShortError):
            pass

    def scraper(self, html):
        bs = BeautifulSoup(html, "html.parser")

        title = bs.find("h1", {"id": "bookTitle"}).get_text(strip=True)
        self.info["title"] = title

        pages_tag = bs.find("span", {"itemprop": "numberOfPages"})
        if pages_tag:
            pages = int(pages_tag.get_text().strip().split()[0])
            self.info["pages"] = pages

        average_rating = float(bs.find("span", {"itemprop": "ratingValue"}).get_text().strip())
        self.info["average_rating"] = average_rating

        rating_count = bs.find("meta", {"itemprop": "ratingCount"}).get("content")
        self.info["rating_count"] = rating_count

        prices_tag = bs.find_all("a", {'class', "buttonBar"})
        for i in prices_tag:
            if "Amazon" in i.get_text():
                price = "{}{}".format('https://www.goodreads.com', i['href'])
                self.info["price"] = price
                break

        img_tag = bs.find("img", {"id": "coverImage"})
        if img_tag:
            img = img_tag["src"]
        else:
            img = "https://s.gr-assets.com/assets/nophoto/book/blank-133x176-8b769f39ba6687a82d2eef30bdf46977.jpg"
        self.info["img"] = img

        description_tag = bs.find("div", {"id": "description"})
        if description_tag is None:
            description = None
        else:
            description_span = description_tag.find("span", {"style": "display:none"})
            if description_span:
                description = description_span.get_text().strip()
            else:
                description = description_tag.get_text().strip()
        self.info["description"] = description

        genres_list = []
        for genre in bs.find_all("a", {"class": "actionLinkLite bookPageGenreLink"}):
            genre_name = genre.get_text().strip()
            if genre_name not in genres_list:
                genres_list.append(genre_name)
                genre_link = f'https://www.goodreads.com{genre["href"]}'
                genre_dict = {"name": genre_name, "link": genre_link}
                self.genres.append(genre_dict)

        for tag in bs.find_all("div", {"id": "details"}):
            row_tag = tag.find_all("div", {"class": "row"})
            index = 0
            if len(row_tag) > 1:
                index = 1
            for div in tag.find_all("div", {"class": "row"})[index]:
                if isinstance(div, NavigableString):
                    for j in div.split():
                        if j.isdigit():
                            year = int(j)
                            self.info["year"] = year
                        if j == "by":
                            publisher = " ".join(div.split()[div.split().index(j) + 1:])
                            self.info["publisher"] = publisher

            for details in tag.find_all("div", {"class": "clearFloats"}):
                if details.find("div", {"class": "infoBoxRowTitle"}).get_text(strip=True) == "ISBN":
                    isbn = details.find("div", {"class": "infoBoxRowItem"}).get_text().strip().split()[0]
                    self.info["isbn"] = isbn
                if details.find("div", {"class": "infoBoxRowTitle"}).get_text(strip=True) == "Edition Language":
                    language = details.find("div", {"class": "infoBoxRowItem"}).get_text(strip=True)
                    self.info["language"] = language
                if details.find("div", {"class": "infoBoxRowTitle"}).get_text(strip=True) == "Characters":
                    characters = details.find("div", {"class": "infoBoxRowItem"}).find_all("a")
                    for character in characters:
                        if character["href"] != "#":
                            character_name = character.get_text().strip()
                            character_link = f'https://www.goodreads.com{character["href"]}'
                            character_dict = {"name": character_name, "link": character_link}
                            self.characters.append(character_dict)

        for div_tag in bs.find_all("div", {"class": "authorName__container"}):
            author_src_id = div_tag.a["href"].split("/")[-1].split(".")[0]
            author_type = div_tag.find("span", {"class": "authorName greyText smallText role"})
            if author_type is None:
                author_type = "Writer"
            else:
                author_type = author_type.text.strip()[1:-1]
            author_dict = {"src_id": author_src_id, "type": author_type}
            self.authors.append(author_dict)
            if self.check.author(author_src_id) is None:  # checking whether the author is already in the db
                author = Author(author_src_id)
                author.scraper()
                author.insert_into_db()

    def insert_into_db(self):
        if self.info["publisher"]:
            self.insert.publisher(self.info["publisher"])
        if self.info["language"]:
            self.insert.language(self.info["language"])

        self.insert.book(self.info)

        if len(self.characters) > 0:
            for item in self.characters:
                self.insert.character(item)
                self.insert.books_characters(self.number, item["link"])

        if len(self.genres) > 0:
            for item in self.genres:
                self.insert.genre(item)
                self.insert.books_genres(self.number, item["link"])

        for item in self.authors:
            self.insert.books_authors(self.number, item["src_id"], item["type"])

        self.insert.close()


class Author:
    def __init__(self, number: int):
        self.number = number
        self.url = f'https://www.goodreads.com/author/show/{self.number}'
        self.info = {"name": None, "books_count": None, "average_rating": None, "rating_count": None,
                     "description": None, "img": None, "src_id": self.number}
        self.insert = SQLInsert()

    def scraper(self):
        with urlopen(self.url) as res:
            html = res.read()

        bs = BeautifulSoup(html, "html.parser")

        name = bs.find("h1", {"class": "authorName"}).get_text().strip()
        self.info["name"] = name

        books_count = bs.find("div", {"class": "hreview-aggregate"}).a.get_text().split()[0].replace(",", "")
        self.info["books_count"] = books_count

        average_rating = float(bs.find("span", {"itemprop": "ratingValue"}).get_text().strip())
        self.info["average_rating"] = average_rating

        rating_count = bs.find("span", {"itemprop": "ratingCount"}).get("content")
        self.info["rating_count"] = rating_count

        author_info = bs.find("div", {"class": "aboutAuthorInfo"})
        if author_info is None:
            description = None
        else:
            description_span = author_info.find("span", {"style": "display:none"})
            if description_span:
                description = description_span.get_text().strip()
            else:
                description = author_info.get_text().strip()
                if description == "edit data":
                    description = None
                elif "edit data" in description:
                    description = description.split("edit data")[-1].strip()
        self.info["description"] = description

        img = bs.find("meta", {"itemprop": "image"}).get("content")
        self.info["img"] = img

    def insert_into_db(self):
        self.insert.author(self.info)
