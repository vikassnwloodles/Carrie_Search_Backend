# Ask Pete Backend

This repository contains the backend for **Ask Pete** formerly known as **Carrie Search**.

## Setup Backend

Follow these steps to set up the backend locally:

1. **Clone the repository**
```bash
git clone https://github.com/vikassnwloodles/Carrie_Search_Backend.git
cd Carrie_Search_Backend/
````

2. **Add environment variables**

* Place the `.env` file in the project root.
* *(Contact the developer to obtain the `.env` file.)*

3. **Create and activate a virtual environment**

* Make sure you have **Python 3.12.3** installed.

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Run database migrations**

```bash
python manage.py migrate
```

6. **Start the development server**

```bash
python manage.py runserver
```

The backend will be accessible at `http://127.0.0.1:8000/` by default.

---

## Notes

* Ensure the `.env` file contains all required environment variables for proper functionality.
* Recommended Python version: **3.12.3**
