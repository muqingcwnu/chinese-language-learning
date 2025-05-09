# China's Legacy - Chinese Language Learning Platform 🇨🇳

A comprehensive web application for learning Mandarin Chinese, featuring interactive lessons, vocabulary practice, quizzes, and a social learning community.

## 🌟 Features

### 1. Learning Resources
- **Grammar Lessons**: Structured lessons for HSK levels 1-6
- **Vocabulary Training**: Interactive vocabulary learning with audio support
- **Pinyin Chart**: Interactive chart for learning Chinese pronunciation
- **AI-Powered Assistant**: Get instant help with language learning
- **PDF Textbooks**: Access to digital learning materials

### 2. Interactive Learning
- **Quizzes**: Test your knowledge with various quiz types:
  - Vocabulary quizzes
  - Grammar exercises
  - Sentence rearrangement
- **Progress Tracking**: Monitor your learning journey
- **Learning Streaks**: Stay motivated with daily learning goals
- **Points System**: Earn points for completing activities

### 3. Social Features
- **Timeline**: Share your learning progress and interact with others
- **User Connections**: Connect with fellow learners
- **Messaging System**: Private messaging between users
- **Comments & Reactions**: Engage with community posts
- **Notifications**: Stay updated with learning reminders and social interactions

### 4. User Profile
- **Customizable Profile**: Add personal and academic information
- **Progress Dashboard**: Visual representation of learning progress
- **Learning Statistics**: Track completed lessons, quizzes, and vocabulary
- **HSK Level Management**: Set and update your current HSK level

## 🛠️ Technology Stack

- **Backend**: Django 4.2
- **Frontend**: 
  - HTML5, CSS3, JavaScript
  - Tailwind CSS
  - Alpine.js
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django Allauth
- **Admin Interface**: Django Jazzmin
- **Form Handling**: Django Crispy Forms
- **API Integration**: DeepSeek AI API
- **File Storage**: Django Storage

## 📋 Prerequisites

- Python 3.8+
- Node.js and npm (for frontend assets)
- Virtual environment (recommended)
- DeepSeek API key

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chinas-legacy.git
   cd chinas-legacy
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   DEEPSEEK_API_KEY=your_deepseek_api_key
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Admin Interface
The admin interface is enhanced using Django Jazzmin with a custom theme matching the application's design.

### Email Configuration
Configure your email settings in `.env` for:
- User registration
- Password reset
- Notifications

### Static Files
- Development: Served by Django
- Production: Use Whitenoise for static file serving

## 👥 User Roles

1. **Regular Users**
   - Access learning materials
   - Take quizzes
   - Interact with community
   - Track progress

2. **Admin Users**
   - Manage user accounts
   - Add/edit learning content
   - Monitor user progress
   - Manage system settings

## 🔒 Security Features

- CSRF Protection
- Secure password hashing
- Session security
- XSS Prevention
- HTTPS enforcement in production
- Protected media files
- Rate limiting

## 📱 Responsive Design

The platform is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile devices

## 🌐 Internationalization

- English and Chinese language support
- Easy language switching
- Localized content and interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

- **Parvez** - [GitHub Profile](https://github.com/yourusername)
- Email: Parvez@stu.cwnu.edu.cn
- Phone: +861390213905

## 🙏 Acknowledgments

- China West Normal University
- DeepSeek AI for API support
- All contributors and testers

## 📞 Support

For support, please email Parvez@stu.cwnu.edu.cn or create an issue in the repository. 
