FROM python:3.12-slim
WORKDIR /workspace
COPY . .
RUN useradd --uid 10001 --create-home appuser && mkdir -p /workspace/runtime && chown -R appuser:appuser /workspace
USER appuser
ENV PYTHONDONTWRITEBYTECODE=1 APP_HOST=0.0.0.0
EXPOSE 8014
CMD ["python", "-B", "-m", "app"]
