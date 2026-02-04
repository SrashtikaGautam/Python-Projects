# Glamour Salon - Beauty Redefined

Welcome to Glamour Salon, a premium salon experience designed exclusively for women. This Streamlit web application offers a complete salon management system with appointment booking, service catalog, and user management.

## Features

- 🎀 **User Authentication**: Simple login with name and phone number
- 💇‍♀️ **Service Catalog**: Comprehensive list of salon services with pricing and descriptions
- 📅 **Appointment Booking**: Easy booking system with date and time selection
- 🗓️ **Appointment Management**: View and cancel your appointments
- 📸 **Gallery**: Visual showcase of our salon and services
- 📞 **Contact Information**: Complete contact details and social media links

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the Glamour Salon website, run:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` in your web browser.

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── config.json         # Salon configuration
└── README.md           # This file
```

## Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with pandas and sqlite3
- **Database**: SQLite (automatically created)
- **Styling**: Custom CSS with Google Fonts (Playfair Display, Poppins)

## Usage

1. Open the application in your browser
2. Login with your name and phone number
3. Explore services in the "Services" section
4. Book appointments in the "Book Appointment" section
5. Manage your appointments in "My Appointments"
6. View our gallery and contact information

## Customization

You can customize the salon information by editing the `config.json` file:
- Update salon name, tagline, and contact information
- Modify business hours
- Change social media links
- Adjust color theme

## Contributing

This project is designed for educational purposes. Feel free to fork and modify for your own use.

## License

This project is open source and available under the MIT License.