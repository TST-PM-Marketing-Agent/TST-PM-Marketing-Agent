# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system packages and Python dependencies
# Using --no-cache-dir to keep the image lightweight
RUN pip install --no-cache-dir \
    "fastapi>=0.115" \
    "uvicorn>=0.30" \
    "pymongo>=4.5" \
    "requests>=2.32" \
    "eval_type_backport>=0.2.0" \
    "pydantic>=2.0"

# Copy all multi-agent system directories into the container
COPY ui-team /app/ui-team
COPY ceo-agent /app/ceo-agent
COPY pm-marketing-agent /app/pm-marketing-agent
COPY engineering-agent /app/engineering-agent

# Set up environment variables
# PYTHONPATH ensures Python can resolve the enterprise_router module from ui-team
ENV PYTHONPATH=/app/ui-team
ENV ROUTER_API_PORT=8765
ENV ROUTER_API_HOST=0.0.0.0

# Expose the API and Dashboard port
EXPOSE 8765

# Start the unified enterprise router API and simulation server
CMD ["python3", "-m", "enterprise_router.api"]
