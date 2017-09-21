set(PYTHON_SOURCES
    __init__.py
    deck.py
    parser.py)

add_python_package(deck sunbeam/deck "${PYTHON_SOURCES}")
