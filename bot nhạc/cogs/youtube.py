import googleapiclient.discovery
import os
import logging

# Lấy API Key từ biến môi trường
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Thiết lập logging
logging.basicConfig(level=logging.INFO)

# Kiểm tra API key trước khi khởi tạo dịch vụ YouTube
if not YOUTUBE_API_KEY:
    logging.error("API Key chưa được thiết lập. Vui lòng kiểm tra biến môi trường YOUTUBE_API_KEY.")
    raise ValueError("YOUTUBE_API_KEY không tồn tại!")

# Khởi tạo dịch vụ YouTube API
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def search_youtube(query):
    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=1
        )
        response = request.execute()

        # Kiểm tra nếu có kết quả tìm kiếm
        if 'items' in response and response['items']:
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            logging.info("Không tìm thấy video nào với từ khóa: %s", query)
            return None
    except googleapiclient.errors.HttpError as e:
        logging.error(f"Lỗi HTTP từ YouTube API: {e}")
        return None
    except Exception as e:
        logging.error(f"Lỗi khi tìm kiếm video trên YouTube: {e}")
        return None

# Ví dụ sử dụng hàm này
if __name__ == "__main__":
    query = "Minecraft gameplay"
    video_url = search_youtube(query)
    if video_url:
        print(f"Video found: {video_url}")
    else:
        print("No video found.")
