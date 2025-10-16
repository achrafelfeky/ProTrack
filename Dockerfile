# استخدم نسخة Python كاملة لتجنب مشاكل PATH
FROM python:3.12

WORKDIR /app

# تحديث pip والتأكد من تثبيته
RUN python -m ensurepip --upgrade
RUN pip install --upgrade pip

# نسخ وتثبيت الباكيجات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# أمر تشغيل Gunicorn
CMD ["gunicorn", "managementproject.wsgi:application", "--bind", "0.0.0.0:8000"]
