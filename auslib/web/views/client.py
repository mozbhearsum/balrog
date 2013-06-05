from flask import make_response, request
from flask.views import MethodView

from auslib.web.base import AUS

import logging

class ClientRequestView(MethodView):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        MethodView.__init__(self, *args, **kwargs)

    def getHeaderArchitecture(self, buildTarget, ua):
        if buildTarget.startswith('Darwin'):
            if ua and 'PPC' in ua:
                return 'PPC'
            else:
                return 'Intel'
        else:
            return 'Intel'

    def getQueryFromURL(self, queryVersion, url):
        query = url.copy()
        if queryVersion in (2, 3, 4):
            query['name'] = AUS.identifyRequest(query)
            ua = request.headers.get('User-Agent')
            query['headerArchitecture'] = self.getHeaderArchitecture(query['buildTarget'], ua)
            query['force'] = (int(request.args.get('force', 0)) == 1)
            return query
        return {}

    def get(self, queryVersion, **url):
        query = self.getQueryFromURL(queryVersion, url)
        self.log.debug("Got query: %s", query)
        if query:
            rule = AUS.evaluateRules(query)
        else:
            rule = {}
        # passing {},{} returns empty xml
        self.log.debug("Got rule: %s", rule)
        xml = AUS.createXML(query, rule)
        self.log.debug("Sending XML: %s", xml)
        response = make_response(xml)
        response.mimetype = 'text/xml'
        return response
