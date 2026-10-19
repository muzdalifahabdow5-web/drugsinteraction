# -*- coding: utf-8 -*-
"""
migrate_age.py - ترحيل قاعدة البيانات الحيّة (Aiven) إلى المخطط الجديد
(العمر بالأيام / الأشهر / السنوات + الفئات العمرية + أشكال الدواء + جدول الجرعات)

- يحافظ على كل بياناتك الحالية (أدوية، تفاعلات، مستخدمين، مرضى...) ولا يحذف أي صف.
- آمن عند التشغيل أكثر من مرة: كل خطوة تتحقق أولاً هل نُفّذت من قبل.
- شغّله بعد أخذ نسخة احتياطية (backup_db.py).

الاستخدام في cmd:
    pip install pymysql cryptography
    python migrate_age.py
"""
import math
from urllib.parse import urlparse, unquote

import pymysql

EXPECTED = {
    'age_groups': ['id', 'name_arabic', 'name_english', 'min_days', 'max_days', 'sort_order', 'description'],
    'associated_symptoms': ['id', 'name_arabic', 'name_english', 'description'],
    'ckeck_medicines': ['ckeck_id', 'drug_id', 'dosage_form_id'],
    'dosage_forms': ['id', 'name_arabic', 'name_english'],
    'drug_classification': ['id', 'name_arabic', 'name_english', 'description'],
    'drug_contraindications': ['id', 'medication_id', 'condition_id', 'pregnancy_risk', 'age_group_id', 'severity', 'description', 'min_age_days', 'max_age_days'],
    'drug_interactions': ['interaction_id', 'drug_1_id', 'drug_2_id', 'severity', 'description'],
    'health_conditions': ['id', 'condition_name', 'condition_description', 'condition_category'],
    'interaction_age_groups': ['interaction_id', 'age_group_id', 'severity', 'notes'],
    'interaction_checks': ['check_id', 'check_date', 'user_id', 'patient_id', 'age_days', 'age_group_id'],
    'interaction_conditions': ['condition_id', 'interaction_check_id', 'notes'],
    'med_associated': ['medicine_id', 'associated_symptom_id'],
    'medication_dosing': ['id', 'medication_id', 'age_group_id', 'dosage_form_id', 'dose_amount', 'dose_unit', 'is_per_kg', 'times_per_day', 'max_daily_dose', 'notes'],
    'medications': ['id', 'scientific_name', 'trade_name', 'dosage_form_id', 'concentration', 'dosage', 'warning', 'classification_id'],
    'medicine_sideeffects': ['medicine_id', 'side_effect_id'],
    'password_resets': ['id', 'user_id', 'code_hash', 'expires_at', 'attempts', 'used', 'created_at'],
    'patient_conditions': ['patient_id', 'condition_id', 'notes'],
    'patients': ['patient_id', 'name', 'is_pregnant', 'gender', 'user_id', 'age_value', 'age_unit', 'age_days', 'age_group_id'],
    'pharmacists': ['pharmacist_id', 'license_number', 'name', 'phone_number', 'user_id'],
    'player_attempts': ['attempt_id', 'player_id', 'question_id', 'selected_option', 'is_correct', 'attempted_at'],
    'players': ['player_id', 'username', 'email', 'total_score', 'created_at', 'user_id'],
    'questions': ['question_id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'difficulty', 'interaction_id', 'source_key'],
    'side_effects': ['id', 'name_arabic', 'name_english', 'description', 'severity'],
    'user_chronic_conditions': ['user_id', 'condition_id'],
    'user_health_profiles': ['user_id', 'is_pregnant', 'age_value', 'age_unit', 'age_days', 'age_group_id'],
    'users': ['id', 'username', 'email', 'password', 'role', 'created_at'],
}

AGE_GROUPS = [
    (1, 'حديث الولادة', 'Neonate', 0, 29, 1, 'من يوم الولادة حتى أقل من شهر'),
    (2, 'رضيع', 'Infant', 30, 364, 2, 'من شهر حتى أقل من سنة'),
    (3, 'طفل صغير', 'Toddler', 365, 1095, 3, 'من سنة حتى أقل من 3 سنوات'),
    (4, 'طفل', 'Child', 1096, 4382, 4, 'من 3 حتى أقل من 12 سنة'),
    (5, 'مراهق', 'Adolescent', 4383, 6574, 5, 'من 12 حتى أقل من 18 سنة'),
    (6, 'بالغ', 'Adult', 6575, 23740, 6, 'من 18 حتى أقل من 65 سنة'),
    (7, 'مسن', 'Elderly', 23741, None, 7, '65 سنة فأكثر'),
]

DOSAGE_FORMS = [
    (1, 'أقراص', 'Tablet'), (2, 'كبسولات', 'Capsule'), (3, 'شراب', 'Syrup'),
    (4, 'معلق', 'Suspension'), (5, 'قطرة', 'Drops'), (6, 'حقن', 'Injection'),
    (7, 'تحاميل', 'Suppository'), (8, 'كريم / مرهم', 'Cream / Ointment'),
    (9, 'بخاخ', 'Inhaler / Spray'), (10, 'أكياس / مسحوق', 'Powder / Sachet'),
]

# كلمات قد تكون مكتوبة في عمود dosage_form القديم وما يقابلها من الأشكال الجديدة
FORM_SYNONYMS = {
    1: ['tablet', 'tablets', 'tab', 'قرص', 'أقراص', 'اقراص', 'حبوب', 'حبة'],
    2: ['capsule', 'capsules', 'cap', 'كبسولة', 'كبسولات', 'كبسول'],
    3: ['syrup', 'شراب'],
    4: ['suspension', 'معلق', 'معلّق'],
    5: ['drops', 'drop', 'قطرة', 'قطرات', 'نقط'],
    6: ['injection', 'inj', 'حقن', 'حقنة', 'إبرة', 'ابرة', 'أمبولة', 'امبولة'],
    7: ['suppository', 'suppositories', 'تحاميل', 'تحميلة', 'لبوس'],
    8: ['cream', 'ointment', 'كريم', 'مرهم'],
    9: ['inhaler', 'spray', 'بخاخ', 'بخاخة'],
    10: ['powder', 'sachet', 'مسحوق', 'أكياس', 'اكياس', 'كيس'],
}

TRIGGERS = [
    ('trg_di_before_insert', """CREATE TRIGGER `trg_di_before_insert` BEFORE INSERT ON `drug_interactions`
 FOR EACH ROW BEGIN
  IF NEW.drug_1_id = NEW.drug_2_id THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'drug_1_id and drug_2_id must be different';
  END IF;
END"""),
    ('trg_di_before_update', """CREATE TRIGGER `trg_di_before_update` BEFORE UPDATE ON `drug_interactions`
 FOR EACH ROW BEGIN
  IF NEW.drug_1_id = NEW.drug_2_id THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'drug_1_id and drug_2_id must be different';
  END IF;
END"""),
    ('trg_checks_age_bi', """CREATE TRIGGER `trg_checks_age_bi` BEFORE INSERT ON `interaction_checks`
 FOR EACH ROW BEGIN
  IF NEW.patient_id IS NOT NULL AND NEW.age_days IS NULL THEN
    SET NEW.age_days     = (SELECT p.age_days     FROM patients p WHERE p.patient_id = NEW.patient_id);
    SET NEW.age_group_id = (SELECT p.age_group_id FROM patients p WHERE p.patient_id = NEW.patient_id);
  END IF;
END"""),
]


def _age_trigger(name, timing, table, with_else):
    els = "\n  ELSE\n    SET NEW.age_days = NULL, NEW.age_group_id = NULL;" if with_else else ""
    return ("""CREATE TRIGGER `%s` BEFORE %s ON `%s`
 FOR EACH ROW BEGIN
  IF NEW.age_value IS NOT NULL THEN
    SET NEW.age_days = CASE NEW.age_unit
        WHEN 'day'   THEN NEW.age_value
        WHEN 'month' THEN ROUND(NEW.age_value * 30.4375)
        ELSE ROUND(NEW.age_value * 365.25) END;
    SET NEW.age_group_id = (SELECT g.id FROM age_groups g
        WHERE NEW.age_days >= g.min_days AND (g.max_days IS NULL OR NEW.age_days <= g.max_days)
        ORDER BY g.min_days LIMIT 1);%s
  END IF;
END""" % (name, timing, table, els))


TRIGGERS += [
    ('trg_patients_age_bi', _age_trigger('trg_patients_age_bi', 'INSERT', 'patients', False)),
    ('trg_patients_age_bu', _age_trigger('trg_patients_age_bu', 'UPDATE', 'patients', True)),
    ('trg_uhp_age_bi', _age_trigger('trg_uhp_age_bi', 'INSERT', 'user_health_profiles', False)),
    ('trg_uhp_age_bu', _age_trigger('trg_uhp_age_bu', 'UPDATE', 'user_health_profiles', True)),
]

conn = None
cur = None


def q(sql, args=None):
    cur.execute(sql, args)
    return cur.fetchall()


def table_exists(t):
    return bool(q("SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s", (t,)))


def col_exists(t, c):
    return bool(q("SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s", (t, c)))


def fk_exists(t, name):
    return bool(q("SELECT 1 FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME=%s "
                  "AND CONSTRAINT_NAME=%s AND CONSTRAINT_TYPE='FOREIGN KEY'", (t, name)))


def run(label, sql, args=None):
    cur.execute(sql, args)
    print('  [تم] ' + label)


def add_fk(table, name, ddl):
    if not fk_exists(table, name):
        run('إضافة المفتاح الأجنبي %s على %s' % (name, table), 'ALTER TABLE `%s` ADD CONSTRAINT `%s` %s' % (table, name, ddl))


def days_from_years(y):
    return int(math.floor(y * 365.25 + 0.5))


# ---------------------------------------------------------------- الخطوات
def step_new_tables():
    print('\n[1] الجداول الجديدة والبيانات المرجعية')
    if not table_exists('age_groups'):
        run('إنشاء age_groups', """CREATE TABLE `age_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_arabic` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_english` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `min_days` int(11) NOT NULL,
  `max_days` int(11) DEFAULT NULL,
  `sort_order` tinyint(4) NOT NULL DEFAULT '0',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_age_groups_name` (`name_english`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    for r in AGE_GROUPS:
        cur.execute("INSERT IGNORE INTO `age_groups` (`id`,`name_arabic`,`name_english`,`min_days`,`max_days`,`sort_order`,`description`) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", r)
    print('  [تم] الفئات العمرية (7 فئات)')

    if not table_exists('dosage_forms'):
        run('إنشاء dosage_forms', """CREATE TABLE `dosage_forms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_arabic` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_english` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dosage_forms_ar` (`name_arabic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    for r in DOSAGE_FORMS:
        cur.execute("INSERT IGNORE INTO `dosage_forms` (`id`,`name_arabic`,`name_english`) VALUES (%s,%s,%s)", r)
    print('  [تم] أشكال الدواء (10 أشكال)')

    if not table_exists('interaction_age_groups'):
        run('إنشاء interaction_age_groups', """CREATE TABLE `interaction_age_groups` (
  `interaction_id` int(11) NOT NULL,
  `age_group_id` int(11) NOT NULL,
  `severity` enum('minor','moderate','major') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`interaction_id`,`age_group_id`),
  KEY `fk_iag_age_group` (`age_group_id`),
  CONSTRAINT `fk_iag_interaction` FOREIGN KEY (`interaction_id`) REFERENCES `drug_interactions` (`interaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_iag_age_group` FOREIGN KEY (`age_group_id`) REFERENCES `age_groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    if not table_exists('medication_dosing'):
        run('إنشاء medication_dosing', """CREATE TABLE `medication_dosing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `medication_id` int(11) NOT NULL,
  `age_group_id` int(11) NOT NULL,
  `dosage_form_id` int(11) NOT NULL,
  `dose_amount` decimal(10,2) DEFAULT NULL,
  `dose_unit` enum('mg','mcg','g','ml','IU','tablet','drop') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'mg',
  `is_per_kg` tinyint(1) NOT NULL DEFAULT '0',
  `times_per_day` tinyint(3) unsigned DEFAULT NULL,
  `max_daily_dose` decimal(10,2) DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dosing` (`medication_id`,`age_group_id`,`dosage_form_id`),
  KEY `fk_dosing_age_group` (`age_group_id`),
  KEY `fk_dosing_form` (`dosage_form_id`),
  CONSTRAINT `fk_dosing_medication` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dosing_age_group` FOREIGN KEY (`age_group_id`) REFERENCES `age_groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dosing_form` FOREIGN KEY (`dosage_form_id`) REFERENCES `dosage_forms` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")


def resolve_form(txt, forms):
    """يرجع رقم شكل الدواء المناسب للنص القديم، وإن لم يجد يُنشئ شكلاً جديداً بنفس النص."""
    norm = ' '.join(str(txt).strip().lower().split())
    if norm in forms:
        return forms[norm]
    for fid, words in FORM_SYNONYMS.items():
        if norm in [w.lower() for w in words]:
            return fid
    pairs = sorted(((w.lower(), fid) for fid, ws in FORM_SYNONYMS.items() for w in ws if len(w) >= 3),
                   key=lambda p: -len(p[0]))
    for w, fid in pairs:
        if w in norm:
            return fid
    name = str(txt).strip()[:100]
    cur.execute("INSERT IGNORE INTO `dosage_forms` (`name_arabic`,`name_english`) VALUES (%s,%s)", (name, name))
    fid = q("SELECT id FROM dosage_forms WHERE name_arabic=%s", (name,))[0][0]
    forms[norm] = fid
    print('  [تنبيه] شكل دواء غير معروف "%s" أُضيف كشكل جديد (رقم %d). يمكنك تسميته لاحقاً.' % (name, fid))
    return fid


def step_medications():
    print('\n[2] الأدوية: تحويل شكل الدواء من نص إلى جدول dosage_forms')
    t = 'medications'
    if not col_exists(t, 'dosage_form_id'):
        run('إضافة العمود dosage_form_id',
            "ALTER TABLE `medications` ADD COLUMN `dosage_form_id` int(11) DEFAULT NULL AFTER `trade_name`, "
            "ADD KEY `fk_med_dosage_form` (`dosage_form_id`)")
    if col_exists(t, 'dosage_form'):
        forms = {}
        for fid, ar, en in q("SELECT id, name_arabic, name_english FROM dosage_forms"):
            forms[ar.strip().lower()] = fid
            forms[en.strip().lower()] = fid
        n = 0
        for mid, txt in q("SELECT id, dosage_form FROM medications"):
            if txt is None or not str(txt).strip():
                continue
            fid = resolve_form(txt, forms)
            cur.execute("UPDATE medications SET dosage_form_id=%s WHERE id=%s AND dosage_form_id IS NULL", (fid, mid))
            n += 1
        print('  [تم] تحويل شكل الدواء لـ %d دواء' % n)
    add_fk(t, 'fk_med_dosage_form',
           "FOREIGN KEY (`dosage_form_id`) REFERENCES `dosage_forms` (`id`) ON DELETE SET NULL ON UPDATE CASCADE")
    if col_exists(t, 'dosage_form'):
        run('حذف العمود القديم dosage_form', "ALTER TABLE `medications` DROP COLUMN `dosage_form`")


def step_check_medicines():
    print('\n[3] ckeck_medicines: إضافة dosage_form_id')
    t = 'ckeck_medicines'
    if not col_exists(t, 'dosage_form_id'):
        run('إضافة العمود dosage_form_id',
            "ALTER TABLE `ckeck_medicines` ADD COLUMN `dosage_form_id` int(11) DEFAULT NULL, "
            "ADD KEY `fk_check_med_form` (`dosage_form_id`)")
    add_fk(t, 'fk_check_med_form',
           "FOREIGN KEY (`dosage_form_id`) REFERENCES `dosage_forms` (`id`) ON DELETE SET NULL ON UPDATE CASCADE")


def step_age_table(num, table, fk_name, required):
    print('\n[%d] %s: العمر (قيمة + وحدة + أيام + فئة عمرية)' % (num, table))
    if not col_exists(table, 'age_value'):
        run('إضافة أعمدة العمر الجديدة',
            "ALTER TABLE `%s` "
            "ADD COLUMN `age_value` int(10) unsigned DEFAULT NULL, "
            "ADD COLUMN `age_unit` enum('day','month','year') NOT NULL DEFAULT 'year', "
            "ADD COLUMN `age_days` int(11) DEFAULT NULL, "
            "ADD COLUMN `age_group_id` int(11) DEFAULT NULL, "
            "ADD KEY `%s` (`age_group_id`)" % (table, fk_name))
    if col_exists(table, 'age'):
        cur.execute(
            "UPDATE `%(t)s` SET age_value=age, age_unit='year', age_days=ROUND(age*365.25), "
            "age_group_id=(SELECT g.id FROM age_groups g WHERE ROUND(`%(t)s`.age*365.25) >= g.min_days "
            "AND (g.max_days IS NULL OR ROUND(`%(t)s`.age*365.25) <= g.max_days) ORDER BY g.min_days LIMIT 1) "
            "WHERE age IS NOT NULL AND age_value IS NULL" % {'t': table})
        print('  [تم] نقل العمر القديم (بالسنوات) إلى الأعمدة الجديدة: %d صف' % cur.rowcount)
    if required:
        nulls = q("SELECT COUNT(*) FROM `%s` WHERE age_value IS NULL" % table)[0][0]
        if nulls == 0:
            run('جعل age_value إلزامياً', "ALTER TABLE `%s` MODIFY `age_value` int(10) unsigned NOT NULL" % table)
        else:
            print('  [تنبيه] يوجد %d صف بلا عمر، لذلك لم أجعل age_value إلزامياً.' % nulls)
    add_fk(table, fk_name,
           "FOREIGN KEY (`age_group_id`) REFERENCES `age_groups` (`id`) ON DELETE SET NULL ON UPDATE CASCADE")
    if col_exists(table, 'age'):
        run('حذف العمود القديم age', "ALTER TABLE `%s` DROP COLUMN `age`" % table)


def step_checks():
    print('\n[6] interaction_checks: العمر وقت الفحص')
    t = 'interaction_checks'
    if not col_exists(t, 'age_days'):
        run('إضافة أعمدة العمر',
            "ALTER TABLE `interaction_checks` ADD COLUMN `age_days` int(11) DEFAULT NULL, "
            "ADD COLUMN `age_group_id` int(11) DEFAULT NULL, ADD KEY `fk_checks_age_group` (`age_group_id`)")
    cur.execute("UPDATE interaction_checks c JOIN patients p ON p.patient_id=c.patient_id "
                "SET c.age_days=p.age_days, c.age_group_id=p.age_group_id WHERE c.age_days IS NULL")
    print('  [تم] تعبئة عمر الفحوصات القديمة من بيانات المرضى: %d صف' % cur.rowcount)
    add_fk(t, 'fk_checks_age_group',
           "FOREIGN KEY (`age_group_id`) REFERENCES `age_groups` (`id`) ON DELETE SET NULL ON UPDATE CASCADE")


def step_contra():
    print('\n[7] موانع الاستعمال: تحويل حدود العمر من سنوات إلى أيام وفئات')
    t = 'drug_contraindications'
    adds = []
    for c in ('age_group_id', 'min_age_days', 'max_age_days'):
        if not col_exists(t, c):
            adds.append("ADD COLUMN `%s` int(11) DEFAULT NULL" % c)
    if not col_exists(t, 'age_group_id'):
        adds.append("ADD KEY `fk_contra_age_group` (`age_group_id`)")
    if adds:
        run('إضافة أعمدة العمر الجديدة', "ALTER TABLE `%s` %s" % (t, ', '.join(adds)))

    if col_exists(t, 'age_from') and col_exists(t, 'age_to'):
        groups = q("SELECT id, min_days, max_days FROM age_groups")
        n = 0
        for cid, lo, hi in q("SELECT id, age_from, age_to FROM drug_contraindications"):
            if lo is None and hi is None:
                continue
            mn = days_from_years(lo) if lo is not None else None
            mx = days_from_years(hi + 1) - 1 if hi is not None else None
            gid = None
            for g_id, g_min, g_max in groups:
                if (mn if mn is not None else 0) == g_min and mx == g_max:
                    gid = g_id
                    break
            cur.execute("UPDATE drug_contraindications SET min_age_days=%s, max_age_days=%s, age_group_id=%s WHERE id=%s",
                        (mn, mx, gid, cid))
            n += 1
        print('  [تم] تحويل حدود العمر في %d مانع استعمال' % n)

    add_fk(t, 'fk_contra_age_group',
           "FOREIGN KEY (`age_group_id`) REFERENCES `age_groups` (`id`) ON DELETE SET NULL ON UPDATE CASCADE")

    for c in ('age_from', 'age_to'):
        if col_exists(t, c):
            run('حذف العمود القديم %s' % c, "ALTER TABLE `%s` DROP COLUMN `%s`" % (t, c))
    if col_exists(t, 'min_age'):
        used = q("SELECT id, min_age FROM drug_contraindications WHERE min_age IS NOT NULL")
        if used:
            print('  [تنبيه] العمود min_age يحتوي قيماً في الصفوف التالية فلم أحذفه حفاظاً على بياناتك: %s'
                  % ', '.join('#%s=%s' % (i, v) for i, v in used))
        else:
            run('حذف العمود القديم min_age (فارغ تماماً)', "ALTER TABLE `%s` DROP COLUMN `min_age`" % t)


def step_triggers():
    print('\n[8] الـ triggers')
    for name, create in TRIGGERS:
        try:
            cur.execute("DROP TRIGGER IF EXISTS `%s`" % name)
            cur.execute(create)
            print('  [تم] %s' % name)
        except Exception as e:
            print('  [فشل] %s -> %s' % (name, e))
            print('        (قد تحتاج صلاحية إضافية؛ يمكن تجاهله مؤقتاً وإخباري بنص الخطأ)')


def verify(before):
    print('\n================ التحقق النهائي ================')
    ok = True
    for t, cols in sorted(EXPECTED.items()):
        if not table_exists(t):
            print('  ناقص: الجدول %s غير موجود' % t)
            ok = False
            continue
        have = [r[0] for r in q("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s", (t,))]
        miss = [c for c in cols if c not in have]
        extra = [c for c in have if c not in cols]
        if miss or extra:
            ok = False
            print('  %s: ناقص %s | زائد %s' % (t, miss or '-', extra or '-'))
    names = {r[0] for r in q("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE()")}
    missing_tr = [n for n, _ in TRIGGERS if n not in names]
    if missing_tr:
        ok = False
        print('  triggers ناقصة:', ', '.join(missing_tr))
    lost = False
    for t, n0 in before.items():
        if table_exists(t):
            n1 = q("SELECT COUNT(*) FROM `%s`" % t)[0][0]
            if n1 < n0:
                lost = True
                print('  !!! عدد صفوف %s نقص: كان %d وأصبح %d' % (t, n0, n1))
    print('\nعدد الصفوف الآن:')
    for t in sorted(EXPECTED):
        if table_exists(t):
            print('  %-28s %d' % (t, q("SELECT COUNT(*) FROM `%s`" % t)[0][0]))
    if ok and not lost:
        print('\nالنتيجة: بنية القاعدة صارت مطابقة للبنية الجديدة، ولم يضع أي صف.')
    else:
        print('\nالنتيجة: توجد ملاحظات أعلاه. انسخها وأرسلها لي (دون الرابط).')


def main():
    global conn, cur
    uri = input('الصق رابط القاعدة ثم اضغط Enter: ').strip()
    u = urlparse(uri)
    if not u.username or not u.hostname:
        raise SystemExit('الرابط ناقص. يجب أن يبدأ بـ mysql://')
    conn = pymysql.connect(host=u.hostname, port=u.port or 3306, user=unquote(u.username),
                           password=unquote(u.password or ''), database=u.path.lstrip('/'),
                           charset='utf8mb4', ssl={'fake_flag_to_enable_tls': True}, autocommit=True)
    cur = conn.cursor()
    print('تم الاتصال بالقاعدة:', u.path.lstrip('/'))

    for core in ('users', 'medications', 'patients', 'drug_interactions', 'interaction_checks'):
        if not table_exists(core):
            raise SystemExit('الجدول %s غير موجود. هذه لا تبدو قاعدة المشروع، فتوقفتُ دون تغيير.' % core)

    before = {}
    for (t,) in q("SHOW TABLES"):
        before[t] = q("SELECT COUNT(*) FROM `%s`" % t)[0][0]

    plan = []
    for t in ('age_groups', 'dosage_forms', 'interaction_age_groups', 'medication_dosing'):
        if not table_exists(t):
            plan.append('إنشاء الجدول الجديد %s' % t)
    if col_exists('medications', 'dosage_form'):
        plan.append('medications: تحويل dosage_form (نص) إلى dosage_form_id')
    if not col_exists('ckeck_medicines', 'dosage_form_id'):
        plan.append('ckeck_medicines: إضافة dosage_form_id')
    for t in ('patients', 'user_health_profiles'):
        if col_exists(t, 'age'):
            plan.append('%s: تحويل age إلى age_value + age_unit + age_days + age_group_id' % t)
    if not col_exists('interaction_checks', 'age_days'):
        plan.append('interaction_checks: إضافة age_days و age_group_id')
    if col_exists('drug_contraindications', 'age_from'):
        plan.append('drug_contraindications: تحويل age_from/age_to إلى min_age_days/max_age_days/age_group_id')
    plan.append('إنشاء/تحديث الـ triggers السبعة')

    print('\nما سيتم تنفيذه على القاعدة:')
    for p in plan:
        print('  - ' + p)
    print('\nتحذير: بعد الترحيل لن يعمل app.py القديم (يعتمد على الأعمدة القديمة)،')
    print('فيجب نشر نسخة app.py والقوالب المتوافقة مع البنية الجديدة.')
    if input('\nهل أخذتَ نسخة احتياطية وتريد المتابعة؟ اكتب YES: ').strip() != 'YES':
        raise SystemExit('أُلغي. لم يتغير شيء.')

    try:
        step_new_tables()
        step_medications()
        step_check_medicines()
        step_age_table(4, 'patients', 'fk_patients_age_group', True)
        step_age_table(5, 'user_health_profiles', 'fk_uhp_age_group', False)
        step_checks()
        step_contra()
        step_triggers()
    except Exception as e:
        print('\n!!! توقف الترحيل بسبب خطأ:', e)
        print('الخطوات السابقة تمت وهي آمنة. أرسل لي نص الخطأ (دون الرابط)، ثم يمكن إعادة تشغيل السكربت بأمان.')
        raise SystemExit(1)

    verify(before)
    conn.close()


if __name__ == '__main__':
    main()