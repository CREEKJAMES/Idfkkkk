
git remote add origin https://github.com/CREEKJAMES/Idfkkkk.git
git branch -M main
git push -u origin main


import pandas as pd
import os
import aiohttp
import asyncio
from IPython.display import display, HTML

async def download_video(session, url, save_path):
    """
    Downloads a video from the given URL to the specified save path using aiohttp.
    
    Args:
        session (aiohttp.ClientSession): The aiohttp session for making requests.
        url (str): The URL of the video to download.
        save_path (str): The local path to save the downloaded video.
        
    Returns:
        None
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    file.write(chunk)
        print(f"Downloaded: {save_path}")
    except aiohttp.ClientError as e:
        print(f"Failed to download {url}: {e}")

async def download_videos(video_urls, download_folder):
    """
    Downloads multiple videos concurrently.
    
    Args:
        video_urls (list of str): List of video URLs to download.
        download_folder (str): The folder to save the downloaded videos.
        
    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in video_urls:
            video_name = os.path.basename(url)
            save_path = os.path.join(download_folder, video_name)
            tasks.append(download_video(session, url, save_path))
        await asyncio.gather(*tasks)

def generate_html_viewer(video_paths, output_file='video_viewer.html'):
    """
    Generates an HTML file to view videos.
    
    Args:
        video_paths (list of str): List of paths to the video files.
        output_file (str): The output HTML file name.
        
    Returns:
        None
    """
    html_content = '<html><body>'
    for video_path in video_paths:
        html_content += f'<video width="320" height="240" controls><source src="{video_path}" type="video/mp4">Your browser does not support the video tag.</video><br>'
    html_content += '</body></html>'

    with open(output_file, 'w') as file:
        file.write(html_content)
    
    # Display the HTML file in Jupyter Notebook
    display(HTML(html_content))

def process_large_csv(file_path, download_folder, chunk_size=100000, search_keywords=None):
    """
    Processes a large CSV file in chunks, sorts by duration, 
    downloads video files, generates a video viewer, and displays CSV data.
    
    Args:
        file_path (str): The path to the CSV file.
        download_folder (str): The folder to save the downloaded video files.
        chunk_size (int): Number of rows per chunk. Default is 100,000.
        search_keywords (list of str): List of keywords to search for and group together.
        
    Returns:
        None
    """
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    video_urls = []
    video_paths = []
    
    try:
        # Read the CSV file with a proper delimiter and error handling
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, error_bad_lines=False):
            # Check if the necessary columns exist
            required_columns = ['duration', 'url', 'embedded_url', 'tags']
            if not all(col in chunk.columns for col in required_columns):
                print("Missing one or more required columns in the CSV file.")
                return
            
            # Display the CSV chunk
            display(chunk.head())
            
            # Filter rows by search keywords if provided
            if search_keywords:
                chunk = chunk[chunk.apply(lambda row: any(keyword in str(row['tags']) for keyword in search_keywords), axis=1)]
            
            # Sort the chunk by duration
            chunk_sorted = chunk.sort_values(by='duration')
            
            # Display the first few rows of the sorted chunk
            display(chunk_sorted.head())
            
            # Process each entry
            for idx, row in chunk_sorted.iterrows():
                print(f"Duration: {row['duration']}")
                print(f"URL: {row['url']}")
                print(f"Embedded URL: {row['embedded_url']}")
                print(f"Tags: {row['tags']}")
                print("----------")
                
                # Extract the file name from the URL
                video_url = row['url']
                if video_url.endswith(('.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv')):
                    video_urls.append(video_url)
                    video_name = os.path.basename(video_url)
                    save_path = os.path.join(download_folder, video_name)
                    video_paths.append(save_path)
            
            # Uncomment the next line to process only the first chunk for testing
            # break

    except pd.errors.EmptyDataError:
        print("No data found in the CSV file.")
    except FileNotFoundError:
        print(f"The file at path {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Download videos asynchronously
    asyncio.run(download_videos(video_urls, download_folder))
    
    # Generate HTML viewer for the downloaded videos
    generate_html_viewer(video_paths)

# Path to the large CSV file
file_path = '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Videos.csv'

# Folder to save the downloaded video files
download_folder = '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/DownloadedVideos'

# List of search keywords to filter videos
search_keywords = ['keyword1', 'keyword2']  # Replace with actual keywords

# Call the function to process the CSV file and download videos
process_large_csv(file_path, download_folder, search_keywords=search_keywords)    

