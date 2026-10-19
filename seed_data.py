# -*- coding: utf-8 -*-
"""
seed_data.py  -  تعبئة قاعدة بيانات (نظام التداخلات الدوائية) بالبيانات العربية
وإضافة حساب المدير.

التشغيل (في cmd):
    pip install pymysql cryptography werkzeug
    python import_schema.py     <- مرة واحدة فقط لإنشاء الجداول (إن لم تكن موجودة)
    python seed_data.py

السكربت آمن للتشغيل أكثر من مرة: لا يكرر السجلات الموجودة.
الأسئلة (questions) لا تُضاف هنا لأن التطبيق يولّدها تلقائيًا من التداخلات.
"""
import pymysql
from urllib.parse import urlparse, unquote
from werkzeug.security import generate_password_hash

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'drugsinteractionssudan@gmail.com'
ADMIN_PASSWORD = 'Admin@2026'   # غيّرها بعد أول دخول من صفحة تغيير كلمة المرور

# ------------------------------------------------------------------
# البيانات
# ------------------------------------------------------------------
CLASSIFICATIONS = [
    ('مضادات التخثر', 'Anticoagulants', 'أدوية تقلل قدرة الدم على التجلط وتُستخدم للوقاية من الجلطات.'),
    ('مضادات الالتهاب غير الستيرويدية', 'NSAIDs', 'أدوية تخفف الألم والالتهاب وتخفض الحرارة.'),
    ('المسكنات وخافضات الحرارة', 'Analgesics and antipyretics', 'أدوية لتسكين الألم الخفيف إلى المتوسط وخفض الحمى.'),
    ('أدوية داء السكري', 'Antidiabetics', 'أدوية تضبط مستوى سكر الدم لدى مرضى السكري.'),
    ('حاصرات قنوات الكالسيوم', 'Calcium Channel Blockers', 'أدوية لعلاج ارتفاع ضغط الدم والذبحة الصدرية.'),
    ('مثبطات الإنزيم المحوّل للأنجيوتنسين', 'ACE Inhibitors', 'أدوية لعلاج ارتفاع ضغط الدم وقصور القلب.'),
    ('حاصرات بيتا', 'Beta Blockers', 'أدوية تبطئ نبض القلب وتخفض ضغط الدم.'),
    ('الستاتينات', 'Statins', 'أدوية تخفض مستوى الكوليسترول في الدم.'),
    ('المضادات الحيوية', 'Antibiotics', 'أدوية لعلاج العدوى البكتيرية والطفيلية.'),
    ('مثبطات مضخة البروتون', 'Proton Pump Inhibitors', 'أدوية تقلل إفراز حمض المعدة.'),
    ('الغليكوزيدات القلبية', 'Cardiac Glycosides', 'أدوية تقوّي انقباض القلب وتنظم نبضه.'),
    ('مدرات البول', 'Diuretics', 'أدوية تزيد إدرار البول وتخفض ضغط الدم وتخفف الوذمة.'),
    ('مضادات الفطريات', 'Antifungals', 'أدوية لعلاج العدوى الفطرية.'),
    ('مضادات الملاريا', 'Antimalarials', 'أدوية لعلاج الملاريا والوقاية منها.'),
]

SIDE_EFFECTS = [
    ('غثيان', 'Nausea', 'شعور بالرغبة في التقيؤ.', 'بسيط'),
    ('قيء', 'Vomiting', 'خروج محتويات المعدة عن طريق الفم.', 'بسيط'),
    ('إسهال', 'Diarrhea', 'زيادة عدد مرات التبرز مع ليونة البراز.', 'بسيط'),
    ('صداع', 'Headache', 'ألم في الرأس بدرجات متفاوتة.', 'بسيط'),
    ('دوخة', 'Dizziness', 'شعور بعدم الاتزان أو دوار.', 'بسيط'),
    ('نعاس', 'Drowsiness', 'ميل شديد إلى النوم وانخفاض في اليقظة.', 'بسيط'),
    ('ألم في المعدة', 'Stomach Pain', 'ألم أو حرقة في أعلى البطن.', 'متوسط'),
    ('طفح جلدي', 'Skin Rash', 'ظهور احمرار أو حكة أو بقع على الجلد.', 'متوسط'),
    ('سعال جاف', 'Dry Cough', 'سعال مستمر غير مصحوب ببلغم.', 'بسيط'),
    ('طعم معدني في الفم', 'Metallic Taste', 'إحساس بطعم معدني مزعج في الفم.', 'بسيط'),
    ('تورم الكاحلين', 'Ankle Edema', 'احتباس السوائل وتورم القدمين والكاحلين.', 'متوسط'),
    ('بطء ضربات القلب', 'Bradycardia', 'انخفاض معدل نبض القلب عن المعدل الطبيعي.', 'متوسط'),
    ('ألم في العضلات', 'Muscle Pain', 'ألم أو ضعف في العضلات.', 'متوسط'),
    ('انخفاض سكر الدم', 'Hypoglycemia', 'هبوط مستوى سكر الدم مع تعرق ورجفة وإرهاق.', 'خطير'),
    ('ارتفاع البوتاسيوم في الدم', 'Hyperkalemia', 'زيادة البوتاسيوم في الدم وقد تسبب اضطرابًا في نظم القلب.', 'خطير'),
    ('نزف', 'Bleeding', 'نزف غير طبيعي أو صعوبة في إيقاف النزف.', 'خطير'),
    ('اضطراب نظم القلب', 'Arrhythmia', 'عدم انتظام ضربات القلب.', 'خطير'),
    ('تضرر الكبد', 'Liver Damage', 'ارتفاع إنزيمات الكبد أو التهابه.', 'خطير'),
    ('تفاعل تحسسي شديد', 'Anaphylaxis', 'حساسية مفرطة قد تهدد الحياة وتحتاج إلى إسعاف فوري.', 'خطير'),
]

SYMPTOMS = [
    ('ألم في الصدر', 'Chest Pain', 'ألم أو ضغط في منطقة الصدر.'),
    ('ضيق في التنفس', 'Shortness of Breath', 'صعوبة في التنفس أو الشعور بالاختناق.'),
    ('اصفرار الجلد والعينين', 'Jaundice', 'علامة على مشكلة في الكبد.'),
    ('براز أسود', 'Black Stools', 'قد يدل على نزف في الجهاز الهضمي العلوي.'),
    ('كدمات سهلة', 'Easy Bruising', 'ظهور كدمات بسبب ضربات خفيفة.'),
    ('خفقان', 'Palpitations', 'الإحساس بضربات القلب السريعة أو غير المنتظمة.'),
    ('تعرق شديد ورجفة', 'Sweating and Tremor', 'من علامات انخفاض سكر الدم.'),
    ('ضعف عضلي', 'Muscle Weakness', 'ضعف غير معتاد في العضلات.'),
    ('بول داكن', 'Dark Urine', 'قد يدل على مشكلة في الكبد أو العضلات.'),
    ('تورم الوجه أو الشفتين', 'Facial or Lip Swelling', 'علامة على تفاعل تحسسي.'),
    ('إغماء', 'Fainting', 'فقدان مؤقت للوعي.'),
    ('انخفاض كمية البول', 'Reduced Urine Output', 'قد يدل على إجهاد الكلى.'),
]

CONDITIONS = [
    ('الربو القصبي', 'مرض مزمن يصيب المجاري التنفسية ويسبب نوبات من ضيق التنفس والصفير.', 'أمراض الجهاز التنفسي'),
    ('أمراض الكلى', 'ضعف في وظائف الكلى وتراجع تدريجي في قدرتها على تصفية الدم.', 'الكلى'),
    ('أمراض الكبد', 'اضطرابات تؤثر في وظائف الكبد مثل التهاب الكبد والتليف.', 'أمراض الجهاز الهضمي'),
    ('قرحة المعدة', 'تقرحات في بطانة المعدة أو الاثني عشر.', 'أمراض الجهاز الهضمي'),
    ('ارتفاع ضغط الدم', 'ارتفاع مستمر في ضغط الدم الشرياني.', 'أمراض القلب والأوعية الدموية'),
    ('داء السكري', 'اضطراب مزمن في استقلاب السكر بسبب نقص الإنسولين أو مقاومته.', 'الأمراض الاستقلابية'),
    ('قصور القلب', 'عجز القلب عن ضخ الدم بكفاءة لتلبية حاجة الجسم.', 'أمراض القلب والأوعية الدموية'),
    ('اضطراب نظم القلب', 'عدم انتظام في ضربات القلب أو سرعتها.', 'أمراض القلب والأوعية الدموية'),
    ('الصرع', 'اضطراب عصبي مزمن يتميز بنوبات تشنجية متكررة.', 'أمراض الجهاز العصبي'),
    ('النقرس', 'التهاب مفصلي ناتج عن ارتفاع حمض اليوريك في الدم.', 'أمراض المفاصل'),
    ('الحساسية من البنسلين', 'تفاعل تحسسي تجاه البنسلين ومشتقاته.', 'الحساسية'),
    ('فقر الدم المنجلي', 'اضطراب وراثي في كريات الدم الحمراء.', 'أمراض الدم'),
]

# (الاسم العلمي, الاسم التجاري, الشكل الدوائي, التركيز, الجرعة, التحذير, التصنيف)
MEDICATIONS = [
    ('Warfarin', 'Coumadin', 'أقراص', '5 mg', 'حسب قيمة INR', 'دواء ضيق المدى العلاجي، ويلزم متابعة INR بانتظام وتجنب تغيير الجرعة دون استشارة الطبيب.', 'Anticoagulants'),
    ('Aspirin', 'Aspirin', 'أقراص', '100 mg', 'قرص واحد يوميًا', 'يزيد خطر النزف وتهيج المعدة، ولا يُعطى للأطفال دون 16 سنة إلا بإشراف طبي.', 'NSAIDs'),
    ('Ibuprofen', 'Brufen', 'أقراص', '400 mg', 'قرص كل 8 ساعات', 'يؤخذ بعد الطعام، ويُتجنب عند مرضى القرحة والكلى والحمل المتأخر.', 'NSAIDs'),
    ('Diclofenac', 'Voltaren', 'أقراص', '50 mg', 'قرص مرتين إلى ثلاث يوميًا', 'يزيد خطر النزف الهضمي والأحداث القلبية، ويُستخدم بأقل جرعة ولأقصر مدة.', 'NSAIDs'),
    ('Paracetamol', 'Panadol', 'أقراص', '500 mg', 'قرصان كل 6 ساعات بحد أقصى 4 غرامات يوميًا', 'تجاوز الجرعة القصوى يسبب تلفًا خطيرًا في الكبد.', 'Analgesics and antipyretics'),
    ('Metformin', 'Glucophage', 'أقراص', '500 mg', 'قرص مرتين يوميًا مع الطعام', 'يُوقف قبل الفحوص الظليلة، ويُتجنب عند قصور الكلى الشديد.', 'Antidiabetics'),
    ('Glibenclamide', 'Daonil', 'أقراص', '5 mg', 'قرص قبل الإفطار', 'قد يسبب هبوطًا حادًا في سكر الدم، خاصة عند كبار السن أو عند تخطي الوجبات.', 'Antidiabetics'),
    ('Amlodipine', 'Norvasc', 'أقراص', '5 mg', 'قرص واحد يوميًا', 'قد يسبب تورم الكاحلين ودوخة عند بدء العلاج.', 'Calcium Channel Blockers'),
    ('Enalapril', 'Renitec', 'أقراص', '10 mg', 'قرص واحد أو قرصان يوميًا', 'يُمنع في الحمل، وقد يسبب سعالًا جافًا وارتفاعًا في البوتاسيوم.', 'ACE Inhibitors'),
    ('Atenolol', 'Tenormin', 'أقراص', '50 mg', 'قرص واحد يوميًا', 'لا يُوقف فجأة، ويُتجنب عند مرضى الربو.', 'Beta Blockers'),
    ('Simvastatin', 'Zocor', 'أقراص', '20 mg', 'قرص مساءً', 'قد يسبب ألمًا عضليًا وتضررًا في الكبد، ويُمنع في الحمل.', 'Statins'),
    ('Clarithromycin', 'Klacid', 'أقراص', '500 mg', 'قرص كل 12 ساعة', 'يتداخل مع عدد كبير من الأدوية عبر تثبيط إنزيمات الكبد.', 'Antibiotics'),
    ('Ciprofloxacin', 'Ciprobay', 'أقراص', '500 mg', 'قرص كل 12 ساعة', 'قد يسبب التهاب الأوتار، ولا يُنصح به للأطفال والحوامل إلا للضرورة.', 'Antibiotics'),
    ('Amoxicillin', 'Amoxil', 'كبسولات', '500 mg', 'كبسولة كل 8 ساعات', 'يُمنع عند من لديهم حساسية من البنسلين.', 'Antibiotics'),
    ('Metronidazole', 'Flagyl', 'أقراص', '500 mg', 'قرص كل 8 ساعات', 'يُمنع تناول الكحول أثناء العلاج وبعده بـ 48 ساعة.', 'Antibiotics'),
    ('Omeprazole', 'Losec', 'كبسولات', '20 mg', 'كبسولة قبل الفطور', 'الاستعمال الطويل قد يقلل امتصاص المغنيسيوم وفيتامين B12.', 'Proton Pump Inhibitors'),
    ('Digoxin', 'Lanoxin', 'أقراص', '0.25 mg', 'حسب توجيه الطبيب', 'دواء ضيق المدى العلاجي، ويلزم مراقبة مستواه في الدم ومستوى البوتاسيوم.', 'Cardiac Glycosides'),
    ('Furosemide', 'Lasix', 'أقراص', '40 mg', 'قرص صباحًا', 'قد يسبب جفافًا وانخفاضًا في البوتاسيوم.', 'Diuretics'),
    ('Spironolactone', 'Aldactone', 'أقراص', '25 mg', 'قرص واحد يوميًا', 'يرفع البوتاسيوم في الدم، ويلزم الحذر عند قصور الكلى.', 'Diuretics'),
    ('Fluconazole', 'Diflucan', 'كبسولات', '150 mg', 'كبسولة واحدة أو حسب الحالة', 'يتداخل مع أدوية كثيرة ويطيل فترة QT في بعض الحالات.', 'Antifungals'),
    ('Artemether-Lumefantrine', 'Coartem', 'أقراص', '20/120 mg', 'ست جرعات خلال ثلاثة أيام', 'يُؤخذ مع وجبة دسمة، ويُتجنب مع الأدوية المطيلة لفترة QT.', 'Antimalarials'),
]

MED_SIDE_EFFECTS = {
    'Warfarin': ['Bleeding'],
    'Aspirin': ['Stomach Pain', 'Bleeding', 'Nausea'],
    'Ibuprofen': ['Stomach Pain', 'Nausea', 'Dizziness'],
    'Diclofenac': ['Stomach Pain', 'Nausea', 'Headache', 'Skin Rash'],
    'Paracetamol': ['Nausea', 'Liver Damage'],
    'Metformin': ['Nausea', 'Diarrhea', 'Metallic Taste'],
    'Glibenclamide': ['Hypoglycemia', 'Nausea', 'Skin Rash'],
    'Amlodipine': ['Ankle Edema', 'Headache', 'Dizziness'],
    'Enalapril': ['Dry Cough', 'Dizziness', 'Hyperkalemia'],
    'Atenolol': ['Bradycardia', 'Dizziness', 'Drowsiness'],
    'Simvastatin': ['Muscle Pain', 'Headache', 'Liver Damage'],
    'Clarithromycin': ['Nausea', 'Diarrhea', 'Metallic Taste', 'Arrhythmia'],
    'Ciprofloxacin': ['Nausea', 'Diarrhea', 'Headache', 'Dizziness'],
    'Amoxicillin': ['Diarrhea', 'Skin Rash', 'Anaphylaxis'],
    'Metronidazole': ['Nausea', 'Metallic Taste', 'Headache'],
    'Omeprazole': ['Headache', 'Diarrhea', 'Stomach Pain'],
    'Digoxin': ['Nausea', 'Vomiting', 'Arrhythmia', 'Bradycardia'],
    'Furosemide': ['Dizziness', 'Muscle Pain'],
    'Spironolactone': ['Hyperkalemia', 'Dizziness', 'Nausea'],
    'Fluconazole': ['Nausea', 'Headache', 'Skin Rash', 'Liver Damage'],
    'Artemether-Lumefantrine': ['Headache', 'Dizziness', 'Vomiting', 'Arrhythmia'],
}

MED_SYMPTOMS = {
    'Warfarin': ['Easy Bruising', 'Black Stools'],
    'Aspirin': ['Black Stools', 'Easy Bruising'],
    'Ibuprofen': ['Black Stools', 'Reduced Urine Output'],
    'Diclofenac': ['Black Stools', 'Chest Pain'],
    'Paracetamol': ['Jaundice', 'Dark Urine'],
    'Metformin': ['Muscle Weakness', 'Shortness of Breath'],
    'Glibenclamide': ['Sweating and Tremor', 'Fainting'],
    'Amlodipine': ['Palpitations', 'Fainting'],
    'Enalapril': ['Facial or Lip Swelling', 'Fainting'],
    'Atenolol': ['Shortness of Breath', 'Fainting'],
    'Simvastatin': ['Muscle Weakness', 'Dark Urine'],
    'Clarithromycin': ['Palpitations', 'Jaundice'],
    'Ciprofloxacin': ['Muscle Weakness', 'Palpitations'],
    'Amoxicillin': ['Facial or Lip Swelling', 'Shortness of Breath'],
    'Metronidazole': ['Dark Urine'],
    'Omeprazole': ['Muscle Weakness'],
    'Digoxin': ['Palpitations', 'Fainting', 'Chest Pain'],
    'Furosemide': ['Muscle Weakness', 'Reduced Urine Output'],
    'Spironolactone': ['Palpitations', 'Muscle Weakness'],
    'Fluconazole': ['Jaundice', 'Palpitations'],
    'Artemether-Lumefantrine': ['Palpitations', 'Fainting'],
}

# (دواء 1, دواء 2, الخطورة, الوصف)
INTERACTIONS = [
    ('Warfarin', 'Aspirin', 'major', 'يزداد خطر النزف بشكل كبير عند الجمع بينهما، فالأسبرين يثبط الصفائح الدموية ويهيج المعدة والوارفارين يضعف التخثر. يُتجنب الجمع إلا بإشراف طبي.'),
    ('Warfarin', 'Ibuprofen', 'major', 'يرفع الإيبوبروفين خطر النزف الهضمي عند مرضى الوارفارين. يُفضل استخدام الباراسيتامول بديلًا.'),
    ('Warfarin', 'Diclofenac', 'major', 'يزيد الديكلوفيناك خطر النزف الهضمي عند تناوله مع الوارفارين. يُنصح بتجنب الجمع.'),
    ('Warfarin', 'Metronidazole', 'major', 'يثبط الميترونيدازول استقلاب الوارفارين فيرتفع INR ويزداد خطر النزف. يلزم تعديل الجرعة ومراقبة INR.'),
    ('Warfarin', 'Fluconazole', 'major', 'يرفع الفلوكونازول مستوى الوارفارين في الدم ويزيد خطر النزف. يلزم مراقبة INR عن قرب.'),
    ('Warfarin', 'Clarithromycin', 'major', 'يزيد الكلاريثروميسين من تأثير الوارفارين المضاد للتخثر ويرفع خطر النزف.'),
    ('Warfarin', 'Ciprofloxacin', 'moderate', 'قد يزيد السيبروفلوكساسين من تأثير الوارفارين، لذا يُنصح بمراقبة INR أثناء العلاج.'),
    ('Warfarin', 'Paracetamol', 'moderate', 'الاستعمال المنتظم لجرعات عالية من الباراسيتامول قد يرفع INR عند مرضى الوارفارين.'),
    ('Simvastatin', 'Clarithromycin', 'major', 'يرفع الكلاريثروميسين مستوى السيمفاستاتين في الدم فيزداد خطر انحلال العضلات المخطط. يُوقف السيمفاستاتين مؤقتًا أثناء العلاج.'),
    ('Simvastatin', 'Amlodipine', 'moderate', 'يرتفع مستوى السيمفاستاتين عند تناوله مع الأملوديبين، ويُنصح بألا تتجاوز جرعة السيمفاستاتين 20 ملغ يوميًا.'),
    ('Digoxin', 'Clarithromycin', 'major', 'يرفع الكلاريثروميسين مستوى الديجوكسين في الدم وقد يسبب تسممًا بالديجوكسين.'),
    ('Digoxin', 'Furosemide', 'moderate', 'قد يسبب الفيوروسيميد نقصًا في البوتاسيوم مما يزيد سمّية الديجوكسين على القلب.'),
    ('Enalapril', 'Spironolactone', 'major', 'يزيد الجمع بينهما خطر ارتفاع البوتاسيوم في الدم ارتفاعًا خطيرًا، ويلزم فحص البوتاسيوم ووظائف الكلى بانتظام.'),
    ('Enalapril', 'Ibuprofen', 'moderate', 'يقلل الإيبوبروفين من التأثير الخافض للضغط ويزيد خطر تضرر الكلى.'),
    ('Enalapril', 'Diclofenac', 'moderate', 'قد يضعف الديكلوفيناك تأثير الإينالابريل ويزيد الضغط على الكلى.'),
    ('Furosemide', 'Ibuprofen', 'moderate', 'قد يضعف الإيبوبروفين تأثير الفيوروسيميد المدر للبول ويزيد خطر تضرر الكلى.'),
    ('Spironolactone', 'Ibuprofen', 'moderate', 'قد يرفع الجمع بينهما البوتاسيوم ويضعف التأثير المدر للبول.'),
    ('Metformin', 'Ciprofloxacin', 'moderate', 'قد يسبب السيبروفلوكساسين اضطرابًا في سكر الدم عند مرضى السكري الذين يتناولون الميتفورمين.'),
    ('Metformin', 'Furosemide', 'minor', 'قد يرتفع مستوى الميتفورمين قليلًا عند تناوله مع الفيوروسيميد، وغالبًا لا يستدعي تغيير العلاج.'),
    ('Glibenclamide', 'Fluconazole', 'major', 'يرفع الفلوكونازول مستوى الغليبنكلاميد فيزداد خطر هبوط سكر الدم الشديد.'),
    ('Glibenclamide', 'Ciprofloxacin', 'moderate', 'قد يسبب الجمع بينهما هبوطًا في سكر الدم، ويُنصح بمراقبة مستوى السكر.'),
    ('Atenolol', 'Amlodipine', 'minor', 'يُستخدمان معًا أحيانًا لضبط الضغط، وقد يحدث انخفاض إضافي في الضغط أو بطء في النبض.'),
    ('Atenolol', 'Ibuprofen', 'moderate', 'قد يقلل الإيبوبروفين من التأثير الخافض للضغط لدى مرضى الأتينولول.'),
    ('Aspirin', 'Ibuprofen', 'moderate', 'قد يتعارض الإيبوبروفين مع التأثير الواقي للقلب الذي يوفره الأسبرين ويزيد خطر النزف الهضمي.'),
    ('Aspirin', 'Diclofenac', 'moderate', 'يزيد الجمع بينهما خطر القرحة والنزف الهضمي دون فائدة علاجية إضافية.'),
    ('Clarithromycin', 'Amlodipine', 'moderate', 'يرفع الكلاريثروميسين مستوى الأملوديبين فقد ينخفض الضغط انخفاضًا زائدًا.'),
    ('Clarithromycin', 'Omeprazole', 'minor', 'يرتفع مستوى كل من الدوائين قليلًا، وغالبًا لا يستدعي تعديل الجرعة.'),
    ('Artemether-Lumefantrine', 'Clarithromycin', 'major', 'يزيد الجمع بينهما خطر إطالة فترة QT واضطراب نظم القلب، كما يرتفع مستوى دواء الملاريا في الدم.'),
    ('Artemether-Lumefantrine', 'Fluconazole', 'moderate', 'قد يزيد الجمع بينهما خطر إطالة فترة QT، ويُنصح بمراقبة نظم القلب.'),
    ('Artemether-Lumefantrine', 'Ciprofloxacin', 'moderate', 'قد يؤدي الجمع بينهما إلى إطالة فترة QT، لذا يُستخدم بحذر.'),
]

# (الدواء, المرض أو None, حمل, عمر من, عمر إلى, الخطورة, الوصف)
CONTRAS = [
    ('Ibuprofen', 'قرحة المعدة', 0, None, None, 'major', 'قد يفاقم القرحة ويسبب نزفًا هضميًا. يُمنع عند وجود قرحة نشطة.'),
    ('Ibuprofen', 'أمراض الكلى', 0, None, None, 'major', 'يقلل تدفق الدم إلى الكلى وقد يزيد تدهور وظائفها.'),
    ('Ibuprofen', 'الربو القصبي', 0, None, None, 'moderate', 'قد يحرض نوبات الربو لدى بعض المرضى.'),
    ('Ibuprofen', 'قصور القلب', 0, None, None, 'moderate', 'قد يسبب احتباس السوائل ويفاقم قصور القلب.'),
    ('Ibuprofen', None, 1, None, None, 'major', 'يُتجنب في الثلث الأخير من الحمل لخطر إغلاق القناة الشريانية للجنين.'),
    ('Diclofenac', 'قرحة المعدة', 0, None, None, 'major', 'يزيد خطر النزف والتقرح الهضمي ويُمنع عند وجود قرحة نشطة.'),
    ('Diclofenac', 'أمراض الكلى', 0, None, None, 'major', 'قد يسبب تدهورًا إضافيًا في وظائف الكلى.'),
    ('Diclofenac', 'قصور القلب', 0, None, None, 'major', 'يزيد احتباس السوائل وخطر الأحداث القلبية الوعائية.'),
    ('Diclofenac', None, 1, None, None, 'major', 'يُتجنب في الحمل، خاصة في الثلث الأخير.'),
    ('Aspirin', 'قرحة المعدة', 0, None, None, 'major', 'يزيد خطر النزف الهضمي ويُمنع عند وجود قرحة نشطة.'),
    ('Aspirin', 'الربو القصبي', 0, None, None, 'moderate', 'قد يحرض نوبات ربو لدى المرضى الحساسين للأسبرين.'),
    ('Aspirin', None, 1, None, None, 'moderate', 'يُستخدم في الحمل بجرعات منخفضة وبإشراف الطبيب فقط.'),
    ('Aspirin', None, 0, 0, 16, 'major', 'يُمنع عند الأطفال واليافعين دون 16 سنة بسبب خطر متلازمة راي.'),
    ('Paracetamol', 'أمراض الكبد', 0, None, None, 'moderate', 'يلزم تخفيض الجرعة عند مرضى الكبد لتجنب السمّية الكبدية.'),
    ('Metformin', 'أمراض الكلى', 0, None, None, 'major', 'يزداد خطر الحماض اللبني، ويُمنع عند القصور الكلوي الشديد.'),
    ('Metformin', 'أمراض الكبد', 0, None, None, 'moderate', 'قد يزيد خطر الحماض اللبني عند ضعف وظائف الكبد.'),
    ('Glibenclamide', 'أمراض الكبد', 0, None, None, 'major', 'يرتفع خطر هبوط سكر الدم عند ضعف الكبد.'),
    ('Glibenclamide', 'أمراض الكلى', 0, None, None, 'major', 'يتراكم الدواء ومستقلباته ويزداد خطر هبوط السكر الشديد.'),
    ('Glibenclamide', None, 1, None, None, 'moderate', 'يُفضّل استبداله بالإنسولين أثناء الحمل.'),
    ('Enalapril', None, 1, None, None, 'major', 'يُمنع في الحمل لأنه قد يسبب تشوهات وتضررًا في كلى الجنين.'),
    ('Atenolol', 'الربو القصبي', 0, None, None, 'major', 'قد يسبب تضيقًا في القصبات الهوائية ويُتجنب عند مرضى الربو.'),
    ('Atenolol', None, 1, None, None, 'moderate', 'قد يؤثر في نمو الجنين، ويُستخدم عند الضرورة فقط.'),
    ('Simvastatin', 'أمراض الكبد', 0, None, None, 'major', 'يُمنع عند وجود مرض كبدي نشط أو ارتفاع غير مفسر في إنزيمات الكبد.'),
    ('Simvastatin', None, 1, None, None, 'major', 'يُمنع في الحمل والإرضاع.'),
    ('Warfarin', None, 1, None, None, 'major', 'يسبب تشوهات جنينية ونزفًا، ويُمنع خاصة في الثلث الأول.'),
    ('Warfarin', 'قرحة المعدة', 0, None, None, 'major', 'يزيد خطر النزف الهضمي الخطير عند وجود قرحة.'),
    ('Ciprofloxacin', None, 1, None, None, 'moderate', 'يُتجنب في الحمل ما لم تتوفر بدائل أكثر أمانًا.'),
    ('Ciprofloxacin', None, 0, 0, 17, 'moderate', 'يُتجنب عند الأطفال لخطر التأثير في الغضاريف والأوتار إلا للضرورة.'),
    ('Ciprofloxacin', 'الصرع', 0, None, None, 'moderate', 'قد يخفض عتبة التشنج ويحرض النوبات.'),
    ('Clarithromycin', 'أمراض الكبد', 0, None, None, 'moderate', 'يلزم الحذر وتعديل الجرعة عند ضعف وظائف الكبد.'),
    ('Clarithromycin', None, 1, None, None, 'moderate', 'يُتجنب في الحمل ما لم تكن الفائدة أكبر من الخطر.'),
    ('Clarithromycin', 'اضطراب نظم القلب', 0, None, None, 'major', 'قد يطيل فترة QT ويحرض اضطرابات خطيرة في نظم القلب.'),
    ('Amoxicillin', 'الحساسية من البنسلين', 0, None, None, 'major', 'يُمنع عند وجود حساسية من البنسلين لخطر التفاعل التحسسي الشديد.'),
    ('Metronidazole', None, 1, None, None, 'moderate', 'يُتجنب في الثلث الأول من الحمل إلا للضرورة.'),
    ('Metronidazole', 'أمراض الكبد', 0, None, None, 'moderate', 'يلزم خفض الجرعة عند ضعف الكبد الشديد.'),
    ('Digoxin', 'أمراض الكلى', 0, None, None, 'moderate', 'يلزم خفض الجرعة ومراقبة مستوى الدواء في الدم.'),
    ('Digoxin', 'اضطراب نظم القلب', 0, None, None, 'moderate', 'يُستخدم بحذر ويلزم مراقبة تخطيط القلب.'),
    ('Furosemide', 'النقرس', 0, None, None, 'moderate', 'قد يرفع حمض اليوريك ويحرض نوبات النقرس.'),
    ('Spironolactone', 'أمراض الكلى', 0, None, None, 'major', 'يزداد خطر ارتفاع البوتاسيوم الخطير.'),
    ('Fluconazole', None, 1, None, None, 'moderate', 'يُتجنب في الحمل، خاصة بالجرعات العالية.'),
    ('Fluconazole', 'أمراض الكبد', 0, None, None, 'moderate', 'قد يسبب سمّية كبدية ويلزم الحذر.'),
    ('Artemether-Lumefantrine', None, 1, None, None, 'moderate', 'يُستخدم في الثلث الأول من الحمل عند عدم توفر بديل فقط.'),
    ('Artemether-Lumefantrine', 'اضطراب نظم القلب', 0, None, None, 'major', 'يُتجنب لدى من لديهم إطالة في فترة QT أو اضطراب نظم القلب.'),
]


# ------------------------------------------------------------------
# أدوات مساعدة
# ------------------------------------------------------------------
def connect():
    uri = input('Paste your DATABASE_URL here, then press Enter: ').strip()
    u = urlparse(uri)
    if not u.username or not u.hostname:
        raise SystemExit('The link is empty or incomplete. It must start with mysql://')
    conn = pymysql.connect(
        host=u.hostname, port=u.port or 3306, user=unquote(u.username),
        password=unquote(u.password or ''), database=u.path.lstrip('/').split('?')[0],
        charset='utf8mb4', ssl={'fake_flag_to_enable_tls': True}, autocommit=False)
    print('Connected to database:', u.path.lstrip('/').split('?')[0])
    return conn


def get_or_create(cur, table, where, values=None):
    """يرجع id السجل إن وُجد، وإلا ينشئه. where و values قواميس."""
    cond = ' AND '.join(f'`{k}` <=> %s' for k in where)
    cur.execute(f'SELECT id FROM `{table}` WHERE {cond}', list(where.values()))
    row = cur.fetchone()
    if row:
        return row[0], False
    data = dict(where)
    data.update(values or {})
    cols = ', '.join(f'`{k}`' for k in data)
    ph = ', '.join(['%s'] * len(data))
    cur.execute(f'INSERT INTO `{table}` ({cols}) VALUES ({ph})', list(data.values()))
    return cur.lastrowid, True


def main():
    conn = connect()
    cur = conn.cursor()
    cur.execute('SET NAMES utf8mb4')

    cur.execute('SHOW TABLES')
    existing = {r[0] for r in cur.fetchall()}
    if 'medications' not in existing or 'users' not in existing:
        raise SystemExit('الجداول غير موجودة. شغّل python import_schema.py أولاً.')

    added = {}

    def bump(name, created):
        if created:
            added[name] = added.get(name, 0) + 1

    # التصنيفات
    cls_id = {}
    for ar, en, desc in CLASSIFICATIONS:
        i, c = get_or_create(cur, 'drug_classification',
                             {'name_english': en}, {'name_arabic': ar, 'description': desc})
        cls_id[en] = i
        bump('drug_classification', c)

    # الأعراض الجانبية
    se_id = {}
    for ar, en, desc, sev in SIDE_EFFECTS:
        i, c = get_or_create(cur, 'side_effects', {'name_english': en},
                             {'name_arabic': ar, 'description': desc, 'severity': sev})
        se_id[en] = i
        bump('side_effects', c)

    # الأعراض المصاحبة
    sy_id = {}
    for ar, en, desc in SYMPTOMS:
        i, c = get_or_create(cur, 'associated_symptoms', {'name_english': en},
                             {'name_arabic': ar, 'description': desc})
        sy_id[en] = i
        bump('associated_symptoms', c)

    # الحالات الصحية
    cond_id = {}
    for name, desc, cat in CONDITIONS:
        i, c = get_or_create(cur, 'health_conditions', {'condition_name': name},
                             {'condition_description': desc, 'condition_category': cat})
        cond_id[name] = i
        bump('health_conditions', c)

    # الأدوية
    med_id = {}
    for sci, trade, form, conc, dose, warn, cls in MEDICATIONS:
        i, c = get_or_create(cur, 'medications',
                             {'scientific_name': sci},
                             {'trade_name': trade, 'dosage_form': form, 'concentration': conc, 'dosage': dose,
                              'warning': warn, 'classification_id': cls_id[cls]})
        med_id[sci] = i
        bump('medications', c)

    # روابط الدواء بالأعراض
    for sci, items in MED_SIDE_EFFECTS.items():
        for en in items:
            cur.execute('INSERT IGNORE INTO medicine_sideeffects (medicine_id, side_effect_id) VALUES (%s,%s)',
                        (med_id[sci], se_id[en]))
            bump('medicine_sideeffects', cur.rowcount > 0)
    for sci, items in MED_SYMPTOMS.items():
        for en in items:
            cur.execute('INSERT IGNORE INTO med_associated (medicine_id, associated_symptom_id) VALUES (%s,%s)',
                        (med_id[sci], sy_id[en]))
            bump('med_associated', cur.rowcount > 0)

    # التداخلات الدوائية
    for a, b, sev, desc in INTERACTIONS:
        d1, d2 = med_id[a], med_id[b]
        cur.execute('SELECT interaction_id FROM drug_interactions '
                    'WHERE (drug_1_id=%s AND drug_2_id=%s) OR (drug_1_id=%s AND drug_2_id=%s)',
                    (d1, d2, d2, d1))
        if cur.fetchone():
            continue
        cur.execute('INSERT INTO drug_interactions (drug_1_id, drug_2_id, severity, description) '
                    'VALUES (%s,%s,%s,%s)', (d1, d2, sev, desc))
        bump('drug_interactions', True)

    # موانع الاستعمال
    for sci, cname, preg, lo, hi, sev, desc in CONTRAS:
        cid = cond_id[cname] if cname else None
        cur.execute('SELECT id FROM drug_contraindications WHERE medication_id=%s AND description=%s',
                    (med_id[sci], desc))
        if cur.fetchone():
            continue
        cur.execute('INSERT INTO drug_contraindications '
                    '(medication_id, condition_id, pregnancy_risk, age_from, age_to, severity, description) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (med_id[sci], cid, preg, lo, hi, sev, desc))
        bump('drug_contraindications', True)

    # حساب المدير
    pw_hash = generate_password_hash(ADMIN_PASSWORD)
    cur.execute('SELECT id FROM users WHERE email=%s', (ADMIN_EMAIL,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE users SET password=%s, role='admin' WHERE id=%s", (pw_hash, row[0]))
        print('Admin account already existed: password reset and role set to admin.')
    else:
        uname = ADMIN_USERNAME
        n = 1
        while True:
            cur.execute('SELECT id FROM users WHERE username=%s', (uname,))
            if not cur.fetchone():
                break
            n += 1
            uname = f'{ADMIN_USERNAME}{n}'
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s,%s,%s,'admin')",
                    (uname, ADMIN_EMAIL, pw_hash))
        print('Admin account created with username:', uname)

    conn.commit()
    print('\nRows added:')
    for k, v in added.items():
        print(f'  {k}: {v}')
    print('\nLogin  ->  email:', ADMIN_EMAIL, '| password:', ADMIN_PASSWORD)
    conn.close()


if __name__ == '__main__':
    main()