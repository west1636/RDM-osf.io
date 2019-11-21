<%inherit file="base.mako"/>

<%def name="title()">${ _("Registries</%def>

<%def name="content()">
<h2>${ _("Registries service is not activated.</h2>
<ul>
<li>${ _("Set the following in local.py:</li>
<pre><code>USE_EXTERNAL_EMBER = True
EXTERNAL_EMBER_APPS = {
  'registries': {
    'url': '/registries/',
    'server': 'http://localhost:4300',
    'path': '/registries/'
  }
}</code></pre>
<li>${ _("Start the registries container with <code>docker-compose up -d registries</code>.") }</li>
</ul>
</%def>
