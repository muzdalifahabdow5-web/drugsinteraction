# -*- coding: utf-8 -*-
"""
backup_db.py - نسخة احتياطية كاملة من قاعدة البيانات إلى ملف .sql
(الجداول + البيانات + الـ triggers)
هذا السكربت للقراءة فقط (SELECT / SHOW). لا يغيّر ولا يحذف أي شيء في القاعدة.
"""
import datetime
import re
from urllib.parse import urlparse, unquote

import pymysql
from pymysql.converters import escape_item


def main():
    uri = input('الصق رابط القاعدة ثم اضغط Enter: ').strip()
    u = urlparse(uri)
    if not u.username or not u.hostname:
        raise SystemExit('الرابط ناقص. يجب أن يبدأ بـ mysql://')
    db = u.path.lstrip('/')
    conn = pymysql.connect(
        host=u.hostname, port=u.port or 3306, user=unquote(u.username),
        password=unquote(u.password or ''), database=db,
        charset='utf8mb4', ssl={'fake_flag_to_enable_tls': True}, autocommit=True)
    cur = conn.cursor()
    print('تم الاتصال بالقاعدة:', db)

    cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
    tables = [r[0] for r in cur.fetchall()]
    if not tables:
        raise SystemExit('القاعدة فارغة، لا يوجد ما يُنسخ.')

    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    fname = 'backup_%s_%s.sql' % (db, stamp)
    counts = []
    with open(fname, 'w', encoding='utf-8', newline='\n') as out:
        out.write('-- Backup of `%s` created %s\n' % (db, datetime.datetime.now()))
        out.write('SET NAMES utf8mb4;\nSET FOREIGN_KEY_CHECKS=0;\n\n')
        for t in tables:
            cur.execute('SHOW CREATE TABLE `%s`' % t)
            create = cur.fetchone()[1]
            out.write('-- ----------------------------\n-- Table `%s`\n-- ----------------------------\n' % t)
            out.write('DROP TABLE IF EXISTS `%s`;\n%s;\n\n' % (t, create))
            cur.execute('SELECT * FROM `%s`' % t)
            cols = [d[0] for d in cur.description]
            collist = ', '.join('`%s`' % c for c in cols)
            n = 0
            batch = []
            for row in cur.fetchall():
                vals = ', '.join(escape_item(v, 'utf8mb4') for v in row)
                batch.append('(%s)' % vals)
                n += 1
                if len(batch) >= 100:
                    out.write('INSERT INTO `%s` (%s) VALUES\n%s;\n' % (t, collist, ',\n'.join(batch)))
                    batch = []
            if batch:
                out.write('INSERT INTO `%s` (%s) VALUES\n%s;\n' % (t, collist, ',\n'.join(batch)))
            out.write('\n')
            counts.append((t, n))
        out.write('SET FOREIGN_KEY_CHECKS=1;\n\n')

        # ---- الـ triggers ----
        cur.execute('SHOW TRIGGERS')
        trigger_names = [r[0] for r in cur.fetchall()]
        out.write('-- ----------------------------\n-- Triggers\n-- ----------------------------\n')
        out.write('DELIMITER $$\n')
        for tr in trigger_names:
            cur.execute('SHOW CREATE TRIGGER `%s`' % tr)
            stmt = cur.fetchone()[2]
            stmt = re.sub(r'DEFINER\s*=\s*`[^`]*`@`[^`]*`\s*', '', stmt)
            out.write('DROP TRIGGER IF EXISTS `%s`$$\n%s$$\n' % (tr, stmt))
        out.write('DELIMITER ;\n')
    conn.close()

    print('\nتمت النسخة الاحتياطية بنجاح. اسم الملف:', fname)
    print('عدد الصفوف في كل جدول:')
    for t, n in counts:
        print('  %-28s %d' % (t, n))
    print('عدد الـ triggers المحفوظة:', len(trigger_names), '->', ', '.join(trigger_names))
    print('\nاحتفظ بالملف في مكان آمن (وانسخه إلى فلاشة أو Google Drive).')


if __name__ == '__main__':
    main()