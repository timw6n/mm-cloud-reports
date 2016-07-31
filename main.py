#!/usr/bin/env python
from google.appengine.ext import vendor
vendor.add('lib')

import json
import jsonschema
import webapp2

from google.appengine.ext import ndb

from api_keys import API_KEYS
from report import Report

with open('resources/report.schema.json') as schema_file:
    REPORT_SCHEMA = json.load(schema_file)

class ReceiveJsonReport(webapp2.RequestHandler):
    def put(self):
        if not self.request.get('key') in API_KEYS:
            webapp2.abort(403)

        if self.request.content_type != 'application/json':
            webapp2.abort(400)

        if not self.request.body:
            webapp2.abort(400)

        report = json.loads(self.request.body)

        try:
            jsonschema.validate(report, REPORT_SCHEMA)
        except jsonschema.ValidationError:
            webapp2.abort(400)

        report_id = Report(contents=report).put().urlsafe()

        self.response.status_int = 201
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'url' : self.request.host_url + '/report/' + report_id + '/'}))

class DisplayHtmlReport(webapp2.RequestHandler):
    def get(self, report_id):
        try:
            report = ndb.Key(urlsafe=report_id).get()
        except:
            webapp2.abort(404)

        self.response.write(report.to_html())

class DisplayOriginalFile(webapp2.RequestHandler):
    def get(self, report_id, number):
        try:
            report = ndb.Key(urlsafe=report_id).get()
            result = report.contents['results'][int(number)]
            file = result['original']
        except:
            webapp2.abort(404)

        self.response.content_type = 'text/plain'
        self.response.write(file)

class DisplayMutantFile(webapp2.RequestHandler):
    def get(self, report_id, number):
        try:
            report = ndb.Key(urlsafe=report_id).get()
            result = report.contents['results'][int(number)]
            file = result['mutant']
        except:
            webapp2.abort(404)

        self.response.content_type = 'text/plain'
        self.response.write(file)

app = webapp2.WSGIApplication([
    ('/report/', ReceiveJsonReport),
    ('/report/([a-zA-Z0-9_-]+)/', DisplayHtmlReport),
    ('/report/([a-zA-Z0-9_-]+)/original/([0-9]+)', DisplayOriginalFile),
    ('/report/([a-zA-Z0-9_-]+)/mutant/([0-9]+)', DisplayMutantFile)
])
