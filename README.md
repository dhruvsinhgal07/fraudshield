# FraudShield 🛡️

AI-powered fraud detection system to identify scam messages, emails, and SMS.

## Features

- 🤖 **AI-Powered Detection** - Machine learning model to detect scams
- 🔗 **URL Analysis** - Identifies suspicious short URLs
- 📊 **Admin Dashboard** - Analytics and user management
- 📱 **Modern UI** - Glassmorphism design with smooth animations
- 👥 **Multi-User** - Role-based access (Admin/User)
- 📈 **History Tracking** - View all scam detection history

## Tech Stack

### Backend
- FastAPI
- Python 3.11+
- MySQL
- Scikit-learn (ML)
- JWT Authentication

### Frontend
- React 18
- Chart.js
- Modern CSS (Glassmorphism)

## Deployment

### Backend (Render)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your repository
5. Render will auto-detect `render.yaml`
6. Add environment variables:
   - `MYSQL_HOST`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`
7. Deploy!

### Frontend (Vercel - Recommended)

1. Push frontend to GitHub
2. Go to [Vercel](https://vercel.com/new)
3. Import your repository
4. Set build settings:
   - Framework: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`
5. Add environment variable:
   - `REACT_APP_API_URL` = your backend URL
6. Deploy!

### Frontend (Netlify Alternative)

1. Push to GitHub
2. Go to [Netlify](https://app.netlify.com/start)
3. Connect repository
4. Build settings auto-detected from `netlify.toml`
5. Deploy!

## Database Setup

Create MySQL database with these tables:

```sql
CREATE DATABASE fraudshield;

USE fraudshield;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  message TEXT NOT NULL,
  scam BOOLEAN NOT NULL,
  confidence FLOAT NOT NULL,
  user_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Environment Variables

### Backend
- `MYSQL_HOST` - Database host
- `MYSQL_USER` - Database user
- `MYSQL_PASSWORD` - Database password
- `MYSQL_DATABASE` - Database name
- `SECRET_KEY` - JWT secret key

### Frontend
- `REACT_APP_API_URL` - Backend API URL

## License

MIT

## Author

Your Name
