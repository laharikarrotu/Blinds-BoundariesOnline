# Elite Architecture Documentation

## System Design Overview

This application uses a **layered architecture** with **design patterns** and **optimized algorithms** for elite-level performance.

## Architecture Layers

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← FastAPI endpoints
├─────────────────────────────────────┤
│        Service Layer                │  ← Business logic
├─────────────────────────────────────┤
│      Repository Layer               │  ← Data access
├─────────────────────────────────────┤
│         Models Layer                │  ← Data structures
├─────────────────────────────────────┤
│    Algorithms & Cache Layer         │  ← Optimizations
└─────────────────────────────────────┘
```

## Key Components

### 1. Core Module (`app/core/`)
- **config.py**: Centralized configuration with caching
- **logger.py**: Structured logging
- **exceptions.py**: Custom exception hierarchy

### 2. Models (`app/models/`)
- **blind.py**: Immutable blind data structures with validation
- **image.py**: Image and mask data models

### 3. Repositories (`app/repositories/`)
- **image_repository.py**: Image storage operations
- **mask_repository.py**: Mask storage operations
- **Pattern**: Repository pattern for data access abstraction

### 4. Services (`app/services/`)
- **window_detection_service.py**: Window detection with caching
- **blind_overlay_service.py**: Optimized blind overlay
- **blind_factory.py**: Factory pattern for blind generators

### 5. Algorithms (`app/algorithms/`)
- **image_optimizer.py**: Optimized image processing algorithms
  - Vectorized operations (O(n) complexity)
  - Efficient resizing
  - Memory-optimized blending

### 6. Cache (`app/cache/`)
- **lru_cache.py**: Thread-safe LRU cache with TTL
  - O(1) get/set operations
  - Automatic eviction
  - Expiration handling

### 7. API (`app/api/`)
- **routes.py**: RESTful API endpoints
- **main.py**: FastAPI application setup

## Design Patterns Implemented

### 1. Repository Pattern
- Abstracts data access
- Easy to swap storage backends
- Clean separation of concerns

### 2. Factory Pattern
- `BlindGeneratorFactory` creates appropriate generators
- Strategy pattern for different blind types

### 3. Singleton Pattern
- Configuration (cached)
- Logger (single instance)
- Cache (global instance)

### 4. Strategy Pattern
- Different detection strategies (Azure, Gemini, OpenCV)
- Different blind generation strategies

## Data Structures & Algorithms

### LRU Cache
- **Time Complexity**: O(1) for get/set
- **Space Complexity**: O(n)
- **Features**: TTL, thread-safe, automatic eviction

### Image Processing
- **Vectorized Operations**: NumPy for O(n) complexity
- **Efficient Resizing**: LANCZOS interpolation
- **Memory Optimized**: Minimal copies

### Mask Matching
- **Dimension Verification**: Automatic resizing
- **Efficient Blending**: Vectorized alpha blending

## Performance Optimizations

1. **Caching**: LRU cache for masks and results
2. **Async/Await**: Non-blocking I/O operations
3. **Vectorization**: NumPy operations instead of loops
4. **Lazy Loading**: Import only when needed
5. **Connection Pooling**: Efficient resource usage

## Code Quality Features

- **Type Hints**: Full type annotations
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Custom exception hierarchy
- **Logging**: Structured logging throughout
- **Validation**: Data validation at model level
- **Immutability**: Frozen dataclasses where appropriate

## Usage

### Start the Elite Architecture Server

```bash
python3 -m app.main
# OR
python3 main.py  # Falls back to elite architecture
```

### API Endpoints

All endpoints are now in `app/api/routes.py`:
- `POST /upload-image` - Upload with validation
- `POST /detect-window` - Optimized detection with caching
- `POST /try-on` - Fast overlay with caching
- `GET /blinds-list` - List available blinds
- `GET /health` - Health check with component status

## Benefits

1. **Maintainability**: Clear separation of concerns
2. **Testability**: Easy to mock and test
3. **Scalability**: Can add new features easily
4. **Performance**: Optimized algorithms and caching
5. **Reliability**: Proper error handling and logging

## Next Steps

- Add unit tests for each layer
- Implement Redis for distributed caching
- Add database layer for persistence
- Implement rate limiting
- Add monitoring and metrics

