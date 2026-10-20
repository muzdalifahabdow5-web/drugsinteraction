# -*- coding: utf-8 -*-
"""
fix_schema.py - يضيف الأعمدة والجداول الناقصة إلى قاعدة Aiven دون حذف أي بيانات.
يقرأ البنية الصحيحة من import_schema.py (يجب أن يكون في نفس المجلد).

التشغيل:  python fix_schema.py
"""
import ast
import re
import pymysql
from urllib.parse import urlparse, unquote


def load_statements():
    src = open('import_schema.py', encoding='utf8').read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'STATEMENTS':
            return ast.literal_eval(node.value)
    raise SystemExit('لم أجد STATEMENTS داخل import_schema.py')


def split_top(body):
    parts, depth, cur = [], 0, ''
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def parse_create(stmt):
    m = re.match(r'CREATE TABLE IF NOT EXISTS `(\w+)`\s*\((.*)\)\s*ENGINE', stmt, re.S)
    if not m:
        return None
    cols = {}
    for p in split_top(m.group(2)):
        if re.match(r'(PRIMARY|UNIQUE|KEY|CONSTRAINT)\b', p, re.I):
            continue
        cm = re.match(r'`(\w+)`', p)
        if cm:
            cols[cm.group(1)] = p
    return m.group(1), cols


uri = input('Paste your DATABASE_URL here, then press Enter: ').strip()
u = urlparse(uri)
if not u.username or not u.hostname:
    raise SystemExit('The link is empty or incomplete. It must start with mysql://')
db = u.path.lstrip('/').split('?')[0]
conn = pymysql.connect(host=u.hostname, port=u.port or 3306, user=unquote(u.username),
                       password=unquote(u.password or ''), database=db, charset='utf8mb4',
                       ssl={'fake_flag_to_enable_tls': True}, autocommit=True)
cur = conn.cursor()
print('Connected to database:', db)

cur.execute('SHOW TABLES')
have_tables = {r[0] for r in cur.fetchall()}
changes = 0
for stmt in load_statements():
    parsed = parse_create(stmt)
    if not parsed:
        continue
    table, cols = parsed
    if table not in have_tables:
        cur.execute(stmt)
        print('Created missing table:', table)
        changes += 1
        continue
    cur.execute('SELECT COLUMN_NAME FROM information_schema.COLUMNS '
                'WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s', (db, table))
    existing = {r[0] for r in cur.fetchall()}
    for name, definition in cols.items():
        if name not in existing:
            cur.execute(f'ALTER TABLE `{table}` ADD COLUMN {definition}')
            print(f'Added column: {table}.{name}')
            changes += 1

print('Done. Changes made:', changes)