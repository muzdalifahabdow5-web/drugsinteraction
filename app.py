import hashlib
import hmac
import json
import os
import random
import secrets
import smtplib
import ssl
import urllib.error
import urllib.request
import zlib
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps

from flask import (Flask, request, redirect, url_for, flash,
                   render_template, session, abort)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# ملاحظة: احتفظي بمفتاحك السري الخاص هنا، ولا تستخدمي هذا النص
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

_db_url = os.environ['DATABASE_URL']
_db_url = _db_url.replace('mysql://', 'mysql+pymysql://', 1).split('?')[0]
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
    'connect_args': {'ssl': {'fake_flag_to_enable_tls': True}},
}
db = SQLAlchemy(app)


# ============================================================
# النماذج (Models): تمثّل جداول قاعدة البيانات
# ============================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'pharmacist', 'user'), nullable=False, default='user')


class DrugClassification(db.Model):
    __tablename__ = 'drug_classification'
    id = db.Column(db.Integer, primary_key=True)
    name_arabic = db.Column(db.String(150), nullable=False)
    name_english = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)


class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    scientific_name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=False)
    dosage_form = db.Column(db.String(100))
    concentration = db.Column(db.String(100))
    dosage = db.Column(db.String(100))
    warning = db.Column(db.Text)
    classification_id = db.Column(db.Integer)


class HealthCondition(db.Model):
    __tablename__ = 'health_conditions'
    id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.String(150), nullable=False)
    condition_description = db.Column(db.Text)
    condition_category = db.Column(db.String(100))


class DrugInteraction(db.Model):
    __tablename__ = 'drug_interactions'
    interaction_id = db.Column(db.Integer, primary_key=True)
    drug_1_id = db.Column(db.Integer, nullable=False)
    drug_2_id = db.Column(db.Integer, nullable=False)
    severity = db.Column(db.Enum('minor', 'moderate', 'major'), nullable=False)
    description = db.Column(db.Text, nullable=False)


class DrugContraindication(db.Model):
    __tablename__ = 'drug_contraindications'
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, nullable=False)
    condition_id = db.Column(db.Integer)
    pregnancy_risk = db.Column(db.Boolean, nullable=False, default=False)
    age_from = db.Column(db.Integer)
    age_to = db.Column(db.Integer)
    severity = db.Column(db.Enum('minor', 'moderate', 'major'), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    age = db.Column(db.Integer, nullable=False)
    is_pregnant = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(20))
    user_id = db.Column(db.Integer)


class InteractionCheck(db.Model):
    __tablename__ = 'interaction_checks'
    check_id = db.Column(db.Integer, primary_key=True)
    check_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer)
    patient_id = db.Column(db.Integer)


class CheckMedicine(db.Model):
    __tablename__ = 'ckeck_medicines'
    ckeck_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, primary_key=True)


class InteractionCondition(db.Model):
    __tablename__ = 'interaction_conditions'
    condition_id = db.Column(db.Integer, primary_key=True)
    interaction_check_id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.Text)


class UserHealthProfile(db.Model):
    __tablename__ = 'user_health_profiles'
    user_id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    is_pregnant = db.Column(db.Boolean, default=False)


class UserChronicCondition(db.Model):
    __tablename__ = 'user_chronic_conditions'
    user_id = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, primary_key=True)


class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.Enum('A', 'B', 'C', 'D'), nullable=False)
    difficulty = db.Column(db.String(50), default='Medium')
    source_key = db.Column(db.String(100))  # مفتاح الأسئلة المولَّدة تلقائيًا من التداخلات


class Player(db.Model):
    __tablename__ = 'players'
    player_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150))
    total_score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer)


class PlayerAttempt(db.Model):
    __tablename__ = 'player_attempts'
    attempt_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    selected_option = db.Column(db.Enum('A', 'B', 'C', 'D'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)


class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    used = db.Column(db.Boolean, nullable=False, default=False)


# ============================================================
# الحارس: يحمي المسارات حسب الدور
# ============================================================

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('يجب تسجيل الدخول أولًا')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# محرك الاستدلال (Inference Engine)
# ============================================================

SEVERITY_RANK = {'minor': 1, 'moderate': 2, 'major': 3}

LEVELS = {
    'danger': {
        'title': 'خطر',
        'message': 'لا يُنصح بهذه التركيبة. راجع الصيدلاني أو الطبيب قبل الاستخدام.',
    },
    'caution': {
        'title': 'يحتاج إلى استشارة',
        'message': 'يُنصح باستشارة الصيدلاني أو الطبيب قبل الاستخدام.',
    },
    'safe': {
        'title': 'آمن',
        'message': 'لم تجد قاعدة المعرفة تداخلًا أو مانع استعمال لهذه المدخلات.',
    },
}


def med_label(med):
    return f'{med["scientific_name"]} ({med["trade_name"]})'


def evaluate(meds, interactions, contras, age, pregnant, cond_names):
    """
    القلب المنطقي للمحرك. لا يتصل بقاعدة البيانات، فيسهل اختباره.
    meds: {id: {'scientific_name':..., 'trade_name':...}}
    interactions: قائمة قواميس (drug_1_id, drug_2_id, severity, description)
    contras: قائمة قواميس (medication_id, condition_id, pregnancy_risk,
             age_from, age_to, severity, description)
    cond_names: {condition_id: اسم المرض} للأمراض التي اختارها المستخدم فقط
    """
    findings = []

    # 1) التداخلات بين الأدوية
    for it in interactions:
        a, b = meds.get(it['drug_1_id']), meds.get(it['drug_2_id'])
        if not a or not b:
            continue
        findings.append({
            'kind': 'interaction',
            'severity': it['severity'],
            'title': f'{med_label(a)} + {med_label(b)}',
            'text': it['description'],
        })

    # 2) موانع الاستعمال: مرض، أو حمل، أو عمر داخل نطاق (من... إلى...)
    for c in contras:
        med = meds.get(c['medication_id'])
        if not med:
            continue
        reasons = []
        if c['condition_id'] is not None and c['condition_id'] in cond_names:
            reasons.append(cond_names[c['condition_id']])
        if c['pregnancy_risk'] and pregnant:
            reasons.append('الحمل')
        lo, hi = c.get('age_from'), c.get('age_to')
        if age is not None and (lo is not None or hi is not None):
            if (lo is None or age >= lo) and (hi is None or age <= hi):
                if lo is not None and hi is not None:
                    reasons.append(f'العمر بين {lo} و{hi} سنة')
                elif lo is not None:
                    reasons.append(f'العمر {lo} سنة فأكثر')
                else:
                    reasons.append(f'العمر {hi} سنة فأقل')
        if reasons:
            findings.append({
                'kind': 'contra',
                'severity': c['severity'],
                'title': f'{med_label(med)}: ' + ' و'.join(reasons),
                'text': c['description'],
            })

    # الأخطر أولًا
    findings.sort(key=lambda f: SEVERITY_RANK[f['severity']], reverse=True)

    # القرار النهائي بحسب أشد مستوى
    top = SEVERITY_RANK[findings[0]['severity']] if findings else 0
    level = 'danger' if top == 3 else 'caution' if top == 2 else 'safe'

    return {
        'level': level,
        'level_title': LEVELS[level]['title'],
        'message': LEVELS[level]['message'],
        'findings': findings,
    }


def analyze(meds, age, pregnant, cond_ids):
    """يحلل أدوية معروفة (قاموس id → بيانات) مقابل قاعدة المعرفة."""
    ids = list(meds)
    interactions, contras = [], []
    if ids:
        interactions = [
            {'drug_1_id': i.drug_1_id, 'drug_2_id': i.drug_2_id,
             'severity': i.severity, 'description': i.description}
            for i in DrugInteraction.query.filter(
                DrugInteraction.drug_1_id.in_(ids),
                DrugInteraction.drug_2_id.in_(ids)).all()
        ]
        contras = [
            {'medication_id': c.medication_id, 'condition_id': c.condition_id,
             'pregnancy_risk': bool(c.pregnancy_risk),
             'age_from': c.age_from, 'age_to': c.age_to,
             'severity': c.severity, 'description': c.description}
            for c in DrugContraindication.query.filter(
                DrugContraindication.medication_id.in_(ids)).all()
        ]

    cond_names = {}
    if cond_ids:
        cond_names = {c.id: c.condition_name for c in
                      HealthCondition.query.filter(HealthCondition.id.in_(cond_ids)).all()}

    result = evaluate(meds, interactions, contras, age, pregnant, cond_names)
    result['meds'] = [med_label(m) for m in meds.values()]
    result['dosages'] = [{'name': med_label(m), 'dosage': m['dosage']}
                         for m in meds.values() if m.get('dosage')]
    result['med_ids'] = ids
    result['saved'] = False
    return result


def run_check(names, age, pregnant, cond_ids):
    """يقرأ قاعدة المعرفة ثم يستدعي evaluate."""
    meds, not_found = {}, []
    for name in names:
        key = name.strip().lower()
        if not key:
            continue
        m = Medication.query.filter(
            (db.func.lower(Medication.scientific_name) == key) |
            (db.func.lower(Medication.trade_name) == key)
        ).first()
        if m:
            meds[m.id] = {'scientific_name': m.scientific_name,
                          'trade_name': m.trade_name,
                          'dosage': m.dosage}
        else:
            not_found.append(name.strip())

    result = analyze(meds, age, pregnant, cond_ids)
    result['not_found'] = not_found
    return result


def save_check(user_id, med_ids, age, pregnant, cond_ids, patient_name=None, gender=None):
    """يحفظ الفحص في سجل المستخدم المسجّل فقط."""
    patient_id = None
    if age is not None:
        patient = Patient(name=patient_name, gender=gender, age=age,
                          is_pregnant=bool(pregnant), user_id=user_id)
        db.session.add(patient)
        db.session.flush()
        patient_id = patient.patient_id

    check = InteractionCheck(check_date=datetime.now(),
                             user_id=user_id, patient_id=patient_id)
    db.session.add(check)
    db.session.flush()

    for mid in med_ids:
        db.session.add(CheckMedicine(ckeck_id=check.check_id, drug_id=mid))
    for cid in cond_ids:
        db.session.add(InteractionCondition(condition_id=cid,
                                            interaction_check_id=check.check_id))
    db.session.commit()


# ============================================================
# المسارات
# ============================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    """صفحة فحص التداخل: مفتوحة للجميع."""
    conditions = HealthCondition.query.order_by(HealthCondition.condition_name).all()
    known = []
    for m in Medication.query.order_by(Medication.scientific_name).all():
        known += [m.scientific_name, m.trade_name]

    form = {'drugs': [], 'age': None, 'pregnant': False, 'conditions': [],
            'patient_name': '', 'gender': ''}
    result, error = None, None
    is_pharmacist = session.get('role') == 'pharmacist'

    if request.method == 'GET' and session.get('role') == 'user':
        prof = UserHealthProfile.query.get(session['user_id'])
        if prof:
            form['age'] = prof.age
            form['pregnant'] = bool(prof.is_pregnant)
        form['conditions'] = [r[0] for r in db.session.query(UserChronicCondition.condition_id)
                              .filter_by(user_id=session['user_id']).all()]

    if request.method == 'POST':
        names = [n for n in request.form.get('drugs', '').split('|') if n.strip()][:10]
        age_raw = request.form.get('age', '')
        age = int(age_raw) if age_raw.isdigit() and 0 < int(age_raw) < 121 else None
        pregnant = 'pregnant' in request.form
        valid_ids = {c.id for c in conditions}
        cond_ids = [int(x) for x in request.form.getlist('conditions')
                    if x.isdigit() and int(x) in valid_ids]

        patient_name, gender = None, None
        if is_pharmacist:
            patient_name = request.form.get('patient_name', '').strip()[:150] or None
            gender = request.form.get('gender', '')
            gender = gender if gender in ('ذكر', 'أنثى') else None

        form = {'drugs': names, 'age': age, 'pregnant': pregnant, 'conditions': cond_ids,
                'patient_name': patient_name or '', 'gender': gender or ''}

        if not names:
            error = 'أدخل اسم دواء واحد على الأقل.'
        elif is_pharmacist and patient_name and age is None:
            error = 'عمر المريض مطلوب عند إدخال اسمه.'
        else:
            result = run_check(names, age, pregnant, cond_ids)
            if not result['med_ids']:
                error = 'لم نجد أيًّا من الأدوية المدخلة في قاعدة المعرفة.'
                result = None
            elif 'user_id' in session:
                save_check(session['user_id'], result['med_ids'], age, pregnant, cond_ids,
                           patient_name, gender)
                result['saved'] = True

    return render_template('index.html', conditions=conditions, known=sorted(set(known)),
                           form=form, result=result, error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('جميع الحقول مطلوبة')
            return redirect(url_for('register'))
        if len(password) < 8:
            flash('كلمة المرور يجب أن تكون 8 رموز على الأقل')
            return redirect(url_for('register'))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('اسم المستخدم أو البريد مستخدم من قبل')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

        # ندخل المستخدم الجديد مباشرة إلى حسابه
        session.clear()
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))

        flash('البريد أو كلمة المرور غير صحيحة')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@role_required('admin', 'pharmacist', 'user')
def dashboard():
    role = session['role']
    if role == 'admin':
        return redirect(url_for('admin_home'))
    if role == 'pharmacist':
        return redirect(url_for('pharmacist_home'))
    return redirect(url_for('user_home'))


# ============================================================
# لوحة الأدمن
# ============================================================

@app.route('/admin')
@role_required('admin')
def admin_home():
    counts = {
        'medications': Medication.query.count(),
        'users': User.query.count(),
        'interactions': DrugInteraction.query.count(),
    }
    return render_template('admin/home.html', counts=counts)


def read_medication_form():
    """يقرأ حقول نموذج الدواء ويعيد (البيانات، رسالة الخطأ)."""
    scientific_name = request.form.get('scientific_name', '').strip()
    trade_name = request.form.get('trade_name', '').strip()
    class_raw = request.form.get('classification_id', '')
    data = {
        'scientific_name': scientific_name,
        'trade_name': trade_name,
        'dosage_form': request.form.get('dosage_form', '').strip() or None,
        'concentration': request.form.get('concentration', '').strip() or None,
        'dosage': request.form.get('dosage', '').strip()[:100] or None,
        'warning': request.form.get('warning', '').strip() or None,
        'classification_id': int(class_raw) if class_raw.isdigit() else None,
    }
    if not scientific_name or not trade_name:
        return data, 'الاسم العلمي والاسم التجاري مطلوبان'
    return data, None


@app.route('/admin/medications', methods=['GET', 'POST'])
@role_required('admin')
def admin_medications():
    if request.method == 'POST':
        data, error = read_medication_form()
        if error:
            flash(error)
        else:
            db.session.add(Medication(**data))
            db.session.commit()
            flash(f'أُضيف الدواء "{data["scientific_name"]}" بنجاح')
            return redirect(url_for('admin_medications'))

    classifications = DrugClassification.query.order_by(DrugClassification.name_arabic).all()
    class_names = {c.id: c.name_arabic for c in classifications}
    meds = Medication.query.order_by(Medication.id.desc()).all()
    return render_template('admin/medications.html', meds=meds,
                           classifications=classifications, class_names=class_names)


@app.route('/admin/medications/<int:med_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    if request.method == 'POST':
        data, error = read_medication_form()
        if error:
            flash(error)
        else:
            for key, value in data.items():
                setattr(med, key, value)
            db.session.commit()
            flash(f'تم تعديل الدواء "{med.scientific_name}"')
            return redirect(url_for('admin_medications'))

    classifications = DrugClassification.query.order_by(DrugClassification.name_arabic).all()
    return render_template('admin/medication_edit.html', med=med, classifications=classifications)


@app.route('/admin/medications/<int:med_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    name = med.scientific_name

    # لا نحذف دواءً مستخدمًا في تداخل أو مانع استعمال أو سجل فحص
    used_in_interaction = DrugInteraction.query.filter(
        (DrugInteraction.drug_1_id == med_id) | (DrugInteraction.drug_2_id == med_id)).count()
    used_in_contra = DrugContraindication.query.filter_by(medication_id=med_id).count()
    used_in_checks = CheckMedicine.query.filter_by(drug_id=med_id).count()

    if used_in_interaction or used_in_contra or used_in_checks:
        parts = []
        if used_in_interaction:
            parts.append(f'{used_in_interaction} تداخل')
        if used_in_contra:
            parts.append(f'{used_in_contra} مانع استعمال')
        if used_in_checks:
            parts.append(f'{used_in_checks} سجل فحص')
        flash(f'لا يمكن حذف "{name}" لأنه مستخدم في: ' + '، '.join(parts))
        return redirect(url_for('admin_medications'))

    try:
        db.session.delete(med)
        db.session.commit()
        flash(f'حُذف الدواء "{name}"')
    except IntegrityError:
        db.session.rollback()
        flash(f'لا يمكن حذف "{name}" لأنه مرتبط ببيانات أخرى في القاعدة')
    return redirect(url_for('admin_medications'))


# ---------- إدارة التداخلات ----------

SEVERITY_AR = {'minor': 'بسيط', 'moderate': 'متوسط', 'major': 'خطير'}


def read_interaction_form(exclude_id=None):
    """يقرأ نموذج التداخل ويتحقق منه. يعيد (البيانات، رسالة الخطأ)."""
    d1 = request.form.get('drug_1_id', '')
    d2 = request.form.get('drug_2_id', '')
    severity = request.form.get('severity', '')
    description = request.form.get('description', '').strip()
    data = {
        'drug_1_id': int(d1) if d1.isdigit() else None,
        'drug_2_id': int(d2) if d2.isdigit() else None,
        'severity': severity,
        'description': description,
    }

    if data['drug_1_id'] is None or data['drug_2_id'] is None:
        return data, 'اختر الدواءين'
    if data['drug_1_id'] == data['drug_2_id']:
        return data, 'يجب أن يكون الدواءان مختلفين'
    if not (Medication.query.get(data['drug_1_id']) and Medication.query.get(data['drug_2_id'])):
        return data, 'أحد الدواءين غير موجود'
    if severity not in SEVERITY_AR:
        return data, 'درجة الخطورة غير صالحة'
    if not description:
        return data, 'وصف التداخل مطلوب'

    # منع تكرار الزوج نفسه بأي ترتيب
    q = DrugInteraction.query.filter(
        ((DrugInteraction.drug_1_id == data['drug_1_id']) & (DrugInteraction.drug_2_id == data['drug_2_id'])) |
        ((DrugInteraction.drug_1_id == data['drug_2_id']) & (DrugInteraction.drug_2_id == data['drug_1_id'])))
    if exclude_id is not None:
        q = q.filter(DrugInteraction.interaction_id != exclude_id)
    if q.first():
        return data, 'هذا التداخل مسجّل من قبل لنفس الدواءين'
    return data, None


@app.route('/admin/interactions', methods=['GET', 'POST'])
@role_required('admin')
def admin_interactions():
    if request.method == 'POST':
        data, error = read_interaction_form()
        if error:
            flash(error)
        else:
            try:
                db.session.add(DrugInteraction(**data))
                db.session.commit()
                flash('أُضيف التداخل بنجاح')
                return redirect(url_for('admin_interactions'))
            except Exception:
                db.session.rollback()
                flash('تعذّرت إضافة التداخل، تأكد من البيانات')

    meds = Medication.query.order_by(Medication.scientific_name).all()
    names = {m.id: f'{m.scientific_name} ({m.trade_name})' for m in meds}
    interactions = DrugInteraction.query.order_by(DrugInteraction.interaction_id.desc()).all()
    return render_template('admin/interactions.html', meds=meds, names=names,
                           interactions=interactions, severity_ar=SEVERITY_AR)


@app.route('/admin/interactions/<int:inter_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_interaction(inter_id):
    inter = DrugInteraction.query.get_or_404(inter_id)
    if request.method == 'POST':
        data, error = read_interaction_form(exclude_id=inter_id)
        if error:
            flash(error)
        else:
            try:
                for key, value in data.items():
                    setattr(inter, key, value)
                db.session.commit()
                flash('تم تعديل التداخل')
                return redirect(url_for('admin_interactions'))
            except Exception:
                db.session.rollback()
                flash('تعذّر تعديل التداخل، تأكد من البيانات')

    meds = Medication.query.order_by(Medication.scientific_name).all()
    return render_template('admin/interaction_edit.html', inter=inter, meds=meds,
                           severity_ar=SEVERITY_AR)


@app.route('/admin/interactions/<int:inter_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_interaction(inter_id):
    inter = DrugInteraction.query.get_or_404(inter_id)
    try:
        db.session.delete(inter)
        db.session.commit()
        flash('حُذف التداخل')
    except IntegrityError:
        db.session.rollback()
        flash('لا يمكن حذف هذا التداخل لأنه مرتبط ببيانات أخرى')
    return redirect(url_for('admin_interactions'))


# ---------- إدارة موانع الاستعمال ----------

def read_contra_form(exclude_id=None):
    """يقرأ نموذج مانع الاستعمال ويتحقق منه. يعيد (البيانات، رسالة الخطأ)."""
    med_raw = request.form.get('medication_id', '')
    cond_raw = request.form.get('condition_id', '')
    from_raw = request.form.get('age_from', '').strip()
    to_raw = request.form.get('age_to', '').strip()
    severity = request.form.get('severity', '')
    description = request.form.get('description', '').strip()

    data = {
        'medication_id': int(med_raw) if med_raw.isdigit() else None,
        'condition_id': int(cond_raw) if cond_raw.isdigit() else None,
        'pregnancy_risk': 'pregnancy_risk' in request.form,
        'age_from': int(from_raw) if from_raw.isdigit() else None,
        'age_to': int(to_raw) if to_raw.isdigit() else None,
        'severity': severity,
        'description': description,
    }

    if data['medication_id'] is None or not Medication.query.get(data['medication_id']):
        return data, 'اختر دواءً صالحًا'
    if data['condition_id'] is not None and not HealthCondition.query.get(data['condition_id']):
        return data, 'المرض المختار غير موجود'
    for raw, key in ((from_raw, 'age_from'), (to_raw, 'age_to')):
        if raw and (data[key] is None or not (0 <= data[key] <= 120)):
            return data, 'حدود العمر يجب أن تكون أرقامًا بين 0 و120'
    if data['age_from'] is not None and data['age_to'] is not None and data['age_from'] > data['age_to']:
        return data, 'بداية نطاق العمر يجب ألا تتجاوز نهايته'
    has_age = data['age_from'] is not None or data['age_to'] is not None
    if data['condition_id'] is None and not data['pregnancy_risk'] and not has_age:
        return data, 'حدّد سببًا واحدًا على الأقل: مرض، أو حمل، أو نطاق عمر'
    if severity not in SEVERITY_AR:
        return data, 'درجة الخطورة غير صالحة'
    if not description:
        return data, 'الوصف مطلوب'

    q = DrugContraindication.query.filter_by(
        medication_id=data['medication_id'], condition_id=data['condition_id'],
        pregnancy_risk=data['pregnancy_risk'],
        age_from=data['age_from'], age_to=data['age_to'])
    if exclude_id is not None:
        q = q.filter(DrugContraindication.id != exclude_id)
    if q.first():
        return data, 'مانع الاستعمال هذا مسجّل من قبل'
    return data, None


@app.route('/admin/contraindications', methods=['GET', 'POST'])
@role_required('admin')
def admin_contraindications():
    if request.method == 'POST':
        data, error = read_contra_form()
        if error:
            flash(error)
        else:
            try:
                db.session.add(DrugContraindication(**data))
                db.session.commit()
                flash('أُضيف مانع الاستعمال بنجاح')
                return redirect(url_for('admin_contraindications'))
            except Exception:
                db.session.rollback()
                flash('تعذّرت الإضافة، تأكد من البيانات')

    meds = Medication.query.order_by(Medication.scientific_name).all()
    conditions = HealthCondition.query.order_by(HealthCondition.condition_name).all()
    med_names = {m.id: f'{m.scientific_name} ({m.trade_name})' for m in meds}
    cond_names = {c.id: c.condition_name for c in conditions}
    contras = DrugContraindication.query.order_by(DrugContraindication.id.desc()).all()
    return render_template('admin/contraindications.html', meds=meds, conditions=conditions,
                           med_names=med_names, cond_names=cond_names,
                           contras=contras, severity_ar=SEVERITY_AR)


@app.route('/admin/contraindications/<int:contra_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_contraindication(contra_id):
    contra = DrugContraindication.query.get_or_404(contra_id)
    if request.method == 'POST':
        data, error = read_contra_form(exclude_id=contra_id)
        if error:
            flash(error)
        else:
            try:
                for key, value in data.items():
                    setattr(contra, key, value)
                db.session.commit()
                flash('تم تعديل مانع الاستعمال')
                return redirect(url_for('admin_contraindications'))
            except Exception:
                db.session.rollback()
                flash('تعذّر التعديل، تأكد من البيانات')

    meds = Medication.query.order_by(Medication.scientific_name).all()
    conditions = HealthCondition.query.order_by(HealthCondition.condition_name).all()
    return render_template('admin/contraindication_edit.html', contra=contra, meds=meds,
                           conditions=conditions, severity_ar=SEVERITY_AR)


@app.route('/admin/contraindications/<int:contra_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_contraindication(contra_id):
    contra = DrugContraindication.query.get_or_404(contra_id)
    try:
        db.session.delete(contra)
        db.session.commit()
        flash('حُذف مانع الاستعمال')
    except IntegrityError:
        db.session.rollback()
        flash('لا يمكن حذفه لأنه مرتبط ببيانات أخرى')
    return redirect(url_for('admin_contraindications'))


# ---------- إدارة الأمراض ----------

def read_condition_form(exclude_id=None):
    """يقرأ نموذج المرض ويتحقق منه. يعيد (البيانات، رسالة الخطأ)."""
    name = request.form.get('condition_name', '').strip()
    data = {
        'condition_name': name,
        'condition_description': request.form.get('condition_description', '').strip() or None,
        'condition_category': request.form.get('condition_category', '').strip() or None,
    }
    if not name:
        return data, 'اسم المرض مطلوب'
    q = HealthCondition.query.filter(db.func.lower(HealthCondition.condition_name) == name.lower())
    if exclude_id is not None:
        q = q.filter(HealthCondition.id != exclude_id)
    if q.first():
        return data, 'هذا المرض مسجّل من قبل'
    return data, None


@app.route('/admin/conditions', methods=['GET', 'POST'])
@role_required('admin')
def admin_conditions():
    if request.method == 'POST':
        data, error = read_condition_form()
        if error:
            flash(error)
        else:
            try:
                db.session.add(HealthCondition(**data))
                db.session.commit()
                flash(f'أُضيف المرض "{data["condition_name"]}" بنجاح')
                return redirect(url_for('admin_conditions'))
            except Exception:
                db.session.rollback()
                flash('تعذّرت الإضافة، تأكد من البيانات')

    conditions = HealthCondition.query.order_by(HealthCondition.id.desc()).all()
    return render_template('admin/conditions.html', conditions=conditions)


@app.route('/admin/conditions/<int:cond_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_condition(cond_id):
    cond = HealthCondition.query.get_or_404(cond_id)
    if request.method == 'POST':
        data, error = read_condition_form(exclude_id=cond_id)
        if error:
            flash(error)
        else:
            try:
                for key, value in data.items():
                    setattr(cond, key, value)
                db.session.commit()
                flash(f'تم تعديل المرض "{cond.condition_name}"')
                return redirect(url_for('admin_conditions'))
            except Exception:
                db.session.rollback()
                flash('تعذّر التعديل، تأكد من البيانات')

    return render_template('admin/condition_edit.html', cond=cond)


@app.route('/admin/conditions/<int:cond_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_condition(cond_id):
    cond = HealthCondition.query.get_or_404(cond_id)
    name = cond.condition_name

    # لا نحذف مرضًا مستخدمًا في مانع استعمال أو سجل فحص
    used_in_contra = DrugContraindication.query.filter_by(condition_id=cond_id).count()
    used_in_checks = InteractionCondition.query.filter_by(condition_id=cond_id).count()
    used_in_profiles = UserChronicCondition.query.filter_by(condition_id=cond_id).count()
    if used_in_contra or used_in_checks or used_in_profiles:
        parts = []
        if used_in_contra:
            parts.append(f'{used_in_contra} مانع استعمال')
        if used_in_checks:
            parts.append(f'{used_in_checks} سجل فحص')
        if used_in_profiles:
            parts.append(f'{used_in_profiles} ملف صحي')
        flash(f'لا يمكن حذف "{name}" لأنه مستخدم في: ' + '، '.join(parts))
        return redirect(url_for('admin_conditions'))

    try:
        db.session.delete(cond)
        db.session.commit()
        flash(f'حُذف المرض "{name}"')
    except IntegrityError:
        db.session.rollback()
        flash(f'لا يمكن حذف "{name}" لأنه مرتبط ببيانات أخرى في القاعدة')
    return redirect(url_for('admin_conditions'))


@app.route('/admin/users', methods=['GET', 'POST'])
@role_required('admin')
def admin_users():
    temp_password = None
    new_username = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '')

        if role not in ('admin', 'pharmacist', 'user'):
            flash('الدور غير صالح')
        elif not username or not email:
            flash('اسم المستخدم والبريد مطلوبان')
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash('اسم المستخدم أو البريد مستخدم من قبل')
        else:
            temp_password = secrets.token_urlsafe(9)  # كلمة مرور مؤقتة عشوائية
            db.session.add(User(
                username=username,
                email=email,
                password=generate_password_hash(temp_password),
                role=role,
            ))
            db.session.commit()
            new_username = username
            flash(f'أُضيف المستخدم "{username}"')

    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users, me=session['user_id'],
                           temp_password=temp_password, new_username=new_username)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user_id == session.get('user_id'):
        flash('لا يمكنك حذف حسابك الذي تدخل به')
        return redirect(url_for('admin_users'))
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        flash('لا يمكن حذف آخر أدمن في النظام')
        return redirect(url_for('admin_users'))

    name = user.username
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'حُذف المستخدم "{name}"')
    except IntegrityError:
        db.session.rollback()
        flash(f'لا يمكن حذف "{name}" لأنه مرتبط ببيانات أخرى في القاعدة')
    return redirect(url_for('admin_users'))


@app.route('/account/password', methods=['GET', 'POST'])
@role_required('admin', 'pharmacist', 'user')
def change_password():
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        user = User.query.get(session['user_id'])

        if not user or not check_password_hash(user.password, current):
            flash('كلمة المرور الحالية غير صحيحة')
        elif len(new) < 8:
            flash('كلمة المرور الجديدة يجب أن تكون 8 رموز على الأقل')
        elif new != confirm:
            flash('كلمة المرور الجديدة وتأكيدها غير متطابقين')
        else:
            user.password = generate_password_hash(new)
            db.session.commit()
            flash('تم تغيير كلمة المرور بنجاح')
            return redirect(url_for('dashboard'))

    return render_template('account/password.html')


def account_home():
    user = User.query.get(session['user_id'])
    return render_template('account/home.html', user=user)


@app.route('/pharmacist')
@role_required('pharmacist')
def pharmacist_home():
    return account_home()


@app.route('/user')
@role_required('user')
def user_home():
    return account_home()


# ---------- الملف الصحي ----------

@app.route('/account/profile', methods=['GET', 'POST'])
@role_required('user')
def health_profile():
    uid = session['user_id']
    conditions = HealthCondition.query.order_by(HealthCondition.condition_name).all()
    valid_ids = {c.id for c in conditions}
    prof = UserHealthProfile.query.get(uid)
    chosen = {r[0] for r in db.session.query(UserChronicCondition.condition_id)
              .filter_by(user_id=uid).all()}

    if request.method == 'POST':
        age_raw = request.form.get('age', '').strip()
        age = int(age_raw) if age_raw.isdigit() else None
        new_ids = {int(x) for x in request.form.getlist('conditions')
                   if x.isdigit() and int(x) in valid_ids}

        if age_raw and (age is None or not (1 <= age <= 120)):
            flash('العمر يجب أن يكون بين 1 و120')
        else:
            try:
                if prof is None:
                    prof = UserHealthProfile(user_id=uid)
                    db.session.add(prof)
                prof.age = age
                prof.is_pregnant = 'pregnant' in request.form

                removed = chosen - new_ids
                if removed:
                    UserChronicCondition.query.filter(
                        UserChronicCondition.user_id == uid,
                        UserChronicCondition.condition_id.in_(removed)
                    ).delete(synchronize_session=False)
                for cid in new_ids - chosen:
                    db.session.add(UserChronicCondition(user_id=uid, condition_id=cid))

                db.session.commit()
                flash('تم حفظ ملفك الصحي')
                return redirect(url_for('health_profile'))
            except Exception:
                db.session.rollback()
                flash('تعذّر حفظ الملف الصحي، حاول مرة أخرى')
            chosen = new_ids

    return render_template('account/profile.html', prof=prof, conditions=conditions, chosen=chosen)


# ---------- سجل الفحوصات ----------

def rebuild_check(check):
    """يعيد تحليل فحص محفوظ بالمعرفة الحالية في القاعدة."""
    med_ids = [r.drug_id for r in CheckMedicine.query.filter_by(ckeck_id=check.check_id).all()]
    meds = {}
    if med_ids:
        for m in Medication.query.filter(Medication.id.in_(med_ids)).all():
            meds[m.id] = {'scientific_name': m.scientific_name, 'trade_name': m.trade_name,
                          'dosage': m.dosage}

    patient = Patient.query.get(check.patient_id) if check.patient_id else None
    age = patient.age if patient else None
    pregnant = bool(patient.is_pregnant) if patient else False
    cond_ids = [r[0] for r in db.session.query(InteractionCondition.condition_id)
                .filter_by(interaction_check_id=check.check_id).all()]

    result = analyze(meds, age, pregnant, cond_ids)
    result['age'] = age
    result['pregnant'] = pregnant
    result['patient_name'] = patient.name if patient else None
    result['gender'] = patient.gender if patient else None
    result['condition_names'] = [c.condition_name for c in
                                 HealthCondition.query.filter(HealthCondition.id.in_(cond_ids)).all()] if cond_ids else []
    return result


@app.route('/account/history')
@role_required('admin', 'pharmacist', 'user')
def check_history():
    q = request.args.get('q', '').strip()
    query = InteractionCheck.query.filter_by(user_id=session['user_id'])
    if q:
        query = query.join(Patient, InteractionCheck.patient_id == Patient.patient_id).filter(
            Patient.name.contains(q, autoescape=True))
    checks = (query.order_by(InteractionCheck.check_date.desc(), InteractionCheck.check_id.desc())
              .limit(50).all())
    rows = [{'check': c, 'result': rebuild_check(c)} for c in checks]
    return render_template('account/history.html', rows=rows, q=q)


@app.route('/account/history/<int:check_id>')
@role_required('admin', 'pharmacist', 'user')
def check_detail(check_id):
    check = InteractionCheck.query.filter_by(
        check_id=check_id, user_id=session['user_id']).first_or_404()
    return render_template('account/history_detail.html', check=check, result=rebuild_check(check))


# ============================================================
# لعبة «تحدي الصيدلاني الخبير» (للصيدلاني فقط)
# ============================================================

ROUND_SIZE = 10
POINTS_PER_CORRECT = 10
LETTERS = 'ABCD'
SEVERITY_ORDER = ['minor', 'moderate', 'major']
SEVERITY_CHOICES = ['بسيط', 'متوسط', 'خطير']


def build_auto_questions(meds, interactions):
    """
    يولّد الأسئلة من جدول التداخلات. لا يتصل بقاعدة البيانات، فيسهل اختباره.
    meds: {id: الاسم العلمي}
    interactions: قائمة قواميس (id, drug_1_id, drug_2_id, severity)
    التوليد حتمي: نفس المدخلات تعطي نفس الأسئلة والخيارات دائمًا.
    """
    partners = {}
    for it in interactions:
        partners.setdefault(it['drug_1_id'], set()).add(it['drug_2_id'])
        partners.setdefault(it['drug_2_id'], set()).add(it['drug_1_id'])

    questions = []
    for it in interactions:
        a, b = it['drug_1_id'], it['drug_2_id']
        if a not in meds or b not in meds or it['severity'] not in SEVERITY_ORDER:
            continue

        # النوع 1: ما درجة خطورة التداخل؟
        questions.append({
            'key': f"i{it['id']}:sev",
            'text': f'ما درجة خطورة التداخل الدوائي بين {meds[a]} و{meds[b]}؟',
            'options': list(SEVERITY_CHOICES),
            'correct': SEVERITY_ORDER.index(it['severity']),
            'difficulty': 'Medium',
        })

        # النوع 2: أي دواء يتداخل مع الدواء المذكور؟ (باتجاهين)
        for tag, target, partner in (('t1', a, b), ('t2', b, a)):
            candidates = sorted(set(meds) - {target} - partners.get(target, set()))
            if len(candidates) < 2:
                continue
            key = f"i{it['id']}:{tag}"
            rnd = random.Random(zlib.crc32(key.encode('utf-8')))
            ids = [partner] + rnd.sample(candidates, min(3, len(candidates)))
            rnd.shuffle(ids)
            questions.append({
                'key': key,
                'text': f'أي من الأدوية التالية له تداخل مسجّل مع {meds[target]}؟',
                'options': [meds[i] for i in ids],
                'correct': ids.index(partner),
                'difficulty': 'Hard',
            })
    return questions


def sync_questions():
    """يزامن الأسئلة المولَّدة مع جدول questions. ينفَّذ عند بدء كل جولة."""
    meds = {m.id: m.scientific_name for m in Medication.query.all()}
    interactions = [{'id': i.interaction_id, 'drug_1_id': i.drug_1_id,
                     'drug_2_id': i.drug_2_id, 'severity': i.severity}
                    for i in DrugInteraction.query.all()]
    built = build_auto_questions(meds, interactions)

    existing = {q.source_key: q for q in
                Question.query.filter(Question.source_key.isnot(None)).all()}
    for b in built:
        opts = b['options'] + [None] * (4 - len(b['options']))
        q = existing.get(b['key'])
        if q is None:
            q = Question(source_key=b['key'])
            db.session.add(q)
        q.question_text = b['text']
        q.option_a, q.option_b, q.option_c, q.option_d = opts
        q.correct_option = LETTERS[b['correct']]
        q.difficulty = b['difficulty']
    db.session.commit()
    return [b['key'] for b in built]


def build_round():
    """يختار أسئلة الجولة من المولَّدة حاليًا ومن الأسئلة اليدوية."""
    keys = sync_questions()
    pool = []
    if keys:
        pool += [q.question_id for q in Question.query.filter(Question.source_key.in_(keys)).all()]
    pool += [q.question_id for q in Question.query.filter(Question.source_key.is_(None)).all()]
    random.shuffle(pool)
    return pool[:ROUND_SIZE]


def get_player():
    uid = session['user_id']
    player = Player.query.filter_by(user_id=uid).first()
    if player is None:
        user = User.query.get(uid)
        player = Player(username=user.username, email=user.email, total_score=0, user_id=uid)
        db.session.add(player)
        db.session.commit()
    return player


def question_options(q):
    pairs = [('A', q.option_a), ('B', q.option_b), ('C', q.option_c), ('D', q.option_d)]
    return [(letter, text) for letter, text in pairs if text]


def explain_question(q):
    """شرح الإجابة من نص التداخل نفسه (للأسئلة المولَّدة فقط)."""
    if q.source_key and q.source_key.startswith('i'):
        try:
            inter_id = int(q.source_key[1:].split(':')[0])
        except ValueError:
            return None
        it = DrugInteraction.query.get(inter_id)
        if it:
            return f'درجة الخطورة: {SEVERITY_AR.get(it.severity, it.severity)}. {it.description}'
    return None


@app.route('/quiz')
@role_required('pharmacist')
def quiz_home():
    player = get_player()
    total = PlayerAttempt.query.filter_by(player_id=player.player_id).count()
    correct = PlayerAttempt.query.filter_by(player_id=player.player_id, is_correct=True).count()
    rank = Player.query.filter(Player.total_score > (player.total_score or 0)).count() + 1
    quiz = session.get('quiz')
    in_progress = bool(quiz and quiz['i'] < len(quiz['ids']))
    return render_template('quiz/home.html', player=player, total=total, correct=correct,
                           rank=rank, round_size=ROUND_SIZE, in_progress=in_progress)


@app.route('/quiz/start', methods=['POST'])
@role_required('pharmacist')
def quiz_start():
    ids = build_round()
    if not ids:
        flash('لا توجد أسئلة كافية بعد. يحتاج الأدمن إلى إضافة تداخلات أولًا.')
        return redirect(url_for('quiz_home'))
    session['quiz'] = {'ids': ids, 'i': 0, 'score': 0, 'answered': False, 'last': None}
    return redirect(url_for('quiz_play'))


@app.route('/quiz/play')
@role_required('pharmacist')
def quiz_play():
    quiz = session.get('quiz')
    if not quiz:
        return redirect(url_for('quiz_home'))
    if quiz['i'] >= len(quiz['ids']):
        return redirect(url_for('quiz_result'))
    if quiz['answered']:
        return redirect(url_for('quiz_feedback'))

    q = Question.query.get(quiz['ids'][quiz['i']])
    if q is None:  # سؤال حُذف أثناء الجولة: نتخطاه
        session['quiz'] = dict(quiz, i=quiz['i'] + 1)
        return redirect(url_for('quiz_play'))
    return render_template('quiz/play.html', q=q, options=question_options(q),
                           number=quiz['i'] + 1, total=len(quiz['ids']), score=quiz['score'])


@app.route('/quiz/answer', methods=['POST'])
@role_required('pharmacist')
def quiz_answer():
    quiz = session.get('quiz')
    if not quiz or quiz['i'] >= len(quiz['ids']):
        return redirect(url_for('quiz_home'))
    if quiz['answered']:
        return redirect(url_for('quiz_feedback'))

    q = Question.query.get(quiz['ids'][quiz['i']])
    if q is None:
        return redirect(url_for('quiz_play'))

    selected = request.form.get('option', '')
    if selected not in [letter for letter, _ in question_options(q)]:
        flash('اختر إجابة أولًا')
        return redirect(url_for('quiz_play'))

    is_correct = (selected == q.correct_option)
    player = get_player()
    db.session.add(PlayerAttempt(player_id=player.player_id, question_id=q.question_id,
                                 selected_option=selected, is_correct=is_correct))
    if is_correct:
        player.total_score = (player.total_score or 0) + POINTS_PER_CORRECT
    db.session.commit()

    session['quiz'] = dict(quiz, answered=True,
                           score=quiz['score'] + (POINTS_PER_CORRECT if is_correct else 0),
                           last={'selected': selected, 'correct': q.correct_option,
                                 'is_correct': is_correct})
    return redirect(url_for('quiz_feedback'))


@app.route('/quiz/feedback')
@role_required('pharmacist')
def quiz_feedback():
    quiz = session.get('quiz')
    if not quiz or not quiz['answered'] or not quiz['last']:
        return redirect(url_for('quiz_play'))
    q = Question.query.get(quiz['ids'][quiz['i']])
    if q is None:
        return redirect(url_for('quiz_play'))
    return render_template('quiz/feedback.html', q=q, options=question_options(q),
                           last=quiz['last'], explanation=explain_question(q),
                           number=quiz['i'] + 1, total=len(quiz['ids']),
                           score=quiz['score'], is_last=(quiz['i'] + 1 >= len(quiz['ids'])))


@app.route('/quiz/exit', methods=['POST'])
@role_required('pharmacist')
def quiz_exit():
    # إنهاء الجولة الحالية والعودة إلى صفحة اللعبة (النقاط المكتسبة تبقى محفوظة)
    session.pop('quiz', None)
    return redirect(url_for('quiz_home'))


@app.route('/quiz/next', methods=['POST'])
@role_required('pharmacist')
def quiz_next():
    quiz = session.get('quiz')
    if not quiz or not quiz['answered']:
        return redirect(url_for('quiz_play'))
    session['quiz'] = dict(quiz, i=quiz['i'] + 1, answered=False, last=None)
    return redirect(url_for('quiz_play'))


@app.route('/quiz/result')
@role_required('pharmacist')
def quiz_result():
    quiz = session.get('quiz')
    if not quiz:
        return redirect(url_for('quiz_home'))
    if quiz['i'] < len(quiz['ids']):
        return redirect(url_for('quiz_play'))
    player = get_player()
    return render_template('quiz/result.html', score=quiz['score'],
                           max_score=len(quiz['ids']) * POINTS_PER_CORRECT,
                           total_score=player.total_score or 0)


@app.route('/quiz/leaderboard')
@role_required('pharmacist')
def quiz_leaderboard():
    me = get_player()
    top = Player.query.order_by(Player.total_score.desc(), Player.player_id).limit(10).all()
    return render_template('quiz/leaderboard.html', top=top, me=me.player_id)


# ============================================================
# نسيت كلمة المرور: رمز تحقق لمرة واحدة (OTP) يُرسل إلى البريد
# ============================================================

RESET_CODE_MINUTES = 10      # مدة صلاحية الرمز
RESET_MAX_ATTEMPTS = 5       # عدد المحاولات الخاطئة المسموح
RESET_RESEND_SECONDS = 60    # أقل مدة بين طلبين للرمز

# بيانات حساب البريد المرسِل تُقرأ من متغيرات البيئة، ولا تُكتب في الكود.
# إن لم تُضبط، يُطبع الرمز في الطرفية (وضع التجربة).
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
# إرسال البريد عبر Brevo (HTTPS): هو الذي يعمل على Render المجاني
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
MAIL_FROM = os.environ.get('MAIL_FROM', MAIL_USERNAME)


def hash_reset_code(user_id, code):
    """نخزّن بصمة الرمز لا الرمز نفسه."""
    key = app.config['SECRET_KEY'].encode('utf-8')
    return hmac.new(key, f'{user_id}:{code}'.encode('utf-8'), hashlib.sha256).hexdigest()


def mask_email(email):
    name, _, domain = email.partition('@')
    return f'{name[:2]}***@{domain}' if domain else '***'


def send_reset_email(to_email, code):
    """يرسل الرمز بالبريد. يعيد True عند النجاح."""
    subject = 'رمز التحقق - نظام صيدلاني خبير'
    body = (f'رمز التحقق الخاص بك: {code}\n\n'
            f'الرمز صالح لمدة {RESET_CODE_MINUTES} دقائق ويُستخدم مرة واحدة.\n'
            'إن لم تطلب هذا الرمز فتجاهل هذه الرسالة.')

    # 1) عبر Brevo (HTTPS): يعمل على Render المجاني
    if BREVO_API_KEY and MAIL_FROM:
        payload = json.dumps({
            'sender': {'name': 'نظام صيدلاني خبير', 'email': MAIL_FROM},
            'to': [{'email': to_email}],
            'subject': subject,
            'textContent': body,
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.brevo.com/v3/smtp/email', data=payload, method='POST',
            headers={'api-key': BREVO_API_KEY,
                     'content-type': 'application/json',
                     'accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return 200 <= resp.status < 300
        except urllib.error.HTTPError as exc:
            print('[خطأ Brevo]', exc.code, exc.read().decode('utf-8', 'ignore'))
            return False
        except Exception as exc:
            print('[خطأ في إرسال البريد]', exc)
            return False

    # 2) عبر SMTP: للتجربة على جهازك أو استضافة مدفوعة
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print(f'[وضع التجربة] رمز التحقق للبريد {to_email}: {code}')
        return True
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = MAIL_USERNAME
        msg['To'] = to_email
        msg.set_content(body, charset='utf-8')
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT,
                              context=ssl.create_default_context(), timeout=15) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f'[خطأ في إرسال البريد] {exc}')
        return False


def login_user(user):
    session.clear()
    session['user_id'] = user.id
    session['role'] = user.role


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('أدخل بريدك الإلكتروني')
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('هذا البريد الإلكتروني غير مسجّل لدينا')
            return redirect(url_for('forgot_password'))

        session['reset_email'] = email
        now = datetime.now().replace(microsecond=0)

        latest = (PasswordReset.query.filter_by(user_id=user.id, used=False)
                  .order_by(PasswordReset.id.desc()).first())
        if latest:
            sent_at = latest.expires_at - timedelta(minutes=RESET_CODE_MINUTES)
            if sent_at + timedelta(seconds=RESET_RESEND_SECONDS) > now:
                flash('أُرسل رمز قبل قليل. أدخل الرمز الذي وصلك، أو انتظر دقيقة لطلب رمز جديد.')
                return redirect(url_for('reset_code'))

        code = f'{secrets.randbelow(10 ** 6):06d}'
        try:
            PasswordReset.query.filter_by(user_id=user.id, used=False).update(
                {'used': True}, synchronize_session=False)
            db.session.add(PasswordReset(
                user_id=user.id, code_hash=hash_reset_code(user.id, code),
                expires_at=now + timedelta(minutes=RESET_CODE_MINUTES),
                attempts=0, used=False))
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('تعذّر إنشاء الرمز، حاول مرة أخرى')
            return redirect(url_for('forgot_password'))

        if not send_reset_email(user.email, code):
            flash('تعذّر إرسال الرمز إلى البريد الآن، حاول لاحقًا')
            return redirect(url_for('forgot_password'))

        flash(f'تم إرسال رمز التحقق إلى بريدك، وهو صالح لمدة {RESET_CODE_MINUTES} دقائق')
        return redirect(url_for('reset_code'))

    return render_template('auth/forgot.html')


@app.route('/reset-code', methods=['GET', 'POST'])
def reset_code():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        user = User.query.filter_by(email=email).first()
        record = None
        if user:
            record = (PasswordReset.query.filter_by(user_id=user.id, used=False)
                      .order_by(PasswordReset.id.desc()).first())
        now = datetime.now().replace(microsecond=0)

        if record is None or record.expires_at < now:
            flash('الرمز غير صحيح أو انتهت صلاحيته')
        else:
            record.attempts += 1
            if record.attempts > RESET_MAX_ATTEMPTS:
                record.used = True
                db.session.commit()
                flash('تجاوزت عدد المحاولات المسموح. اطلب رمزًا جديدًا.')
            elif hmac.compare_digest(record.code_hash, hash_reset_code(user.id, code)):
                record.used = True
                db.session.commit()
                session.pop('reset_email', None)
                session['reset_user_id'] = user.id
                session['reset_verified_at'] = now.timestamp()
                return redirect(url_for('reset_password'))
            else:
                db.session.commit()
                flash(f'الرمز غير صحيح. المحاولات المتبقية: {RESET_MAX_ATTEMPTS - record.attempts}')
        return redirect(url_for('reset_code'))  # يبقى في صفحة الرمز نفسها

    return render_template('auth/code.html', masked=mask_email(email), minutes=RESET_CODE_MINUTES)


def verified_reset_user():
    uid = session.get('reset_user_id')
    verified_at = session.get('reset_verified_at')
    if not uid or not verified_at:
        return None
    if datetime.now().timestamp() - verified_at > RESET_CODE_MINUTES * 60:
        session.pop('reset_user_id', None)
        session.pop('reset_verified_at', None)
        return None
    return User.query.get(uid)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    user = verified_reset_user()
    if user is None:
        flash('انتهت صلاحية العملية. اطلب رمزًا جديدًا.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        if request.form.get('action') == 'skip':
            login_user(user)  # دخول مباشر دون تغيير كلمة المرور
            return redirect(url_for('dashboard'))

        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if len(new) < 8:
            flash('كلمة المرور الجديدة يجب أن تكون 8 رموز على الأقل')
        elif new != confirm:
            flash('كلمة المرور الجديدة وتأكيدها غير متطابقين')
        else:
            user.password = generate_password_hash(new)
            db.session.commit()
            login_user(user)
            flash('تم تغيير كلمة المرور بنجاح')
            return redirect(url_for('dashboard'))
        return redirect(url_for('reset_password'))

    return render_template('auth/reset.html', username=user.username)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)