from waitress import serve
from member_portal.wsgi import application

serve(application, host='192.168.200.3', port=8000)
