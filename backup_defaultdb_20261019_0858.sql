-- Backup of `defaultdb` created 2026-10-19 08:58:50.820326
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table `associated_symptoms`
-- ----------------------------
DROP TABLE IF EXISTS `associated_symptoms`;
CREATE TABLE "associated_symptoms" (
  "id" int NOT NULL AUTO_INCREMENT,
  "name_arabic" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "name_english" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "description" text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY ("id")
);

INSERT INTO `associated_symptoms` (`id`, `name_arabic`, `name_english`, `description`) VALUES
(1, 'ألم في الصدر', 'Chest Pain', 'ألم أو ضغط في منطقة الصدر.'),
(2, 'ضيق في التنفس', 'Shortness of Breath', 'صعوبة في التنفس أو الشعور بالاختناق.'),
(3, 'اصفرار الجلد والعينين', 'Jaundice', 'علامة على مشكلة في الكبد.'),
(4, 'براز أسود', 'Black Stools', 'قد يدل على نزف في الجهاز الهضمي العلوي.'),
(5, 'كدمات سهلة', 'Easy Bruising', 'ظهور كدمات بسبب ضربات خفيفة.'),
(6, 'خفقان', 'Palpitations', 'الإحساس بضربات القلب السريعة أو غير المنتظمة.'),
(7, 'تعرق شديد ورجفة', 'Sweating and Tremor', 'من علامات انخفاض سكر الدم.'),
(8, 'ضعف عضلي', 'Muscle Weakness', 'ضعف غير معتاد في العضلات.'),
(9, 'بول داكن', 'Dark Urine', 'قد يدل على مشكلة في الكبد أو العضلات.'),
(10, 'تورم الوجه أو الشفتين', 'Facial or Lip Swelling', 'علامة على تفاعل تحسسي.'),
(11, 'إغماء', 'Fainting', 'فقدان مؤقت للوعي.'),
(12, 'انخفاض كمية البول', 'Reduced Urine Output', 'قد يدل على إجهاد الكلى.');

-- ----------------------------
-- Table `ckeck_medicines`
-- ----------------------------
DROP TABLE IF EXISTS `ckeck_medicines`;
CREATE TABLE "ckeck_medicines" (
  "ckeck_id" int NOT NULL,
  "drug_id" int NOT NULL,
  PRIMARY KEY ("ckeck_id","drug_id"),
  KEY "fk_check_med_drug" ("drug_id"),
  CONSTRAINT "fk_check_med_check" FOREIGN KEY ("ckeck_id") REFERENCES "interaction_checks" ("check_id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_check_med_drug" FOREIGN KEY ("drug_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `ckeck_medicines` (`ckeck_id`, `drug_id`) VALUES
(2, 5),
(3, 5),
(4, 5),
(5, 5),
(6, 5),
(7, 5),
(8, 5),
(9, 5),
(1, 8),
(8, 8),
(9, 8),
(1, 14),
(9, 21);

-- ----------------------------
-- Table `drug_classification`
-- ----------------------------
DROP TABLE IF EXISTS `drug_classification`;
CREATE TABLE "drug_classification" (
  "id" int NOT NULL AUTO_INCREMENT,
  "name_arabic" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "name_english" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "description" text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY ("id")
);

INSERT INTO `drug_classification` (`id`, `name_arabic`, `name_english`, `description`) VALUES
(1, 'مضادات التخثر', 'Anticoagulants', 'أدوية تقلل قدرة الدم على التجلط وتُستخدم للوقاية من الجلطات.'),
(2, 'مضادات الالتهاب غير الستيرويدية', 'NSAIDs', 'أدوية تخفف الألم والالتهاب وتخفض الحرارة.'),
(3, 'المسكنات وخافضات الحرارة', 'Analgesics and antipyretics', 'أدوية لتسكين الألم الخفيف إلى المتوسط وخفض الحمى.'),
(4, 'أدوية داء السكري', 'Antidiabetics', 'أدوية تضبط مستوى سكر الدم لدى مرضى السكري.'),
(5, 'حاصرات قنوات الكالسيوم', 'Calcium Channel Blockers', 'أدوية لعلاج ارتفاع ضغط الدم والذبحة الصدرية.'),
(6, 'مثبطات الإنزيم المحوّل للأنجيوتنسين', 'ACE Inhibitors', 'أدوية لعلاج ارتفاع ضغط الدم وقصور القلب.'),
(7, 'حاصرات بيتا', 'Beta Blockers', 'أدوية تبطئ نبض القلب وتخفض ضغط الدم.'),
(8, 'الستاتينات', 'Statins', 'أدوية تخفض مستوى الكوليسترول في الدم.'),
(9, 'المضادات الحيوية', 'Antibiotics', 'أدوية لعلاج العدوى البكتيرية والطفيلية.'),
(10, 'مثبطات مضخة البروتون', 'Proton Pump Inhibitors', 'أدوية تقلل إفراز حمض المعدة.'),
(11, 'الغليكوزيدات القلبية', 'Cardiac Glycosides', 'أدوية تقوّي انقباض القلب وتنظم نبضه.'),
(12, 'مدرات البول', 'Diuretics', 'أدوية تزيد إدرار البول وتخفض ضغط الدم وتخفف الوذمة.'),
(13, 'مضادات الفطريات', 'Antifungals', 'أدوية لعلاج العدوى الفطرية.'),
(14, 'مضادات الملاريا', 'Antimalarials', 'أدوية لعلاج الملاريا والوقاية منها.');

-- ----------------------------
-- Table `drug_contraindications`
-- ----------------------------
DROP TABLE IF EXISTS `drug_contraindications`;
CREATE TABLE "drug_contraindications" (
  "id" int NOT NULL AUTO_INCREMENT,
  "medication_id" int NOT NULL,
  "condition_id" int DEFAULT NULL,
  "pregnancy_risk" tinyint(1) NOT NULL DEFAULT '0',
  "age_from" int DEFAULT NULL,
  "age_to" int DEFAULT NULL,
  "min_age" int DEFAULT NULL,
  "severity" enum('minor','moderate','major') COLLATE utf8mb4_unicode_ci NOT NULL,
  "description" text COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY ("id"),
  KEY "fk_contra_medication" ("medication_id"),
  KEY "fk_contra_condition" ("condition_id"),
  CONSTRAINT "fk_contra_condition" FOREIGN KEY ("condition_id") REFERENCES "health_conditions" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_contra_medication" FOREIGN KEY ("medication_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `drug_contraindications` (`id`, `medication_id`, `condition_id`, `pregnancy_risk`, `age_from`, `age_to`, `min_age`, `severity`, `description`) VALUES
(1, 3, 4, 0, NULL, NULL, NULL, 'major', 'قد يفاقم القرحة ويسبب نزفًا هضميًا. يُمنع عند وجود قرحة نشطة.'),
(2, 3, 2, 0, NULL, NULL, NULL, 'major', 'يقلل تدفق الدم إلى الكلى وقد يزيد تدهور وظائفها.'),
(3, 3, 1, 0, NULL, NULL, NULL, 'moderate', 'قد يحرض نوبات الربو لدى بعض المرضى.'),
(4, 3, 7, 0, NULL, NULL, NULL, 'moderate', 'قد يسبب احتباس السوائل ويفاقم قصور القلب.'),
(5, 3, NULL, 1, NULL, NULL, NULL, 'major', 'يُتجنب في الثلث الأخير من الحمل لخطر إغلاق القناة الشريانية للجنين.'),
(6, 4, 4, 0, NULL, NULL, NULL, 'major', 'يزيد خطر النزف والتقرح الهضمي ويُمنع عند وجود قرحة نشطة.'),
(7, 4, 2, 0, NULL, NULL, NULL, 'major', 'قد يسبب تدهورًا إضافيًا في وظائف الكلى.'),
(8, 4, 7, 0, NULL, NULL, NULL, 'major', 'يزيد احتباس السوائل وخطر الأحداث القلبية الوعائية.'),
(9, 4, NULL, 1, NULL, NULL, NULL, 'major', 'يُتجنب في الحمل، خاصة في الثلث الأخير.'),
(10, 2, 4, 0, NULL, NULL, NULL, 'major', 'يزيد خطر النزف الهضمي ويُمنع عند وجود قرحة نشطة.'),
(11, 2, 1, 0, NULL, NULL, NULL, 'moderate', 'قد يحرض نوبات ربو لدى المرضى الحساسين للأسبرين.'),
(12, 2, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُستخدم في الحمل بجرعات منخفضة وبإشراف الطبيب فقط.'),
(13, 2, NULL, 0, 0, 16, NULL, 'major', 'يُمنع عند الأطفال واليافعين دون 16 سنة بسبب خطر متلازمة راي.'),
(14, 5, 3, 0, NULL, NULL, NULL, 'moderate', 'يلزم تخفيض الجرعة عند مرضى الكبد لتجنب السمّية الكبدية.'),
(15, 6, 2, 0, NULL, NULL, NULL, 'major', 'يزداد خطر الحماض اللبني، ويُمنع عند القصور الكلوي الشديد.'),
(16, 6, 3, 0, NULL, NULL, NULL, 'moderate', 'قد يزيد خطر الحماض اللبني عند ضعف وظائف الكبد.'),
(17, 7, 3, 0, NULL, NULL, NULL, 'major', 'يرتفع خطر هبوط سكر الدم عند ضعف الكبد.'),
(18, 7, 2, 0, NULL, NULL, NULL, 'major', 'يتراكم الدواء ومستقلباته ويزداد خطر هبوط السكر الشديد.'),
(19, 7, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُفضّل استبداله بالإنسولين أثناء الحمل.'),
(20, 9, NULL, 1, NULL, NULL, NULL, 'major', 'يُمنع في الحمل لأنه قد يسبب تشوهات وتضررًا في كلى الجنين.'),
(21, 10, 1, 0, NULL, NULL, NULL, 'major', 'قد يسبب تضيقًا في القصبات الهوائية ويُتجنب عند مرضى الربو.'),
(22, 10, NULL, 1, NULL, NULL, NULL, 'moderate', 'قد يؤثر في نمو الجنين، ويُستخدم عند الضرورة فقط.'),
(23, 11, 3, 0, NULL, NULL, NULL, 'major', 'يُمنع عند وجود مرض كبدي نشط أو ارتفاع غير مفسر في إنزيمات الكبد.'),
(24, 11, NULL, 1, NULL, NULL, NULL, 'major', 'يُمنع في الحمل والإرضاع.'),
(25, 1, NULL, 1, NULL, NULL, NULL, 'major', 'يسبب تشوهات جنينية ونزفًا، ويُمنع خاصة في الثلث الأول.'),
(26, 1, 4, 0, NULL, NULL, NULL, 'major', 'يزيد خطر النزف الهضمي الخطير عند وجود قرحة.'),
(27, 13, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُتجنب في الحمل ما لم تتوفر بدائل أكثر أمانًا.'),
(28, 13, NULL, 0, 0, 17, NULL, 'moderate', 'يُتجنب عند الأطفال لخطر التأثير في الغضاريف والأوتار إلا للضرورة.'),
(29, 13, 9, 0, NULL, NULL, NULL, 'moderate', 'قد يخفض عتبة التشنج ويحرض النوبات.'),
(30, 12, 3, 0, NULL, NULL, NULL, 'moderate', 'يلزم الحذر وتعديل الجرعة عند ضعف وظائف الكبد.'),
(31, 12, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُتجنب في الحمل ما لم تكن الفائدة أكبر من الخطر.'),
(32, 12, 8, 0, NULL, NULL, NULL, 'major', 'قد يطيل فترة QT ويحرض اضطرابات خطيرة في نظم القلب.'),
(33, 14, 11, 0, NULL, NULL, NULL, 'major', 'يُمنع عند وجود حساسية من البنسلين لخطر التفاعل التحسسي الشديد.'),
(34, 15, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُتجنب في الثلث الأول من الحمل إلا للضرورة.'),
(35, 15, 3, 0, NULL, NULL, NULL, 'moderate', 'يلزم خفض الجرعة عند ضعف الكبد الشديد.'),
(36, 17, 2, 0, NULL, NULL, NULL, 'moderate', 'يلزم خفض الجرعة ومراقبة مستوى الدواء في الدم.'),
(37, 17, 8, 0, NULL, NULL, NULL, 'moderate', 'يُستخدم بحذر ويلزم مراقبة تخطيط القلب.'),
(38, 18, 10, 0, NULL, NULL, NULL, 'moderate', 'قد يرفع حمض اليوريك ويحرض نوبات النقرس.'),
(39, 19, 2, 0, NULL, NULL, NULL, 'major', 'يزداد خطر ارتفاع البوتاسيوم الخطير.'),
(40, 20, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُتجنب في الحمل، خاصة بالجرعات العالية.'),
(41, 20, 3, 0, NULL, NULL, NULL, 'moderate', 'قد يسبب سمّية كبدية ويلزم الحذر.'),
(42, 21, NULL, 1, NULL, NULL, NULL, 'moderate', 'يُستخدم في الثلث الأول من الحمل عند عدم توفر بديل فقط.'),
(43, 21, 8, 0, NULL, NULL, NULL, 'major', 'يُتجنب لدى من لديهم إطالة في فترة QT أو اضطراب نظم القلب.');

-- ----------------------------
-- Table `drug_interactions`
-- ----------------------------
DROP TABLE IF EXISTS `drug_interactions`;
CREATE TABLE "drug_interactions" (
  "interaction_id" int NOT NULL AUTO_INCREMENT,
  "drug_1_id" int NOT NULL,
  "drug_2_id" int NOT NULL,
  "severity" enum('minor','moderate','major') COLLATE utf8mb4_unicode_ci NOT NULL,
  "description" text COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY ("interaction_id"),
  KEY "fk_interaction_drug1" ("drug_1_id"),
  KEY "fk_interaction_drug2" ("drug_2_id"),
  CONSTRAINT "fk_interaction_drug1" FOREIGN KEY ("drug_1_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_interaction_drug2" FOREIGN KEY ("drug_2_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `drug_interactions` (`interaction_id`, `drug_1_id`, `drug_2_id`, `severity`, `description`) VALUES
(1, 1, 2, 'major', 'يزداد خطر النزف بشكل كبير عند الجمع بينهما، فالأسبرين يثبط الصفائح الدموية ويهيج المعدة والوارفارين يضعف التخثر. يُتجنب الجمع إلا بإشراف طبي.'),
(2, 1, 3, 'major', 'يرفع الإيبوبروفين خطر النزف الهضمي عند مرضى الوارفارين. يُفضل استخدام الباراسيتامول بديلًا.'),
(3, 1, 4, 'major', 'يزيد الديكلوفيناك خطر النزف الهضمي عند تناوله مع الوارفارين. يُنصح بتجنب الجمع.'),
(4, 1, 15, 'major', 'يثبط الميترونيدازول استقلاب الوارفارين فيرتفع INR ويزداد خطر النزف. يلزم تعديل الجرعة ومراقبة INR.'),
(5, 1, 20, 'major', 'يرفع الفلوكونازول مستوى الوارفارين في الدم ويزيد خطر النزف. يلزم مراقبة INR عن قرب.'),
(6, 1, 12, 'major', 'يزيد الكلاريثروميسين من تأثير الوارفارين المضاد للتخثر ويرفع خطر النزف.'),
(7, 1, 13, 'moderate', 'قد يزيد السيبروفلوكساسين من تأثير الوارفارين، لذا يُنصح بمراقبة INR أثناء العلاج.'),
(8, 1, 5, 'moderate', 'الاستعمال المنتظم لجرعات عالية من الباراسيتامول قد يرفع INR عند مرضى الوارفارين.'),
(9, 11, 12, 'major', 'يرفع الكلاريثروميسين مستوى السيمفاستاتين في الدم فيزداد خطر انحلال العضلات المخطط. يُوقف السيمفاستاتين مؤقتًا أثناء العلاج.'),
(10, 11, 8, 'moderate', 'يرتفع مستوى السيمفاستاتين عند تناوله مع الأملوديبين، ويُنصح بألا تتجاوز جرعة السيمفاستاتين 20 ملغ يوميًا.'),
(11, 17, 12, 'major', 'يرفع الكلاريثروميسين مستوى الديجوكسين في الدم وقد يسبب تسممًا بالديجوكسين.'),
(12, 17, 18, 'moderate', 'قد يسبب الفيوروسيميد نقصًا في البوتاسيوم مما يزيد سمّية الديجوكسين على القلب.'),
(13, 9, 19, 'major', 'يزيد الجمع بينهما خطر ارتفاع البوتاسيوم في الدم ارتفاعًا خطيرًا، ويلزم فحص البوتاسيوم ووظائف الكلى بانتظام.'),
(14, 9, 3, 'moderate', 'يقلل الإيبوبروفين من التأثير الخافض للضغط ويزيد خطر تضرر الكلى.'),
(15, 9, 4, 'moderate', 'قد يضعف الديكلوفيناك تأثير الإينالابريل ويزيد الضغط على الكلى.'),
(16, 18, 3, 'moderate', 'قد يضعف الإيبوبروفين تأثير الفيوروسيميد المدر للبول ويزيد خطر تضرر الكلى.'),
(17, 19, 3, 'moderate', 'قد يرفع الجمع بينهما البوتاسيوم ويضعف التأثير المدر للبول.'),
(18, 6, 13, 'moderate', 'قد يسبب السيبروفلوكساسين اضطرابًا في سكر الدم عند مرضى السكري الذين يتناولون الميتفورمين.'),
(19, 6, 18, 'minor', 'قد يرتفع مستوى الميتفورمين قليلًا عند تناوله مع الفيوروسيميد، وغالبًا لا يستدعي تغيير العلاج.'),
(20, 7, 20, 'major', 'يرفع الفلوكونازول مستوى الغليبنكلاميد فيزداد خطر هبوط سكر الدم الشديد.'),
(21, 7, 13, 'moderate', 'قد يسبب الجمع بينهما هبوطًا في سكر الدم، ويُنصح بمراقبة مستوى السكر.'),
(22, 10, 8, 'minor', 'يُستخدمان معًا أحيانًا لضبط الضغط، وقد يحدث انخفاض إضافي في الضغط أو بطء في النبض.'),
(23, 10, 3, 'moderate', 'قد يقلل الإيبوبروفين من التأثير الخافض للضغط لدى مرضى الأتينولول.'),
(24, 2, 3, 'moderate', 'قد يتعارض الإيبوبروفين مع التأثير الواقي للقلب الذي يوفره الأسبرين ويزيد خطر النزف الهضمي.'),
(25, 2, 4, 'moderate', 'يزيد الجمع بينهما خطر القرحة والنزف الهضمي دون فائدة علاجية إضافية.'),
(26, 12, 8, 'moderate', 'يرفع الكلاريثروميسين مستوى الأملوديبين فقد ينخفض الضغط انخفاضًا زائدًا.'),
(27, 12, 16, 'minor', 'يرتفع مستوى كل من الدوائين قليلًا، وغالبًا لا يستدعي تعديل الجرعة.'),
(28, 21, 12, 'major', 'يزيد الجمع بينهما خطر إطالة فترة QT واضطراب نظم القلب، كما يرتفع مستوى دواء الملاريا في الدم.'),
(29, 21, 20, 'moderate', 'قد يزيد الجمع بينهما خطر إطالة فترة QT، ويُنصح بمراقبة نظم القلب.'),
(30, 21, 13, 'moderate', 'قد يؤدي الجمع بينهما إلى إطالة فترة QT، لذا يُستخدم بحذر.');

-- ----------------------------
-- Table `health_conditions`
-- ----------------------------
DROP TABLE IF EXISTS `health_conditions`;
CREATE TABLE "health_conditions" (
  "id" int NOT NULL AUTO_INCREMENT,
  "condition_name" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "condition_description" text COLLATE utf8mb4_unicode_ci,
  "condition_category" varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY ("id")
);

INSERT INTO `health_conditions` (`id`, `condition_name`, `condition_description`, `condition_category`) VALUES
(1, 'الربو القصبي', 'مرض مزمن يصيب المجاري التنفسية ويسبب نوبات من ضيق التنفس والصفير.', 'أمراض الجهاز التنفسي'),
(2, 'أمراض الكلى', 'ضعف في وظائف الكلى وتراجع تدريجي في قدرتها على تصفية الدم.', 'الكلى'),
(3, 'أمراض الكبد', 'اضطرابات تؤثر في وظائف الكبد مثل التهاب الكبد والتليف.', 'أمراض الجهاز الهضمي'),
(4, 'قرحة المعدة', 'تقرحات في بطانة المعدة أو الاثني عشر.', 'أمراض الجهاز الهضمي'),
(5, 'ارتفاع ضغط الدم', 'ارتفاع مستمر في ضغط الدم الشرياني.', 'أمراض القلب والأوعية الدموية'),
(6, 'داء السكري', 'اضطراب مزمن في استقلاب السكر بسبب نقص الإنسولين أو مقاومته.', 'الأمراض الاستقلابية'),
(7, 'قصور القلب', 'عجز القلب عن ضخ الدم بكفاءة لتلبية حاجة الجسم.', 'أمراض القلب والأوعية الدموية'),
(8, 'اضطراب نظم القلب', 'عدم انتظام في ضربات القلب أو سرعتها.', 'أمراض القلب والأوعية الدموية'),
(9, 'الصرع', 'اضطراب عصبي مزمن يتميز بنوبات تشنجية متكررة.', 'أمراض الجهاز العصبي'),
(10, 'النقرس', 'التهاب مفصلي ناتج عن ارتفاع حمض اليوريك في الدم.', 'أمراض المفاصل'),
(11, 'الحساسية من البنسلين', 'تفاعل تحسسي تجاه البنسلين ومشتقاته.', 'الحساسية'),
(12, 'فقر الدم المنجلي', 'اضطراب وراثي في كريات الدم الحمراء.', 'أمراض الدم');

-- ----------------------------
-- Table `interaction_checks`
-- ----------------------------
DROP TABLE IF EXISTS `interaction_checks`;
CREATE TABLE "interaction_checks" (
  "check_id" int NOT NULL AUTO_INCREMENT,
  "check_date" datetime NOT NULL,
  "user_id" int DEFAULT NULL,
  "patient_id" int DEFAULT NULL,
  PRIMARY KEY ("check_id"),
  KEY "fk_checks_user" ("user_id"),
  KEY "fk_checks_patient" ("patient_id"),
  CONSTRAINT "fk_checks_patient" FOREIGN KEY ("patient_id") REFERENCES "patients" ("patient_id") ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT "fk_checks_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO `interaction_checks` (`check_id`, `check_date`, `user_id`, `patient_id`) VALUES
(1, '2026-10-18 17:09:16', 7, 1),
(2, '2026-10-18 20:31:07', 8, NULL),
(3, '2026-10-18 20:31:11', 8, NULL),
(4, '2026-10-18 20:31:15', 8, NULL),
(5, '2026-10-18 20:31:19', 8, NULL),
(6, '2026-10-18 20:31:23', 8, NULL),
(7, '2026-10-18 20:31:28', 8, NULL),
(8, '2026-10-18 20:31:32', 8, NULL),
(9, '2026-10-18 20:32:00', 8, NULL);

-- ----------------------------
-- Table `interaction_conditions`
-- ----------------------------
DROP TABLE IF EXISTS `interaction_conditions`;
CREATE TABLE "interaction_conditions" (
  "condition_id" int NOT NULL,
  "interaction_check_id" int NOT NULL,
  "notes" text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY ("condition_id","interaction_check_id"),
  KEY "fk_int_cond_check" ("interaction_check_id"),
  CONSTRAINT "fk_int_cond_check" FOREIGN KEY ("interaction_check_id") REFERENCES "interaction_checks" ("check_id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_int_cond_condition" FOREIGN KEY ("condition_id") REFERENCES "health_conditions" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);


-- ----------------------------
-- Table `med_associated`
-- ----------------------------
DROP TABLE IF EXISTS `med_associated`;
CREATE TABLE "med_associated" (
  "medicine_id" int NOT NULL,
  "associated_symptom_id" int NOT NULL,
  PRIMARY KEY ("medicine_id","associated_symptom_id"),
  KEY "fk_med_assoc_sym" ("associated_symptom_id"),
  CONSTRAINT "fk_med_assoc_med" FOREIGN KEY ("medicine_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_med_assoc_sym" FOREIGN KEY ("associated_symptom_id") REFERENCES "associated_symptoms" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `med_associated` (`medicine_id`, `associated_symptom_id`) VALUES
(4, 1),
(17, 1),
(6, 2),
(10, 2),
(14, 2),
(5, 3),
(12, 3),
(20, 3),
(1, 4),
(2, 4),
(3, 4),
(4, 4),
(1, 5),
(2, 5),
(8, 6),
(12, 6),
(13, 6),
(17, 6),
(19, 6),
(20, 6),
(21, 6),
(7, 7),
(6, 8),
(11, 8),
(13, 8),
(16, 8),
(18, 8),
(19, 8),
(5, 9),
(11, 9),
(15, 9),
(9, 10),
(14, 10),
(7, 11),
(8, 11),
(9, 11),
(10, 11),
(17, 11),
(21, 11),
(3, 12),
(18, 12);

-- ----------------------------
-- Table `medications`
-- ----------------------------
DROP TABLE IF EXISTS `medications`;
CREATE TABLE "medications" (
  "id" int NOT NULL AUTO_INCREMENT,
  "scientific_name" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "trade_name" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "dosage_form" varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "concentration" varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "dosage" varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "warning" text COLLATE utf8mb4_unicode_ci,
  "classification_id" int DEFAULT NULL,
  PRIMARY KEY ("id"),
  KEY "fk_med_classification" ("classification_id"),
  CONSTRAINT "fk_med_classification" FOREIGN KEY ("classification_id") REFERENCES "drug_classification" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO `medications` (`id`, `scientific_name`, `trade_name`, `dosage_form`, `concentration`, `dosage`, `warning`, `classification_id`) VALUES
(1, 'Warfarin', 'Coumadin', 'أقراص', '5 mg', 'حسب قيمة INR', 'دواء ضيق المدى العلاجي، ويلزم متابعة INR بانتظام وتجنب تغيير الجرعة دون استشارة الطبيب.', 1),
(2, 'Aspirin', 'Aspirin', 'أقراص', '100 mg', 'قرص واحد يوميًا', 'يزيد خطر النزف وتهيج المعدة، ولا يُعطى للأطفال دون 16 سنة إلا بإشراف طبي.', 2),
(3, 'Ibuprofen', 'Brufen', 'أقراص', '400 mg', 'قرص كل 8 ساعات', 'يؤخذ بعد الطعام، ويُتجنب عند مرضى القرحة والكلى والحمل المتأخر.', 2),
(4, 'Diclofenac', 'Voltaren', 'أقراص', '50 mg', 'قرص مرتين إلى ثلاث يوميًا', 'يزيد خطر النزف الهضمي والأحداث القلبية، ويُستخدم بأقل جرعة ولأقصر مدة.', 2),
(5, 'Paracetamol', 'Panadol', 'أقراص', '500 mg', 'قرصان كل 6 ساعات بحد أقصى 4 غرامات يوميًا', 'تجاوز الجرعة القصوى يسبب تلفًا خطيرًا في الكبد.', 3),
(6, 'Metformin', 'Glucophage', 'أقراص', '500 mg', 'قرص مرتين يوميًا مع الطعام', 'يُوقف قبل الفحوص الظليلة، ويُتجنب عند قصور الكلى الشديد.', 4),
(7, 'Glibenclamide', 'Daonil', 'أقراص', '5 mg', 'قرص قبل الإفطار', 'قد يسبب هبوطًا حادًا في سكر الدم، خاصة عند كبار السن أو عند تخطي الوجبات.', 4),
(8, 'Amlodipine', 'Norvasc', 'أقراص', '5 mg', 'قرص واحد يوميًا', 'قد يسبب تورم الكاحلين ودوخة عند بدء العلاج.', 5),
(9, 'Enalapril', 'Renitec', 'أقراص', '10 mg', 'قرص واحد أو قرصان يوميًا', 'يُمنع في الحمل، وقد يسبب سعالًا جافًا وارتفاعًا في البوتاسيوم.', 6),
(10, 'Atenolol', 'Tenormin', 'أقراص', '50 mg', 'قرص واحد يوميًا', 'لا يُوقف فجأة، ويُتجنب عند مرضى الربو.', 7),
(11, 'Simvastatin', 'Zocor', 'أقراص', '20 mg', 'قرص مساءً', 'قد يسبب ألمًا عضليًا وتضررًا في الكبد، ويُمنع في الحمل.', 8),
(12, 'Clarithromycin', 'Klacid', 'أقراص', '500 mg', 'قرص كل 12 ساعة', 'يتداخل مع عدد كبير من الأدوية عبر تثبيط إنزيمات الكبد.', 9),
(13, 'Ciprofloxacin', 'Ciprobay', 'أقراص', '500 mg', 'قرص كل 12 ساعة', 'قد يسبب التهاب الأوتار، ولا يُنصح به للأطفال والحوامل إلا للضرورة.', 9),
(14, 'Amoxicillin', 'Amoxil', 'كبسولات', '500 mg', 'كبسولة كل 8 ساعات', 'يُمنع عند من لديهم حساسية من البنسلين.', 9),
(15, 'Metronidazole', 'Flagyl', 'أقراص', '500 mg', 'قرص كل 8 ساعات', 'يُمنع تناول الكحول أثناء العلاج وبعده بـ 48 ساعة.', 9),
(16, 'Omeprazole', 'Losec', 'كبسولات', '20 mg', 'كبسولة قبل الفطور', 'الاستعمال الطويل قد يقلل امتصاص المغنيسيوم وفيتامين B12.', 10),
(17, 'Digoxin', 'Lanoxin', 'أقراص', '0.25 mg', 'حسب توجيه الطبيب', 'دواء ضيق المدى العلاجي، ويلزم مراقبة مستواه في الدم ومستوى البوتاسيوم.', 11),
(18, 'Furosemide', 'Lasix', 'أقراص', '40 mg', 'قرص صباحًا', 'قد يسبب جفافًا وانخفاضًا في البوتاسيوم.', 12),
(19, 'Spironolactone', 'Aldactone', 'أقراص', '25 mg', 'قرص واحد يوميًا', 'يرفع البوتاسيوم في الدم، ويلزم الحذر عند قصور الكلى.', 12),
(20, 'Fluconazole', 'Diflucan', 'كبسولات', '150 mg', 'كبسولة واحدة أو حسب الحالة', 'يتداخل مع أدوية كثيرة ويطيل فترة QT في بعض الحالات.', 13),
(21, 'Artemether-Lumefantrine', 'Coartem', 'أقراص', '20/120 mg', 'ست جرعات خلال ثلاثة أيام', 'يُؤخذ مع وجبة دسمة، ويُتجنب مع الأدوية المطيلة لفترة QT.', 14);

-- ----------------------------
-- Table `medicine_sideeffects`
-- ----------------------------
DROP TABLE IF EXISTS `medicine_sideeffects`;
CREATE TABLE "medicine_sideeffects" (
  "medicine_id" int NOT NULL,
  "side_effect_id" int NOT NULL,
  PRIMARY KEY ("medicine_id","side_effect_id"),
  KEY "fk_med_side_effect" ("side_effect_id"),
  CONSTRAINT "fk_med_side_effect" FOREIGN KEY ("side_effect_id") REFERENCES "side_effects" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_med_side_med" FOREIGN KEY ("medicine_id") REFERENCES "medications" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `medicine_sideeffects` (`medicine_id`, `side_effect_id`) VALUES
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(12, 1),
(13, 1),
(15, 1),
(17, 1),
(19, 1),
(20, 1),
(17, 2),
(21, 2),
(6, 3),
(12, 3),
(13, 3),
(14, 3),
(16, 3),
(4, 4),
(8, 4),
(11, 4),
(13, 4),
(15, 4),
(16, 4),
(20, 4),
(21, 4),
(3, 5),
(8, 5),
(9, 5),
(10, 5),
(13, 5),
(18, 5),
(19, 5),
(21, 5),
(10, 6),
(2, 7),
(3, 7),
(4, 7),
(16, 7),
(4, 8),
(7, 8),
(14, 8),
(20, 8),
(9, 9),
(6, 10),
(12, 10),
(15, 10),
(8, 11),
(10, 12),
(17, 12),
(11, 13),
(18, 13),
(7, 14),
(9, 15),
(19, 15),
(1, 16),
(2, 16),
(12, 17),
(17, 17),
(21, 17),
(5, 18),
(11, 18),
(20, 18),
(14, 19);

-- ----------------------------
-- Table `password_resets`
-- ----------------------------
DROP TABLE IF EXISTS `password_resets`;
CREATE TABLE "password_resets" (
  "id" int NOT NULL AUTO_INCREMENT,
  "user_id" int NOT NULL,
  "code_hash" varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  "expires_at" datetime NOT NULL,
  "attempts" int NOT NULL DEFAULT '0',
  "used" tinyint(1) NOT NULL DEFAULT '0',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  KEY "fk_pr_user" ("user_id"),
  CONSTRAINT "fk_pr_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `password_resets` (`id`, `user_id`, `code_hash`, `expires_at`, `attempts`, `used`, `created_at`) VALUES
(1, 2, '2fe92ae64027abe77d3324159e6831a611e53aaf3eee6a11453239d57b448071', '2026-10-17 01:17:26', 0, 0, '2026-10-17 01:07:26'),
(2, 7, '5bbc9f751c19f9c6bb70e0c7b30e4a31b8475213e3f968debb847afe9b8bd1ab', '2026-10-18 17:19:50', 0, 1, '2026-10-18 17:09:50'),
(3, 7, '5b9446e0f3b038d41b379ba2d9e90c680f02f6252c8113b1a7bc5e6ca42bde14', '2026-10-18 17:21:05', 0, 1, '2026-10-18 17:11:05'),
(4, 7, '480298369324c6758d6a39a8127861918fc89ede3415e8bf5c72359acebe56d4', '2026-10-18 17:22:20', 0, 1, '2026-10-18 17:12:20'),
(5, 7, 'f7e80af8b1d62d3db4ea015027ddc8da8bbb9339211424f9cb0a1abe366d5457', '2026-10-18 17:24:19', 0, 0, '2026-10-18 17:14:20'),
(6, 8, 'bcac9bd70f45a52912d1c2e7176f308bb13b9517e3d9bd4bc89ea48fea244956', '2026-10-18 20:43:38', 0, 0, '2026-10-18 20:33:39');

-- ----------------------------
-- Table `patient_conditions`
-- ----------------------------
DROP TABLE IF EXISTS `patient_conditions`;
CREATE TABLE "patient_conditions" (
  "patient_id" int NOT NULL,
  "condition_id" int NOT NULL,
  "notes" text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY ("patient_id","condition_id"),
  KEY "fk_pat_cond_condition" ("condition_id"),
  CONSTRAINT "fk_pat_cond_condition" FOREIGN KEY ("condition_id") REFERENCES "health_conditions" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_pat_cond_patient" FOREIGN KEY ("patient_id") REFERENCES "patients" ("patient_id") ON DELETE CASCADE ON UPDATE CASCADE
);


-- ----------------------------
-- Table `patients`
-- ----------------------------
DROP TABLE IF EXISTS `patients`;
CREATE TABLE "patients" (
  "patient_id" int NOT NULL AUTO_INCREMENT,
  "name" varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "age" int NOT NULL,
  "is_pregnant" tinyint(1) DEFAULT '0',
  "gender" varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "user_id" int DEFAULT NULL,
  PRIMARY KEY ("patient_id"),
  KEY "fk_patients_user" ("user_id"),
  CONSTRAINT "fk_patients_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO `patients` (`patient_id`, `name`, `age`, `is_pregnant`, `gender`, `user_id`) VALUES
(1, NULL, 24, 0, NULL, 7);

-- ----------------------------
-- Table `pharmacists`
-- ----------------------------
DROP TABLE IF EXISTS `pharmacists`;
CREATE TABLE "pharmacists" (
  "pharmacist_id" int NOT NULL AUTO_INCREMENT,
  "license_number" varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  "name" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "phone_number" varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  "user_id" int DEFAULT NULL,
  PRIMARY KEY ("pharmacist_id"),
  UNIQUE KEY "uq_pharmacists_user" ("user_id"),
  CONSTRAINT "fk_pharmacists_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);


-- ----------------------------
-- Table `player_attempts`
-- ----------------------------
DROP TABLE IF EXISTS `player_attempts`;
CREATE TABLE "player_attempts" (
  "attempt_id" int NOT NULL AUTO_INCREMENT,
  "player_id" int NOT NULL,
  "question_id" int NOT NULL,
  "selected_option" enum('A','B','C','D') COLLATE utf8mb4_unicode_ci NOT NULL,
  "is_correct" tinyint(1) NOT NULL,
  "attempted_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("attempt_id"),
  KEY "fk_attempt_player" ("player_id"),
  KEY "fk_attempt_question" ("question_id"),
  CONSTRAINT "fk_attempt_player" FOREIGN KEY ("player_id") REFERENCES "players" ("player_id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_attempt_question" FOREIGN KEY ("question_id") REFERENCES "questions" ("question_id") ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `player_attempts` (`attempt_id`, `player_id`, `question_id`, `selected_option`, `is_correct`, `attempted_at`) VALUES
(1, 1, 15, 'B', 0, '2026-10-17 01:01:32'),
(2, 1, 84, 'C', 1, '2026-10-17 01:01:45'),
(3, 2, 84, 'C', 1, '2026-10-17 01:45:08'),
(4, 2, 80, 'A', 1, '2026-10-17 01:45:55'),
(5, 2, 49, 'B', 1, '2026-10-17 01:46:26'),
(6, 2, 33, 'D', 0, '2026-10-17 01:46:46'),
(7, 2, 57, 'B', 0, '2026-10-17 01:47:08'),
(8, 2, 27, 'C', 0, '2026-10-17 01:47:26'),
(9, 2, 15, 'B', 0, '2026-10-17 01:47:42'),
(10, 2, 58, 'B', 0, '2026-10-17 01:47:58'),
(11, 2, 77, 'D', 0, '2026-10-17 01:48:10'),
(12, 2, 75, 'D', 0, '2026-10-17 01:48:25');

-- ----------------------------
-- Table `players`
-- ----------------------------
DROP TABLE IF EXISTS `players`;
CREATE TABLE "players" (
  "player_id" int NOT NULL AUTO_INCREMENT,
  "username" varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  "email" varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "total_score" int DEFAULT '0',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "user_id" int DEFAULT NULL,
  PRIMARY KEY ("player_id"),
  UNIQUE KEY "uq_players_user" ("user_id"),
  CONSTRAINT "fk_players_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO `players` (`player_id`, `username`, `email`, `total_score`, `created_at`, `user_id`) VALUES
(1, 'Pharmacist', 'Pharmacist@gmail.com', 10, '2026-10-17 01:00:48', 3),
(2, 'خرباش', 'khrpashmusabahmed@gmail.com', 30, '2026-10-17 01:44:14', 6);

-- ----------------------------
-- Table `questions`
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE "questions" (
  "question_id" int NOT NULL AUTO_INCREMENT,
  "question_text" text COLLATE utf8mb4_unicode_ci NOT NULL,
  "option_a" varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  "option_b" varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  "option_c" varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  "option_d" varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "correct_option" enum('A','B','C','D') COLLATE utf8mb4_unicode_ci NOT NULL,
  "difficulty" varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Medium',
  "interaction_id" int DEFAULT NULL,
  "source_key" varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY ("question_id"),
  UNIQUE KEY "uq_questions_source_key" ("source_key"),
  KEY "fk_questions_interaction" ("interaction_id"),
  CONSTRAINT "fk_questions_interaction" FOREIGN KEY ("interaction_id") REFERENCES "drug_interactions" ("interaction_id") ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO `questions` (`question_id`, `question_text`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `difficulty`, `interaction_id`, `source_key`) VALUES
(1, 'ما درجة خطورة التداخل الدوائي بين Warfarin وAspirin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i1:sev'),
(2, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Digoxin', 'Aspirin', 'Metformin', 'Artemether-Lumefantrine', 'B', 'Hard', NULL, 'i1:t1'),
(3, 'أي من الأدوية التالية له تداخل مسجّل مع Aspirin؟', 'Fluconazole', 'Warfarin', 'Ciprofloxacin', 'Simvastatin', 'B', 'Hard', NULL, 'i1:t2'),
(4, 'ما درجة خطورة التداخل الدوائي بين Warfarin وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i2:sev'),
(5, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Glibenclamide', 'Spironolactone', 'Ibuprofen', 'Simvastatin', 'C', 'Hard', NULL, 'i2:t1'),
(6, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Warfarin', 'Glibenclamide', 'Artemether-Lumefantrine', 'Diclofenac', 'A', 'Hard', NULL, 'i2:t2'),
(7, 'ما درجة خطورة التداخل الدوائي بين Warfarin وDiclofenac؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i3:sev'),
(8, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Amlodipine', 'Simvastatin', 'Metformin', 'Diclofenac', 'D', 'Hard', NULL, 'i3:t1'),
(9, 'أي من الأدوية التالية له تداخل مسجّل مع Diclofenac؟', 'Clarithromycin', 'Warfarin', 'Spironolactone', 'Simvastatin', 'B', 'Hard', NULL, 'i3:t2'),
(10, 'ما درجة خطورة التداخل الدوائي بين Warfarin وMetronidazole؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i4:sev'),
(11, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Amoxicillin', 'Spironolactone', 'Metronidazole', 'Glibenclamide', 'C', 'Hard', NULL, 'i4:t1'),
(12, 'أي من الأدوية التالية له تداخل مسجّل مع Metronidazole؟', 'Aspirin', 'Simvastatin', 'Warfarin', 'Digoxin', 'C', 'Hard', NULL, 'i4:t2'),
(13, 'ما درجة خطورة التداخل الدوائي بين Warfarin وFluconazole؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i5:sev'),
(14, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Simvastatin', 'Fluconazole', 'Omeprazole', 'Digoxin', 'B', 'Hard', NULL, 'i5:t1'),
(15, 'أي من الأدوية التالية له تداخل مسجّل مع Fluconazole؟', 'Diclofenac', 'Amlodipine', 'Paracetamol', 'Warfarin', 'D', 'Hard', NULL, 'i5:t2'),
(16, 'ما درجة خطورة التداخل الدوائي بين Warfarin وClarithromycin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i6:sev'),
(17, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Metformin', 'Artemether-Lumefantrine', 'Clarithromycin', 'Atenolol', 'C', 'Hard', NULL, 'i6:t1'),
(18, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Warfarin', 'Atenolol', 'Paracetamol', 'Fluconazole', 'A', 'Hard', NULL, 'i6:t2'),
(19, 'ما درجة خطورة التداخل الدوائي بين Warfarin وCiprofloxacin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i7:sev'),
(20, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Glibenclamide', 'Ciprofloxacin', 'Metformin', 'Enalapril', 'B', 'Hard', NULL, 'i7:t1'),
(21, 'أي من الأدوية التالية له تداخل مسجّل مع Ciprofloxacin؟', 'Amlodipine', 'Digoxin', 'Metronidazole', 'Warfarin', 'D', 'Hard', NULL, 'i7:t2'),
(22, 'ما درجة خطورة التداخل الدوائي بين Warfarin وParacetamol؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i8:sev'),
(23, 'أي من الأدوية التالية له تداخل مسجّل مع Warfarin؟', 'Enalapril', 'Metformin', 'Paracetamol', 'Atenolol', 'C', 'Hard', NULL, 'i8:t1'),
(24, 'أي من الأدوية التالية له تداخل مسجّل مع Paracetamol؟', 'Amlodipine', 'Metformin', 'Fluconazole', 'Warfarin', 'D', 'Hard', NULL, 'i8:t2'),
(25, 'ما درجة خطورة التداخل الدوائي بين Simvastatin وClarithromycin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i9:sev'),
(26, 'أي من الأدوية التالية له تداخل مسجّل مع Simvastatin؟', 'Clarithromycin', 'Amoxicillin', 'Furosemide', 'Enalapril', 'A', 'Hard', NULL, 'i9:t1'),
(27, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Furosemide', 'Simvastatin', 'Amoxicillin', 'Ibuprofen', 'B', 'Hard', NULL, 'i9:t2'),
(28, 'ما درجة خطورة التداخل الدوائي بين Simvastatin وAmlodipine؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i10:sev'),
(29, 'أي من الأدوية التالية له تداخل مسجّل مع Simvastatin؟', 'Warfarin', 'Amlodipine', 'Ibuprofen', 'Paracetamol', 'B', 'Hard', NULL, 'i10:t1'),
(30, 'أي من الأدوية التالية له تداخل مسجّل مع Amlodipine؟', 'Fluconazole', 'Simvastatin', 'Metformin', 'Artemether-Lumefantrine', 'B', 'Hard', NULL, 'i10:t2'),
(31, 'ما درجة خطورة التداخل الدوائي بين Digoxin وClarithromycin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i11:sev'),
(32, 'أي من الأدوية التالية له تداخل مسجّل مع Digoxin؟', 'Aspirin', 'Metronidazole', 'Clarithromycin', 'Paracetamol', 'C', 'Hard', NULL, 'i11:t1'),
(33, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Enalapril', 'Digoxin', 'Atenolol', 'Diclofenac', 'B', 'Hard', NULL, 'i11:t2'),
(34, 'ما درجة خطورة التداخل الدوائي بين Digoxin وFurosemide؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i12:sev'),
(35, 'أي من الأدوية التالية له تداخل مسجّل مع Digoxin؟', 'Simvastatin', 'Fluconazole', 'Metronidazole', 'Furosemide', 'D', 'Hard', NULL, 'i12:t1'),
(36, 'أي من الأدوية التالية له تداخل مسجّل مع Furosemide؟', 'Metronidazole', 'Atenolol', 'Amlodipine', 'Digoxin', 'D', 'Hard', NULL, 'i12:t2'),
(37, 'ما درجة خطورة التداخل الدوائي بين Enalapril وSpironolactone؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i13:sev'),
(38, 'أي من الأدوية التالية له تداخل مسجّل مع Enalapril؟', 'Spironolactone', 'Fluconazole', 'Artemether-Lumefantrine', 'Metronidazole', 'A', 'Hard', NULL, 'i13:t1'),
(39, 'أي من الأدوية التالية له تداخل مسجّل مع Spironolactone؟', 'Metformin', 'Enalapril', 'Simvastatin', 'Ciprofloxacin', 'B', 'Hard', NULL, 'i13:t2'),
(40, 'ما درجة خطورة التداخل الدوائي بين Enalapril وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i14:sev'),
(41, 'أي من الأدوية التالية له تداخل مسجّل مع Enalapril؟', 'Ibuprofen', 'Digoxin', 'Clarithromycin', 'Amoxicillin', 'A', 'Hard', NULL, 'i14:t1'),
(42, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Amlodipine', 'Paracetamol', 'Enalapril', 'Clarithromycin', 'C', 'Hard', NULL, 'i14:t2'),
(43, 'ما درجة خطورة التداخل الدوائي بين Enalapril وDiclofenac؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i15:sev'),
(44, 'أي من الأدوية التالية له تداخل مسجّل مع Enalapril؟', 'Omeprazole', 'Diclofenac', 'Simvastatin', 'Warfarin', 'B', 'Hard', NULL, 'i15:t1'),
(45, 'أي من الأدوية التالية له تداخل مسجّل مع Diclofenac؟', 'Paracetamol', 'Enalapril', 'Simvastatin', 'Atenolol', 'B', 'Hard', NULL, 'i15:t2'),
(46, 'ما درجة خطورة التداخل الدوائي بين Furosemide وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i16:sev'),
(47, 'أي من الأدوية التالية له تداخل مسجّل مع Furosemide؟', 'Simvastatin', 'Ciprofloxacin', 'Warfarin', 'Ibuprofen', 'D', 'Hard', NULL, 'i16:t1'),
(48, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Furosemide', 'Metformin', 'Digoxin', 'Simvastatin', 'A', 'Hard', NULL, 'i16:t2'),
(49, 'ما درجة خطورة التداخل الدوائي بين Spironolactone وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i17:sev'),
(50, 'أي من الأدوية التالية له تداخل مسجّل مع Spironolactone؟', 'Warfarin', 'Metformin', 'Fluconazole', 'Ibuprofen', 'D', 'Hard', NULL, 'i17:t1'),
(51, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Metronidazole', 'Spironolactone', 'Clarithromycin', 'Omeprazole', 'B', 'Hard', NULL, 'i17:t2'),
(52, 'ما درجة خطورة التداخل الدوائي بين Metformin وCiprofloxacin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i18:sev'),
(53, 'أي من الأدوية التالية له تداخل مسجّل مع Metformin؟', 'Fluconazole', 'Paracetamol', 'Ciprofloxacin', 'Artemether-Lumefantrine', 'C', 'Hard', NULL, 'i18:t1'),
(54, 'أي من الأدوية التالية له تداخل مسجّل مع Ciprofloxacin؟', 'Diclofenac', 'Omeprazole', 'Metformin', 'Ibuprofen', 'C', 'Hard', NULL, 'i18:t2'),
(55, 'ما درجة خطورة التداخل الدوائي بين Metformin وFurosemide؟', 'بسيط', 'متوسط', 'خطير', NULL, 'A', 'Medium', NULL, 'i19:sev'),
(56, 'أي من الأدوية التالية له تداخل مسجّل مع Metformin؟', 'Furosemide', 'Aspirin', 'Diclofenac', 'Atenolol', 'A', 'Hard', NULL, 'i19:t1'),
(57, 'أي من الأدوية التالية له تداخل مسجّل مع Furosemide؟', 'Aspirin', 'Warfarin', 'Metformin', 'Glibenclamide', 'C', 'Hard', NULL, 'i19:t2'),
(58, 'ما درجة خطورة التداخل الدوائي بين Glibenclamide وFluconazole؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i20:sev'),
(59, 'أي من الأدوية التالية له تداخل مسجّل مع Glibenclamide؟', 'Fluconazole', 'Warfarin', 'Diclofenac', 'Atenolol', 'A', 'Hard', NULL, 'i20:t1'),
(60, 'أي من الأدوية التالية له تداخل مسجّل مع Fluconazole؟', 'Spironolactone', 'Glibenclamide', 'Paracetamol', 'Diclofenac', 'B', 'Hard', NULL, 'i20:t2'),
(61, 'ما درجة خطورة التداخل الدوائي بين Glibenclamide وCiprofloxacin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i21:sev'),
(62, 'أي من الأدوية التالية له تداخل مسجّل مع Glibenclamide؟', 'Ciprofloxacin', 'Metronidazole', 'Warfarin', 'Furosemide', 'A', 'Hard', NULL, 'i21:t1'),
(63, 'أي من الأدوية التالية له تداخل مسجّل مع Ciprofloxacin؟', 'Omeprazole', 'Glibenclamide', 'Enalapril', 'Spironolactone', 'B', 'Hard', NULL, 'i21:t2'),
(64, 'ما درجة خطورة التداخل الدوائي بين Atenolol وAmlodipine؟', 'بسيط', 'متوسط', 'خطير', NULL, 'A', 'Medium', NULL, 'i22:sev'),
(65, 'أي من الأدوية التالية له تداخل مسجّل مع Atenolol؟', 'Artemether-Lumefantrine', 'Omeprazole', 'Amlodipine', 'Spironolactone', 'C', 'Hard', NULL, 'i22:t1'),
(66, 'أي من الأدوية التالية له تداخل مسجّل مع Amlodipine؟', 'Furosemide', 'Fluconazole', 'Glibenclamide', 'Atenolol', 'D', 'Hard', NULL, 'i22:t2'),
(67, 'ما درجة خطورة التداخل الدوائي بين Atenolol وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i23:sev'),
(68, 'أي من الأدوية التالية له تداخل مسجّل مع Atenolol؟', 'Aspirin', 'Clarithromycin', 'Ibuprofen', 'Spironolactone', 'C', 'Hard', NULL, 'i23:t1'),
(69, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Clarithromycin', 'Atenolol', 'Glibenclamide', 'Simvastatin', 'B', 'Hard', NULL, 'i23:t2'),
(70, 'ما درجة خطورة التداخل الدوائي بين Aspirin وIbuprofen؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i24:sev'),
(71, 'أي من الأدوية التالية له تداخل مسجّل مع Aspirin؟', 'Amoxicillin', 'Spironolactone', 'Metronidazole', 'Ibuprofen', 'D', 'Hard', NULL, 'i24:t1'),
(72, 'أي من الأدوية التالية له تداخل مسجّل مع Ibuprofen؟', 'Amlodipine', 'Glibenclamide', 'Aspirin', 'Clarithromycin', 'C', 'Hard', NULL, 'i24:t2'),
(73, 'ما درجة خطورة التداخل الدوائي بين Aspirin وDiclofenac؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i25:sev'),
(74, 'أي من الأدوية التالية له تداخل مسجّل مع Aspirin؟', 'Paracetamol', 'Artemether-Lumefantrine', 'Amoxicillin', 'Diclofenac', 'D', 'Hard', NULL, 'i25:t1'),
(75, 'أي من الأدوية التالية له تداخل مسجّل مع Diclofenac؟', 'Amoxicillin', 'Spironolactone', 'Aspirin', 'Metformin', 'C', 'Hard', NULL, 'i25:t2'),
(76, 'ما درجة خطورة التداخل الدوائي بين Clarithromycin وAmlodipine؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i26:sev'),
(77, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Ibuprofen', 'Amlodipine', 'Amoxicillin', 'Spironolactone', 'B', 'Hard', NULL, 'i26:t1'),
(78, 'أي من الأدوية التالية له تداخل مسجّل مع Amlodipine؟', 'Aspirin', 'Metformin', 'Clarithromycin', 'Warfarin', 'C', 'Hard', NULL, 'i26:t2'),
(79, 'ما درجة خطورة التداخل الدوائي بين Clarithromycin وOmeprazole؟', 'بسيط', 'متوسط', 'خطير', NULL, 'A', 'Medium', NULL, 'i27:sev'),
(80, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Omeprazole', 'Ibuprofen', 'Ciprofloxacin', 'Atenolol', 'A', 'Hard', NULL, 'i27:t1'),
(81, 'أي من الأدوية التالية له تداخل مسجّل مع Omeprazole؟', 'Clarithromycin', 'Paracetamol', 'Aspirin', 'Ciprofloxacin', 'A', 'Hard', NULL, 'i27:t2'),
(82, 'ما درجة خطورة التداخل الدوائي بين Artemether-Lumefantrine وClarithromycin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'C', 'Medium', NULL, 'i28:sev'),
(83, 'أي من الأدوية التالية له تداخل مسجّل مع Artemether-Lumefantrine؟', 'Diclofenac', 'Glibenclamide', 'Clarithromycin', 'Spironolactone', 'C', 'Hard', NULL, 'i28:t1'),
(84, 'أي من الأدوية التالية له تداخل مسجّل مع Clarithromycin؟', 'Spironolactone', 'Fluconazole', 'Artemether-Lumefantrine', 'Ibuprofen', 'C', 'Hard', NULL, 'i28:t2'),
(85, 'ما درجة خطورة التداخل الدوائي بين Artemether-Lumefantrine وFluconazole؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i29:sev'),
(86, 'أي من الأدوية التالية له تداخل مسجّل مع Artemether-Lumefantrine؟', 'Paracetamol', 'Omeprazole', 'Metronidazole', 'Fluconazole', 'D', 'Hard', NULL, 'i29:t1'),
(87, 'أي من الأدوية التالية له تداخل مسجّل مع Fluconazole؟', 'Amlodipine', 'Enalapril', 'Furosemide', 'Artemether-Lumefantrine', 'D', 'Hard', NULL, 'i29:t2'),
(88, 'ما درجة خطورة التداخل الدوائي بين Artemether-Lumefantrine وCiprofloxacin؟', 'بسيط', 'متوسط', 'خطير', NULL, 'B', 'Medium', NULL, 'i30:sev'),
(89, 'أي من الأدوية التالية له تداخل مسجّل مع Artemether-Lumefantrine؟', 'Ciprofloxacin', 'Warfarin', 'Paracetamol', 'Furosemide', 'A', 'Hard', NULL, 'i30:t1'),
(90, 'أي من الأدوية التالية له تداخل مسجّل مع Ciprofloxacin؟', 'Artemether-Lumefantrine', 'Amoxicillin', 'Atenolol', 'Aspirin', 'A', 'Hard', NULL, 'i30:t2');

-- ----------------------------
-- Table `side_effects`
-- ----------------------------
DROP TABLE IF EXISTS `side_effects`;
CREATE TABLE "side_effects" (
  "id" int NOT NULL AUTO_INCREMENT,
  "name_arabic" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "name_english" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "description" text COLLATE utf8mb4_unicode_ci,
  "severity" varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY ("id")
);

INSERT INTO `side_effects` (`id`, `name_arabic`, `name_english`, `description`, `severity`) VALUES
(1, 'غثيان', 'Nausea', 'شعور بالرغبة في التقيؤ.', 'بسيط'),
(2, 'قيء', 'Vomiting', 'خروج محتويات المعدة عن طريق الفم.', 'بسيط'),
(3, 'إسهال', 'Diarrhea', 'زيادة عدد مرات التبرز مع ليونة البراز.', 'بسيط'),
(4, 'صداع', 'Headache', 'ألم في الرأس بدرجات متفاوتة.', 'بسيط'),
(5, 'دوخة', 'Dizziness', 'شعور بعدم الاتزان أو دوار.', 'بسيط'),
(6, 'نعاس', 'Drowsiness', 'ميل شديد إلى النوم وانخفاض في اليقظة.', 'بسيط'),
(7, 'ألم في المعدة', 'Stomach Pain', 'ألم أو حرقة في أعلى البطن.', 'متوسط'),
(8, 'طفح جلدي', 'Skin Rash', 'ظهور احمرار أو حكة أو بقع على الجلد.', 'متوسط'),
(9, 'سعال جاف', 'Dry Cough', 'سعال مستمر غير مصحوب ببلغم.', 'بسيط'),
(10, 'طعم معدني في الفم', 'Metallic Taste', 'إحساس بطعم معدني مزعج في الفم.', 'بسيط'),
(11, 'تورم الكاحلين', 'Ankle Edema', 'احتباس السوائل وتورم القدمين والكاحلين.', 'متوسط'),
(12, 'بطء ضربات القلب', 'Bradycardia', 'انخفاض معدل نبض القلب عن المعدل الطبيعي.', 'متوسط'),
(13, 'ألم في العضلات', 'Muscle Pain', 'ألم أو ضعف في العضلات.', 'متوسط'),
(14, 'انخفاض سكر الدم', 'Hypoglycemia', 'هبوط مستوى سكر الدم مع تعرق ورجفة وإرهاق.', 'خطير'),
(15, 'ارتفاع البوتاسيوم في الدم', 'Hyperkalemia', 'زيادة البوتاسيوم في الدم وقد تسبب اضطرابًا في نظم القلب.', 'خطير'),
(16, 'نزف', 'Bleeding', 'نزف غير طبيعي أو صعوبة في إيقاف النزف.', 'خطير'),
(17, 'اضطراب نظم القلب', 'Arrhythmia', 'عدم انتظام ضربات القلب.', 'خطير'),
(18, 'تضرر الكبد', 'Liver Damage', 'ارتفاع إنزيمات الكبد أو التهابه.', 'خطير'),
(19, 'تفاعل تحسسي شديد', 'Anaphylaxis', 'حساسية مفرطة قد تهدد الحياة وتحتاج إلى إسعاف فوري.', 'خطير');

-- ----------------------------
-- Table `user_chronic_conditions`
-- ----------------------------
DROP TABLE IF EXISTS `user_chronic_conditions`;
CREATE TABLE "user_chronic_conditions" (
  "user_id" int NOT NULL,
  "condition_id" int NOT NULL,
  PRIMARY KEY ("user_id","condition_id"),
  KEY "fk_ucc_condition" ("condition_id"),
  CONSTRAINT "fk_ucc_condition" FOREIGN KEY ("condition_id") REFERENCES "health_conditions" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_ucc_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);


-- ----------------------------
-- Table `user_health_profiles`
-- ----------------------------
DROP TABLE IF EXISTS `user_health_profiles`;
CREATE TABLE "user_health_profiles" (
  "user_id" int NOT NULL,
  "age" int DEFAULT NULL,
  "is_pregnant" tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY ("user_id"),
  CONSTRAINT "fk_uhp_user" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);


-- ----------------------------
-- Table `users`
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE "users" (
  "id" int NOT NULL AUTO_INCREMENT,
  "username" varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  "email" varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  "password" varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  "role" enum('admin','pharmacist','user') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  UNIQUE KEY "uq_users_username" ("username"),
  UNIQUE KEY "uq_users_email" ("email")
);

INSERT INTO `users` (`id`, `username`, `email`, `password`, `role`, `created_at`) VALUES
(2, 'admin', 'drugsinteractionssudan@gmail.com', 'scrypt:32768:8:1$ufgskmSA1c7Uq27W$d04a7d8bc448db475b1025dd44c437a4d9565b1d5e150eb95f164e5453b0dec434abea55f22c449c99d1feedc4cdd291534b4ad2facf1f234ac7a7a0c5ebfcab', 'admin', '2026-10-17 00:53:38'),
(3, 'Pharmacist', 'Pharmacist@gmail.com', 'scrypt:32768:8:1$pNvt4snobXhXk914$18cdf34a26868ddda71147d9aff459939c0857d77f4f9374486e59ef22905138a6efaee3ea2965e821e85122786ac32877e56bae18c28cbcf6b0702d9b644e47', 'pharmacist', '2026-10-17 00:58:51'),
(4, 'user', 'user@user', 'scrypt:32768:8:1$9qCBJ3tuOpJs1Ap5$ad31a3981a03514726651e8b611ebba817a9bd73e83f1e7829beda5d0bea8f41a3d53eb0cb7040eab9777c47cb46221e8acb2abb10f380733962240a19cc8ae4', 'user', '2026-10-17 01:11:26'),
(5, 'آدمن', 'admin@admin', 'scrypt:32768:8:1$xAj7dRJ7TsVLpqWv$df27a50abc8cb41d2b99c4ba747b06d2babd6d5ac5fdb9d7f4f947c8b7dd707cea5064d44f2c316a02e8f7e81ad8e1a1d0c1124aeaf9974c9318af165d61fbf6', 'admin', '2026-10-17 01:29:37'),
(6, 'خرباش', 'khrpashmusabahmed@gmail.com', 'scrypt:32768:8:1$6gg06Pkt3n8JKP1K$950bd20280a8c83cd8d41a9bc3f3b633884520b8d228d64dac1237e621c2f9f996286ded2133ef4a580d2abe7fbd8a8493bca75285390575fec1f72198fbe9f8', 'pharmacist', '2026-10-17 01:40:19'),
(7, 'esraa', 'esra.makawe@gmail.com', 'scrypt:32768:8:1$paQ0Bu3k5attH9SF$63880e5c122f5d8b326e4def37fd4d6dda7158f1638b4be64db834e6d801e4591e054675457ac7d5cf724486a46b6e48b4d86590371e81d99afc87b5f179a599', 'user', '2026-10-18 17:08:38'),
(8, 'ahmed_adil', 'ahmed.adil.hassan.ahmed@gmail.com', 'scrypt:32768:8:1$AGNJrA4ONXJYq3vJ$0321f885cce095577a7205c06ae3d7666ba266dca0e6814205f2e160720768a87a3cbd8df7370fb9dcdbd3f8120b51fe7bae1fa7e5916087336b8fee9fc98ae5', 'user', '2026-10-18 20:28:36');

SET FOREIGN_KEY_CHECKS=1;
