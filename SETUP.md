# SETUP.md

## Comprehensive Setup and Installation Guide

### System Requirements
- Python 3.x
- Virtualenv
- Flask
- Dependencies as listed in `requirements.txt`

### Python Virtual Environment Setup
1. Install Virtualenv if not already installed:
   ```bash
   pip install virtualenv
   ```
2. Create a virtual environment:
   ```bash
   virtualenv venv
   ```
3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

### Install Dependencies
Run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```

### OpenWeatherMap API Key Configuration
1. Sign up at [OpenWeatherMap](https://openweathermap.org/) to obtain your API key.
2. Add your API key to the environment variables.

### Environment Variables Setup (.env file)
Create a `.env` file in the root directory with the following content:
```
API_KEY=your_openweather_api_key
```

### Backend Flask Server Startup
To start the backend Flask server on port 5050:
```bash
flask run --host=0.0.0.0 --port=5050
```

### Frontend Static Server Launch
To launch the frontend static server on port 8000:
```bash
python -m http.server 8000
```

### Verification Steps
1. Open your web browser and navigate to `http://localhost:8000` to verify the frontend.
2. Check the backend by accessing `http://localhost:5050`.

### Troubleshooting Common Issues
- **Issue:** Flask server not starting.
  - **Solution:** Ensure your virtual environment is activated and all dependencies are installed.
- **Issue:** API key not working.
  - **Solution:** Check if the API key is correctly set in the `.env` file.

### Development Workflow
1. Create a branch for new features: `git checkout -b feature-branch`
2. Make your changes.
3. Commit your changes: `git commit -m "Description of changes"`
4. Push your changes: `git push origin feature-branch`
5. Create a pull request.

### Docker Setup Option
To set up the application using Docker:
1. Create a `Dockerfile` and a `docker-compose.yml`.
2. Build your Docker container:
   ```bash
   docker-compose up --build
   ```
3. Access the application through your browser at `http://localhost:8000`.  

---