# 1. Download a ready-made Linux environment with Playwright & Python installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# 2. Create and go into a folder named /app inside the container
WORKDIR /app

# 3. Copy your requirements.txt from your computer into the container
COPY requirements.txt .

# 4. Install all your Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Install the Chromium browser
RUN playwright install chromium

# 6. Copy the rest of your project files into /app
COPY . .

# 7. Start your FastAPI server on port 10000 (Render's default port)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]