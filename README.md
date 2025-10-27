# Spark Website - Docker Setup

This is the original Spark website served via Docker using nginx.

## Run the Website

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Using Docker directly
```bash
docker build -t spark-website .
docker run -d -p 8080:80 --name spark-website spark-website
```

## Access the Website

Open your browser and navigate to:
```
http://localhost:8080
```

## Stop the Website

```bash
docker-compose down
```

Or if using Docker directly:
```bash
docker stop spark-website
docker rm spark-website
```

## Website Structure

The website files are located in `old/www.spark.org.il/` and include:
- index.html (homepage)
- Multiple blog post HTML files
- Static assets and resources
