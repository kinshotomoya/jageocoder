import os
import re
from typing import List

from flask import Flask, request, render_template, jsonify
from flask_cors import cross_origin

import jageocoder
from jageocoder.address import AddressLevel
jageocoder.init()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

url_prefix = os.environ.get('URL_PREFIX', '')
inner_url_prefix = os.environ.get('INNER_URL_PREFIX', '')
if url_prefix != "" and url_prefix[-1] == "/":
    url_prefix = url_prefix[:-1]
if inner_url_prefix != "" and inner_url_prefix[-1] == "/":
    inner_url_prefix = inner_url_prefix[:-1]

re_splitter = re.compile(r'[ \u2000,、]+')


def _split_args(val: str) -> List[str]:
    args = re_splitter.split(val)
    args = [x for x in args if x != '']
    return args


@app.route(inner_url_prefix + "/")
def index():
    query = request.args.get('q', '')
    skip_aza = request.args.get('skip_aza', 'auto')
    return render_template(
        'index.html',
        url_prefix=url_prefix,
        skip_aza=skip_aza,
        q=query, result=None)


@app.route(inner_url_prefix + "/webapi")
def webapi():
    return render_template('webapi.html')


@app.route(inner_url_prefix + "/search", methods=['POST', 'GET'])
def search():
    query = request.args.get('q')
    area = request.args.get('area', '')
    skip_aza = request.args.get('skip_aza', 'auto')
    if query:
        results = jageocoder.searchNode(
            query=query, best_only=True,
            aza_skip=skip_aza,
            target_area=_split_args(area))
    else:
        results = None

    return render_template(
        'index.html',
        url_prefix=url_prefix,
        skip_aza=skip_aza,
        area=area,
        q=query, results=results)


@app.route(inner_url_prefix + "/node/<id>", methods=['POST', 'GET'])
def show_node(id):
    node = jageocoder.get_module_tree().get_node_by_id(id)
    query = request.args.get('q', '')
    area = request.args.get('area', '')
    skip_aza = request.args.get('skip_aza', 'auto')

    return render_template(
        'node.html',
        url_prefix=url_prefix,
        skip_aza=skip_aza,
        area=area,
        q=query,
        node=node)


@app.route(inner_url_prefix + "/geocode", methods=['POST', 'GET'])
@cross_origin()
def geocode():
    if request.method == 'GET':
        query = request.args.get('addr', '')
        area = request.args.get('area', '')
        skip_aza = request.args.get('skip_aza', 'auto')
    else:
        query = request.form.get('addr', '')
        area = request.form.get('area', '')
        skip_aza = request.form.get('skip_aza', 'auto')

    if query:
        results = jageocoder.searchNode(
            query=query, best_only=True,
            target_area=_split_args(area),
            aza_skip=skip_aza)
    else:
        return "'addr' is required.", 400

    return jsonify([x.to_dict() for x in results]), 200


@app.route(inner_url_prefix + "/rgeocode", methods=['POST', 'GET'])
@cross_origin()
def reverse_geocode():
    if request.method == 'GET':
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        level = request.args.get('level', AddressLevel.AZA)
    else:
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        level = request.form.get('level', AddressLevel.AZA)

    if lat and lon:
        results = jageocoder.reverse(
            x=float(lon),
            y=float(lat),
            level=int(level))
    else:
        return "'lat' and 'lon' are required.", 400

    return jsonify(results), 200
