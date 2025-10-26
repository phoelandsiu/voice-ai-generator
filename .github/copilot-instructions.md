# AI Coding Assistant Instructions

This document provides essential context for AI coding assistants working in this audio project codebase.

## Project Overview

This is a Python-based audio processing project that interacts with external APIs. The project is currently in early development stages.

## Key Components

### Model Generation
- Located in `model_generation.py`
- Handles audio model generation using external API services
- Uses environment variables for API configuration

## Environment & Configuration

- API credentials are managed through environment variables in `.env`
- Key environment variables:
  - `API_KEY`: Required for external API authentication

## Development Workflow

### Setup
1. Ensure Python environment is properly configured
2. Set up required environment variables (see `.env.example` for template)
3. Install required dependencies (TODO: Add requirements.txt)

### Best Practices
1. Environment Variables:
   - Always use environment variables for sensitive data
   - Access environment variables using `os.getenv()`

## Areas for Development

Current focus areas that need attention:
1. Implementation of model generation functionality in `model_generation.py`
2. Setting up proper dependency management
3. Adding error handling for API interactions
4. Implementing logging system
5. Adding tests

## TODO
- [ ] Add requirements.txt for dependency management
- [ ] Complete model generation implementation
- [ ] Add proper error handling
- [ ] Set up testing framework
- [ ] Add logging system
- [ ] Create documentation for API usage

---
Note: This is an initial version of the instructions based on the current state of the project. As the project evolves, these instructions should be updated to reflect new patterns and conventions.