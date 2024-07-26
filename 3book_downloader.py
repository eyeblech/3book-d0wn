import requests
import os

def print_ascii_art():
    art = """
 ██▀    ██▄ ▄▀▄ ▄▀▄ █▄▀ ▄▀▀   █▀▄ ▄▀▄ █   █ █▄ █ █   ▄▀▄ ▄▀▄ █▀▄ ██▀ █▀▄
 █▄▄ ▀▀ █▄█ ▀▄▀ ▀▄▀ █ █ ▄██   █▄▀ ▀▄▀ ▀▄▀▄▀ █ ▀█ █▄▄ ▀▄▀ █▀█ █▄▀ █▄▄ █▀▄
                                               
    """
    print(art)


def search_books(query='', num_results=10):
    """
    Searches for books based on the query.
    """
    url = f'https://archive.org/advancedsearch.php?q={query}&fl[]=identifier,title,creator&sort[]=random&rows={num_results}&start=0&output=json'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data['response']['docs']
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON from response.")
            return []
    else:
        print(f"Request failed with status code {response.status_code}")
        return []

def get_download_links(identifier):
    """
    Retrieves download links for the specified book identifier.
    """
    url = f'https://archive.org/metadata/{identifier}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            files = data.get('files', [])
            download_links = [f"https://archive.org/download/{identifier}/{file['name']}"
                              for file in files if file['name'].endswith(('.txt', '.epub', '.pdf', '.mobi'))]
            return download_links
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON from response.")
            return []
    else:
        print(f"Request failed with status code {response.status_code}")
        return []

def download_file(file_url, save_path):
    """
    Downloads a file from the given URL and saves it to the specified path.
    """
    response = requests.get(file_url)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded and saved as '{save_path}'")

def format_creator(creator):
    """
    Formats the creator field to handle lists.
    """
    if isinstance(creator, list):
        return ', '.join(creator).replace('/', '_')
    return creator.replace('/', '_')

def main():
    print_ascii_art()
    search_query = input("Enter the Title or Subject to Search for Books: ").strip()
    if not search_query:
        print("No search query provided. Exiting.")
        return

    num_results = input("Enter the number of results you want (default 10): ").strip()
    if not num_results.isdigit():
        num_results = 10
    else:
        num_results = int(num_results)

    books = search_books(search_query, num_results)
    if not books:
        print("No books found for the given query.")
        return

    print("\nAvailable books:")
    for idx, book in enumerate(books):
        title = book.get('title', 'Unknown Title').replace('/', '_')
        creator = format_creator(book.get('creator', 'Unknown Creator'))
        print(f"[{idx}] {title} by {creator}")

    try:
        choice = int(input("Enter the Number of the Book you want to Download: ").strip())
        if 0 <= choice < len(books):
            selected_book = books[choice]
            identifier = selected_book['identifier']
            title = selected_book.get('title', 'Unknown Title').replace('/', '_')
            creator = format_creator(selected_book.get('creator', 'Unknown Creator'))
            print(f"\nSelected book: {title} by {creator}")

            download_links = get_download_links(identifier)
            if download_links:
                # Prefer .epub format if available
                download_link = next((link for link in download_links if '.epub' in link), download_links[0])
                extension = download_link.split('.')[-1]
                save_path = os.path.join(os.path.expanduser('~'), 'Downloads', f'{title}_{creator}.{extension}')
                print(f"Downloading from: {download_link}")
                download_file(download_link, save_path)
            else:
                print("No downloadable link found for the selected book.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
