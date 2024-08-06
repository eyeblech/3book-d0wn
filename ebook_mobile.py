import requests
import os
from tqdm import tqdm
import platform

def print_ascii_art():
    art = """
 ██▀    ██▄ ▄▀▄ ▄▀▄ █▄▀ ▄▀▀   █▀▄ ▄▀▄ █   █ █▄ █ █   ▄▀▄ ▄▀▄ █▀▄ ██▀ █▀▄
 █▄▄ ▀▀ █▄█ ▀▄▀ ▀▄▀ █ █ ▄██   █▄▀ ▀▄▀ ▀▄▀▄▀ █ ▀█ █▄▄ ▀▄▀ █▀█ █▄▀ █▄▄ █▀▄
                                               
    """
    print(art)

def search_books(query='', num_results=10):
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
    response = requests.get(file_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb') as file, tqdm(
        total=total_size, unit='B', unit_scale=True, desc=save_path.split('/')[-1], initial=0, ascii=True
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            progress_bar.update(len(data))
            file.write(data)
    
    print(f"Downloaded and saved as '{save_path}'")

def format_creator(creator):
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
                download_link = next((link for link in download_links if '.epub' in link), download_links[0])
                extension = download_link.split('.')[-1]
                
                # Determine the correct download path for Android
                if platform.system() == 'Linux' and 'ANDROID_STORAGE' in os.environ:
                    download_dir = os.path.join(os.getenv('EXTERNAL_STORAGE', '/storage/emulated/0'), 'Download')
                else:
                    download_dir = os.path.expanduser('~/Downloads')

                save_path = os.path.join(download_dir, f'{title}_{creator}.{extension}')
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

