from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qsl
import argparse
import json

from xplan import display_cursor


class XPlanHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/javascript')
        self.end_headers()
        if str.startswith(self.path, '/xplan?'):
            message = gen_xplan_response(self.path)
            self.wfile.write(bytes(message, "utf8"))
        else:
            self.wfile.write(bytes('', "utf8"))
        return


def run(server_host='127.0.0.1', server_port=8080, server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    print('starting server...')
    server_address = (server_host, server_port)
    httpd = server_class(server_address, handler_class)
    print('running server...')
    httpd.serve_forever()


def parse_path_args(path):
    o = urlparse(path)
    return dict(parse_qsl(o.query))


def gen_xplan_response(path):
    url_args = parse_path_args(path)
    sql_id = url_args["sql_id"]
    child_number = url_args["child"]
    db_name = url_args["db_name"]
    inst = url_args["inst"]
    name = "%s-%s" % (db_name, inst)
    dsn = get_config()[name]
    xplan = display_cursor(dsn, sql_id, child_number).to_str()
    return "callback(%s)" % json.dumps({"xplan": xplan})


def get_config():
    dsns = {}
    with open(config_file) as f:
        dsns = json.loads(f.read())
    return dsns


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-cf', '--config_file', help="data source file path", required=True)
    return parser.parse_args()


def main(args):
    global config_file
    config_file = args.config_file
    run(server_host='0.0.0.0', handler_class=XPlanHTTPRequestHandler)


if __name__ == "__main__":
    args = parse_args()
    main(args)
