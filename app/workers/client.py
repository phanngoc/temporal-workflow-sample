import asyncio
from temporalio.client import Client
import os
from dotenv import load_dotenv

# Đảm bảo .env được load
load_dotenv()

# Biến cục bộ lưu trữ client
_client = None

async def get_client() -> Client:
    """
    Trả về một temporal client. Tạo mới nếu chưa tồn tại.
    """
    global _client
    if _client is None:
        # Lấy URL từ biến môi trường hoặc sử dụng giá trị mặc định
        temporal_server_url = os.getenv("TEMPORAL_SERVER_URL", "localhost:7233")
        _client = await Client.connect(temporal_server_url)
    
    return _client 