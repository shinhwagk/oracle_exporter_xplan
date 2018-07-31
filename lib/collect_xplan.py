import os
import argparse
import sys

import cx_Oracle

lastActiveSql = """SELECT sql_id, child_number FROM v$sql WHERE parsing_schema_name not in ('SYS', 'SYSTEM') AND last_active_time >= TRUNC(sysdate, 'MI') - 1 / 24 / 60 AND is_obsolete ='N' AND last_active_time < TRUNC(sysdate, 'MI')"""
sqlPlan = """SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(:sql_id, :child_number, 'ALL'))"""

# global variable
# store_path = ""


def oracle_query(conn):
    def oq(precess_cursor):
        l = []
        c = conn.cursor()
        precess_cursor(c, l)
        c.close()
        return l
    return oq


def collect_last_active_sql(c, l):
    for sql_id, child_number in c.execute(lastActiveSql):
        l.append((sql_id, child_number))


def collect_sql_plan(sql_id, child_number):
    def f(c, l):
        for txt, in c.execute(sqlPlan, sql_id=sql_id, child_number=child_number):
            l.append(txt)
    return f


def gen_sql_plan_file_path(store_path, sql_id, child_number):
    n = "%s_%s" % (sql_id, child_number)
    return os.path.join(store_path, n)


def judge_sql_plan_stored(store_path, sql_id, child_number):
    p = gen_sql_plan_file_path(store_path, sql_id, child_number)
    return os.path.exists(p)


def filter_stored_sql_plan(store_path, sqls):
    return list(filter(lambda ss: not judge_sql_plan_stored(store_path, ss[0], ss[1]), sqls))


def store_sql_plan(store_path, sql_id, child_number, sql_plan_texts):
    p = gen_sql_plan_file_path(store_path, sql_id, child_number)
    spts = list(map(lambda t: t + "\n", sql_plan_texts))
    with open(p, mode="w", encoding="utf8") as f:
        f.writelines(spts[:-1])


def create_store_xplan_dir(dp):
    if not os.path.exists(dp):
        os.makedirs(dp)


def collect(db_name, inst, data_source, store_path):
    conn = cx_Oracle.connect(data_source)
    dp = os.path.join(store_path, db_name, inst)
    create_store_xplan_dir(dp)
    process_query = oracle_query(conn)
    sqls = process_query(collect_last_active_sql)
    nsqls = filter_stored_sql_plan(dp, sqls)
    for s, c in nsqls:
        sxp = process_query(collect_sql_plan(s, c))  # sql_xplan sp
        store_sql_plan(dp, s, c, sxp)
    conn.close()


def main(db_name, inst,  data_source, store_path):
    try:
        collect(db_name, inst, data_source, store_path)
        print("collect xplan: {0}-{1} success.".format(db_name, inst))
    except BaseException as e:
        print("collect xplan: {0}-{1} failed, error: {2}".format(db_name, inst, str(e)))
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dn', '--db_name', help="db name", required=True)
    parser.add_argument('-i', '--inst', help="inst", required=True)
    parser.add_argument('-ds', '--data_source', help="data source", required=True)
    parser.add_argument('-sp', '--store_path', help="store path", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.db_name, args.inst, args.data_source, args.store_path)
