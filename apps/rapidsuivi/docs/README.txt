--------------
CREATE TRANSLATION MESSAGES
--------------
cd  rapidsuivi
mkdir locale
django-admin makemessages -l fr
django-admin makemessages -l en

1 - Partout ou django-admin trouvera _(message-key)
il ajoutera directement dans /locale/LC_MESSAGES/fr/django.po
le message key (message-key)


------------------
COMPILE MESSAGES
-----------------

django-admin compilemessages

-------------
TESTE
-------------
cd project_dir
python  rapidsms test rapidsuivi
