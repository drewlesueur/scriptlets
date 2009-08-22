import wsgiref.handlers
import urllib, cgi

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from models import Script, baseN
import time


    


class MainHandler(webapp.RequestHandler):
    def _save_and_redirect(self, name, language, code):
        if name == "":
            name = baseN(abs(hash(time.time())), 36)
        
        script = Script.all().filter('name =', name).get()
        if (script):
            script.language = language
            script.code = code
            script.put()
        else:    
            script = Script(name=name, language=language, code=code)
            script.put()
        self.redirect('/view/%s' % script.name)
        
    def get(self):
        self._get_main('', '', '')
        
    def _get_main(self, name, language, code):
    
        
        user = users.get_current_user()
        auth_save = self.request.cookies.get('auth_save', None)
        if auth_save:
            self.response.headers.add_header('Set-Cookie', 'auth_save=; expires=Wed, 11-Sep-1985 11:00:00 GMT')
            params = cgi.parse_qs(auth_save)
            self._save_and_redirect(params['name'][0], params['language'][0], params['code'][0])
        else:
            scripts = Script.all().filter('user =', user)
            scripts = scripts.fetch(1000)
            
            params = {'user': user, 'scripts': scripts, 'name': name, 'language': language, 'code': code}
            if user:
                params['logout_url'] = users.create_logout_url("/")
            else:
                params['login_url'] = users.create_login_url('/')
            self.response.out.write(template.render('templates/main.html', params))

    def post(self):
        user = users.get_current_user()
        language = self.request.POST['language']
        code = self.request.POST['%s-code' % language]
        name = self.request.POST['name']
        if user:
            self._save_and_redirect(name, language, code)
        else:
            auth_save = {'language': language, 'code': code, 'name' : name}
            self.response.headers.add_header('Set-Cookie', 'auth_save=%s' % urllib.urlencode(auth_save))
            self.redirect(users.create_login_url("/"))

if __name__ == '__main__':
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/', MainHandler)], debug=True))
