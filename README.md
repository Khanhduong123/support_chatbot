# Support Chatbot

Dự án **support_chatbot** là một ứng dụng chatbot hỗ trợ khách hàng, được xây dựng với Python sử dụng FastAPI. Ứng dụng giúp tự động hóa việc trả lời các câu hỏi thường gặp và hỗ trợ người dùng hiệu quả.

## Tính năng

- Trả lời tự động các câu hỏi thường gặp.
- Giao diện API RESTful thân thiện với lập trình viên.
- Có thể mở rộng và tùy chỉnh dễ dàng.

## Yêu cầu

- Python 3.10+
- FastAPI
- Uvicorn

## Cài đặt

1. Clone repository:
   ```bash
   git clone https://github.com/your-username/support_chatbot.git
   cd support_chatbot
   ```

2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy dự án

Khởi động ứng dụng bằng lệnh dưới đây:

```bash
uvicorn main:app --reload
```

- Tham số `--reload` giúp server tự động khởi động lại khi có thay đổi code.
- Mặc định ứng dụng chạy tại [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Docs

Sau khi khởi động, bạn có thể truy cập tài liệu tự động tại:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo Pull Request hoặc Issue để trao đổi thêm.

---

**Chúc bạn sử dụng hiệu quả!**
