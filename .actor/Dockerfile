FROM apify/actor-python:3.12
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Bake both Whisper models into the image so runs start fast and need no download.
RUN python -c "from faster_whisper import download_model; download_model('small', output_dir='/models/small'); download_model('base', output_dir='/models/base')"
COPY . ./
CMD ["python3", "-m", "src"]
