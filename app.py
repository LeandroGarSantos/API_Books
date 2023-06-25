from flask import Flask, jsonify, request
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging


app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Our list of books
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "1984", "author": "George Orwell"}
]

# Add 100 more books to the list
for i in range(3, 103):
    books.append({"id": i, "title": f"Book {i}", "author": f"Author {i}"})


def validate_book_data(data):
    if "title" not in data or "author" not in data:
        return False
    return True


@app.route('/api/books', methods=['GET', 'POST'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def handle_books():
    app.logger.info('GET request received for /api/books')  # Log a message

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        start_index = (page - 1) * limit
        end_index = start_index + limit

        paginated_books = books[start_index:end_index]

        return jsonify(paginated_books)
    elif request.method == 'POST':
        # Get the new book data from the client
        new_book = request.get_json()

        # Generate a new ID for the book
        new_id = max(book['id'] for book in books) + 1
        new_book['id'] = new_id

        # Add the new book to our list
        books.append(new_book)

        # Return the new book data to the client
        return jsonify(new_book), 201
    else:
        # Handle the GET request
        author = request.args.get('author')

        if author:
            filtered_books = [book for book in books if book.get('author') == author]
            return jsonify(filtered_books)
        else:
            return jsonify(books)


def find_book_by_id(book_id):
    """Find the book with the id `book_id`.
    If there is no book with this id, return None."""
    for book in books:
        if book['id'] == book_id:
            return book
    return None


@app.route('/api/books/<int:id>', methods=['PUT'])
def handle_book(id):
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        return '', 404

    # Update the book with the new data
    new_data = request.get_json()
    book.update(new_data)

    # Return the updated book
    return jsonify(book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        return '', 404

    # Remove the book from the list
    book.remove(book)

    # Return the deleted book
    return jsonify(book)


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


def read_books(endpoint):
    page = 1
    limit = 10

    while True:
        # Send GET request to the endpoint with pagination parameters
        response = requests.get(endpoint, params={'page': page, 'limit': limit})

        if response.status_code == 200:
            books = response.json()
            if len(books) > 0:
                # Process the books
                for book in books:
                    # Do something with each book
                    print(f"Reading book: {book['title']} by {book['author']}")
                page += 1
            else:
                # All books have been read
                break
        else:
            print(f"Error occurred: {response.status_code}")
            break


# Replace the endpoint URL with your Codio's Flask endpoint URL
endpoint_url = 'https://hamletpigment-litercola-5000.codio.io/api/books'


# Call the function to read the books
read_books(endpoint_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)