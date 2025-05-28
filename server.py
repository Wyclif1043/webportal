from waitress import serve
from member_portal.wsgi import application

serve(application, host='197.232.170.121', port=8000)
