# Educational portal

A Django-based educational portal with core functionality for conducting academic competitions.

---

## Table of Contents

- [Requirements](#requirements)  
- [Installation](#installation)  
- [Project Structure](#project-structure)
- [Contributing](#contributing)  

[//]: # (- [License]&#40;#license&#41;  )

---

## Requirements

- Python 3.11+  
- pip  
- virtualenv or built-in venv  

---

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Eramcheg/UaInternetOlimp
   cd UaInternetOlimp
   ```
   
2. **Create & activate a clean virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate    # macOS/Linux
    venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
   ```

4. **Configure environment**  

   - 4.1. Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env        # macOS/Linux
    copy .env.example .env      # Windows
    ```
   
   - 4.2 Place service Firebase key to credentials/key.json 

   - 4.3 Fill all variables
   ```env
     DEBUG=True
     DJANGO_SECRET_KEY=...
     FIREBASE_CREDENTIALS=credentials/key.json
     ...
   ```

5. **Apply migrations**
    ```bash
    python manage.py migrate
    ```

6. **Run the dev server**
    ```bash
    python manage.py runserver
    ```
   
---