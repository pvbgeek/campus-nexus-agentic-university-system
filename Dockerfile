FROM python:3.12-slim
WORKDIR /srv/app
COPY requirements-agents.lock.txt .
RUN python -m pip install --no-cache-dir -r requirements-agents.lock.txt \
    && useradd --create-home --uid 10001 campus \
    && install -d -o campus -g campus /srv/data /srv/app/.cache
COPY app ./app
COPY scripts/build_policy_index.py scripts/publish_policy.py scripts/init_local.py ./scripts/
COPY docs/policies/current-policy.md ./docs/policies/current-policy.md
ENV CAMPUS_NEXUS_DATA=/srv/data PYTHONDONTWRITEBYTECODE=1
USER campus
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
