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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.