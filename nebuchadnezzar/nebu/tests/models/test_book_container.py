import os

from nebu.models.book_container import (
    book_container_factory,
    parse_book_vars,
    parse_books,
)
from nebu.xml_utils import etree_from_str


BookContainer = book_container_factory(
    "/collections",
    "/modules",
    "/media",
    "/private",
    "/interactives",
)


def test_default_container_values():
    container = BookContainer(".", [])
    assert container.books_root.endswith("/collections")
    assert os.path.isabs(container.books_root)
    assert container.pages_root.endswith("/modules")
    assert os.path.isabs(container.pages_root)
    assert container.media_root.endswith("/media")
    assert os.path.isabs(container.media_root)
    assert container.private_root.endswith("/private")
    assert os.path.isabs(container.private_root)
    assert container.public_root.endswith("/interactives")
    assert os.path.isabs(container.public_root)


def test_parse_book_vars():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <var name="BOOKS_ROOT" value="/books" />
</container>
"""
    etree = etree_from_str(books_xml)
    book_vars = parse_book_vars(etree)
    assert book_vars["books_root"] == "/books"


def test_parse_books():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <book slug="slug_name" style="dummy" href="href_path" />
</container>
"""
    etree = etree_from_str(books_xml)
    books = parse_books(etree)
    book = books[0]
    assert book.slug == "slug_name"
    assert book.style == "dummy"
    assert book.href == "href_path"
    assert book.collection_id is None


def test_parse_books_collection_id():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <book slug="slug_name" style="dummy" collection-id="col12345" href="href_path" />
</container>
"""
    etree = etree_from_str(books_xml)
    books = parse_books(etree)
    book = books[0]
    assert book.slug == "slug_name"
    assert book.style == "dummy"
    assert book.href == "href_path"
    assert book.collection_id == "col12345"


def test_parse_books_missing_required():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <book slug="slug_name" href="href_path" />
</container>
"""
    etree = etree_from_str(books_xml)
    exc = ""
    try:
        _ = parse_books(etree)
    except Exception as e:
        exc = str(e)
    assert "missing 1 required positional argument" in exc and "style" in exc


def test_partial_container():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <var name="BOOKS_ROOT" value="/books" />
    <book slug="slug_name" href="href_path" style="dummy" />
</container>
"""
    container = BookContainer.from_str(books_xml, ".")
    # Updated
    assert container.books_root.endswith("/books")
    assert os.path.isabs(container.books_root)
    # Stay the same
    assert container.pages_root.endswith("/modules")
    assert os.path.isabs(container.pages_root)
    assert container.media_root.endswith("/media")
    assert os.path.isabs(container.media_root)
    assert container.private_root.endswith("/private")
    assert os.path.isabs(container.private_root)
    assert container.public_root.endswith("/interactives")
    assert os.path.isabs(container.public_root)


def test_invalid_var_name():
    books_xml = """\
<container xmlns="https://openstax.org/namespaces/book-container" version="1">
    <var name="TEST_INVALID_NAME" value="..." />
</container>
"""
    exc = ""
    try:
        _ = BookContainer.from_str(books_xml, ".")
    except Exception as e:
        exc = str(e)
    assert "unexpected keyword argument" in exc
    assert "test_invalid_name" in exc