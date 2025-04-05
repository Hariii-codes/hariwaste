# WasteWorks

A comprehensive waste management platform that leverages image recognition technology to help users identify and properly recycle materials while promoting environmental awareness.

## Features

- **AI-powered Material Identification**: Upload images of waste items to receive analysis on recyclability, material composition, and proper disposal methods.
- **Blockchain-enabled Waste Tracking**: Monitor waste items from drop-off to recycling facility with a secure, transparent tracking system.
- **Interactive Recycling Guidance**: Get detailed instructions on how to prepare and recycle different types of materials.
- **Infrastructure Reporting**: Report damaged waste management infrastructure through webcam photos.
- **Rewards System**: Earn eco-points and achievements for responsible waste management.

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **AI/ML**: Google Gemini API, OpenCV, scikit-learn
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF, WTForms

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/wasteworks.git
   cd wasteworks
   ```

2. Install dependencies:
   ```
   pip install -r dependencies.txt
   ```

3. Configure environment variables:
   Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/wasteworks
   SESSION_SECRET=your_secret_key
   ```

4. Initialize the database:
   ```
   python recreate_db.py
   ```

5. Run the application:
   ```
   python main.py
   ```

## Database Schema

The application uses several related models:
- User (authentication, points, achievements)
- WasteItem (uploaded waste items with analysis)
- DropLocation (recycling centers)
- WasteJourneyBlock (blockchain-like tracking)
- InfrastructureReport (citizen reports of damaged infrastructure)

## Deployment

### Deploy to Render.com

This application is configured for easy deployment on Render.com:

1. Fork or clone this repository to your GitHub account
2. Sign up for Render.com and connect your GitHub account
3. Create a new Web Service and select your repository
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements-render.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers=2 main:app`

5. Add the following environment variables:
   - `SESSION_SECRET`: (generate a random value)
   - `FLASK_ENV`: production
   - `PYTHON_VERSION`: 3.11.8

6. Create a PostgreSQL database in Render:
   - Go to Dashboard -> New -> PostgreSQL
   - Link it to your web service

7. The application will automatically set up the database schema during first deployment.

### Database Migrations

If you need to update the database schema after deployment:

```bash
# For adding new columns to existing tables:
python update_db.py

# For completely resetting the database (warning: all data will be lost):
python recreate_db.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.