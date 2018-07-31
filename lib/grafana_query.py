from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qsl
import json
import os
import sys
import argparse

store_path = ""


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
    xf = get_xplan_file_path(store_path, db_name, inst, sql_id, child_number)
    xplan = get_xplan(xf)
    return "callback(%s)" % json.dumps({"xplan": xplan})


def get_xplan_file_path(store_plan, db_name, inst, sql_id, child_number):
    return os.path.join(store_plan, db_name, inst, "%s_%s" % (sql_id, child_number))


def get_xplan(xplan_file):
    data = ""
    with open(xplan_file) as f:
        data = f.read()
    return data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sp', '--store_path', help="store path", required=True)
    parser.add_argument('-pp', '--pid_path', help="pid path", required=True)
    return parser.parse_args()


def writePidFileIfNotExist(pid_path):
    pid_file_path = os.path.join(pid_path, "grafana_query.pid")
    if os.path.exists(pid_file_path):
        print("pid file: %s exist." % pid_file_path)
        sys.exit(1)
    else:
        pid = str(os.getpid())
        f = open(pid_file_path, 'w')
        f.write(pid)
        f.close()


def main(args):
    writePidFileIfNotExist(args.pid_path)
    global store_path
    store_path = args.store_path
    run(server_host='0.0.0.0', handler_class=XPlanHTTPRequestHandler)


if __name__ == "__main__":
    args = parse_args()
    main(args)
