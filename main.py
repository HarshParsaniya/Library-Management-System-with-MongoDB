from pymongo import MongoClient

class Library:
    def __init__(self, library_name):
        self.library_name = library_name

        self.client = MongoClient("mongodb+srv://<username>:<password>@cluster0.gv4ocpr.mongodb.net/",tlsAllowInvalidCertificates = True)


        self.db = self.client["library_database2"]
        self.books_collection = self.db["books"]
        self.lend_collection = self.db["lend"]

    def display_book(self):
        print('Books available in the library:\n')
        for book in self.books_collection.find():
            print(f'{book["bookname"]} - {book["quantity"]}')
        print()

    def add_book(self, bookname, no_of_books):
        existing_book = self.books_collection.find_one({"bookname": bookname})
        if existing_book:
            # Book already exists, updating the quantity
            self.books_collection.update_one({"_id": existing_book["_id"]}, {"$inc": {"quantity": no_of_books}})
        else:
            # Book doesn't exist, adding a new entry
            self.books_collection.insert_one({"bookname": bookname, "quantity": no_of_books})

    def lend_book(self):
        person_name = input('What is your name: ')
        bookname = input('Which book do you want: ')

        book = self.books_collection.find_one({"bookname": bookname, "quantity": {"$gt": 0}})
        if book:
            self.books_collection.update_one({"_id": book["_id"]}, {"$inc": {"quantity": -1}})
            self.lend_collection.update_one(
                {"bookname": bookname},
                {"$push": {"borrowers": person_name}},
                upsert=True
            )
        else:
            print(f'{bookname} is not available in the {self.library_name} library')
            answer = input(f'Do you want to know who has {bookname} book (y/n): ')
            if answer.lower() == 'y':
                borrowed_info = self.lend_collection.find_one({"bookname": bookname})
                if borrowed_info and "borrowers" in borrowed_info:
                    print(f'{bookname} book with {", ".join(borrowed_info["borrowers"])}')

    def return_book(self):
        bookname = input('Which book do you want to return: ')
        person_name = input('What is your name: ')

        borrowed_info = self.lend_collection.find_one({"bookname": bookname, "borrowers": person_name})
        if borrowed_info:
            self.lend_collection.update_one(
                {"_id": borrowed_info["_id"]},
                {"$pull": {"borrowers": person_name}}
            )
            self.books_collection.update_one({"bookname": bookname}, {"$inc": {"quantity": 1}})
        else:
            print(f"You did not borrow {bookname} from {self.library_name}")

def main():
    library_name = input("Enter the library name: ")
    print(f'Library Name is: {library_name}')

    harsh_library = Library(library_name)

    while True:
        print('1. Display Books')
        print('2. Add Book')
        print('3. Lend Book')
        print('4. Return Book')
        print('5. Exit')

        answer = input('Enter the choice from the above list: ')

        match answer:
            case '1':
                harsh_library.display_book()
            case '2':
                bookname = input('Enter the book name: ')
                no_of_books = int(input('Enter the number of books you want to add: '))
                harsh_library.add_book(bookname, no_of_books)
            case '3':
                harsh_library.lend_book()
            case '4':
                harsh_library.return_book()
            case '5':
                harsh_library.client.close()  # Close the MongoDB connection
                exit()
            case _:
                print('Enter a valid number from the above list')


if __name__ == '__main__':
    main()