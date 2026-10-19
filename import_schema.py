import pymysql
from getpass import getpass
from urllib.parse import urlparse, unquote

STATEMENTS = [
'''SET NAMES utf8mb4''',
'''CREATE TABLE IF NOT EXISTS `associated_symptoms` ( `id` int(11) NOT NULL AUTO_INCREMENT, `name_arabic` varchar(150) NOT NULL, `name_english` varchar(150) NOT NULL, `description` text, PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `ckeck_medicines` ( `ckeck_id` int(11) NOT NULL, `drug_id` int(11) NOT NULL, PRIMARY KEY (`ckeck_id`,`drug_id`), KEY `fk_check_med_drug` (`drug_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `drug_classification` ( `id` int(11) NOT NULL AUTO_INCREMENT, `name_arabic` varchar(150) NOT NULL, `name_english` varchar(150) NOT NULL, `description` text, PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `drug_contraindications` ( `id` int(11) NOT NULL AUTO_INCREMENT, `medication_id` int(11) NOT NULL, `condition_id` int(11) DEFAULT NULL, `pregnancy_risk` tinyint(1) NOT NULL DEFAULT '0', `age_from` int(11) DEFAULT NULL, `age_to` int(11) DEFAULT NULL, `min_age` int(11) DEFAULT NULL, `severity` enum('minor','moderate','major') NOT NULL, `description` text NOT NULL, PRIMARY KEY (`id`), KEY `fk_contra_medication` (`medication_id`), KEY `fk_contra_condition` (`condition_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `drug_interactions` ( `interaction_id` int(11) NOT NULL AUTO_INCREMENT, `drug_1_id` int(11) NOT NULL, `drug_2_id` int(11) NOT NULL, `severity` enum('minor','moderate','major') NOT NULL, `description` text NOT NULL, PRIMARY KEY (`interaction_id`), KEY `fk_interaction_drug1` (`drug_1_id`), KEY `fk_interaction_drug2` (`drug_2_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `health_conditions` ( `id` int(11) NOT NULL AUTO_INCREMENT, `condition_name` varchar(150) NOT NULL, `condition_description` text, `condition_category` varchar(100) DEFAULT NULL, PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `interaction_checks` ( `check_id` int(11) NOT NULL AUTO_INCREMENT, `check_date` datetime NOT NULL, `user_id` int(11) DEFAULT NULL, `patient_id` int(11) DEFAULT NULL, PRIMARY KEY (`check_id`), KEY `fk_checks_user` (`user_id`), KEY `fk_checks_patient` (`patient_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `interaction_conditions` ( `condition_id` int(11) NOT NULL, `interaction_check_id` int(11) NOT NULL, `notes` text, PRIMARY KEY (`condition_id`,`interaction_check_id`), KEY `fk_int_cond_check` (`interaction_check_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `medications` ( `id` int(11) NOT NULL AUTO_INCREMENT, `scientific_name` varchar(150) NOT NULL, `trade_name` varchar(150) NOT NULL, `dosage_form` varchar(100) DEFAULT NULL, `concentration` varchar(100) DEFAULT NULL, `dosage` varchar(100) DEFAULT NULL, `warning` text, `classification_id` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `fk_med_classification` (`classification_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `medicine_sideeffects` ( `medicine_id` int(11) NOT NULL, `side_effect_id` int(11) NOT NULL, PRIMARY KEY (`medicine_id`,`side_effect_id`), KEY `fk_med_side_effect` (`side_effect_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `med_associated` ( `medicine_id` int(11) NOT NULL, `associated_symptom_id` int(11) NOT NULL, PRIMARY KEY (`medicine_id`,`associated_symptom_id`), KEY `fk_med_assoc_sym` (`associated_symptom_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `password_resets` ( `id` int(11) NOT NULL AUTO_INCREMENT, `user_id` int(11) NOT NULL, `code_hash` varchar(255) NOT NULL, `expires_at` datetime NOT NULL, `attempts` int(11) NOT NULL DEFAULT '0', `used` tinyint(1) NOT NULL DEFAULT '0', `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `fk_pr_user` (`user_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `patients` ( `patient_id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(150) DEFAULT NULL, `age` int(11) NOT NULL, `is_pregnant` tinyint(1) DEFAULT '0', `gender` varchar(20) DEFAULT NULL, `user_id` int(11) DEFAULT NULL, PRIMARY KEY (`patient_id`), KEY `fk_patients_user` (`user_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `patient_conditions` ( `patient_id` int(11) NOT NULL, `condition_id` int(11) NOT NULL, `notes` text, PRIMARY KEY (`patient_id`,`condition_id`), KEY `fk_pat_cond_condition` (`condition_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `pharmacists` ( `pharmacist_id` int(11) NOT NULL AUTO_INCREMENT, `license_number` varchar(100) NOT NULL, `name` varchar(150) NOT NULL, `phone_number` varchar(50) NOT NULL, `user_id` int(11) DEFAULT NULL, PRIMARY KEY (`pharmacist_id`), UNIQUE KEY `uq_pharmacists_user` (`user_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `players` ( `player_id` int(11) NOT NULL AUTO_INCREMENT, `username` varchar(100) NOT NULL, `email` varchar(150) DEFAULT NULL, `total_score` int(11) DEFAULT '0', `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, `user_id` int(11) DEFAULT NULL, PRIMARY KEY (`player_id`), UNIQUE KEY `uq_players_user` (`user_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `player_attempts` ( `attempt_id` int(11) NOT NULL AUTO_INCREMENT, `player_id` int(11) NOT NULL, `question_id` int(11) NOT NULL, `selected_option` enum('A','B','C','D') NOT NULL, `is_correct` tinyint(1) NOT NULL, `attempted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`attempt_id`), KEY `fk_attempt_player` (`player_id`), KEY `fk_attempt_question` (`question_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `questions` ( `question_id` int(11) NOT NULL AUTO_INCREMENT, `question_text` text NOT NULL, `option_a` varchar(255) NOT NULL, `option_b` varchar(255) NOT NULL, `option_c` varchar(255) NOT NULL, `option_d` varchar(255) DEFAULT NULL, `correct_option` enum('A','B','C','D') NOT NULL, `difficulty` varchar(50) DEFAULT 'Medium', `interaction_id` int(11) DEFAULT NULL, `source_key` varchar(100) DEFAULT NULL, PRIMARY KEY (`question_id`), UNIQUE KEY `uq_questions_source_key` (`source_key`), KEY `fk_questions_interaction` (`interaction_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `side_effects` ( `id` int(11) NOT NULL AUTO_INCREMENT, `name_arabic` varchar(150) NOT NULL, `name_english` varchar(150) NOT NULL, `description` text, `severity` varchar(50) DEFAULT NULL, PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `users` ( `id` int(11) NOT NULL AUTO_INCREMENT, `username` varchar(100) NOT NULL, `email` varchar(150) NOT NULL, `password` varchar(255) NOT NULL, `role` enum('admin','pharmacist','user') NOT NULL DEFAULT 'user', `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), UNIQUE KEY `uq_users_username` (`username`), UNIQUE KEY `uq_users_email` (`email`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `user_chronic_conditions` ( `user_id` int(11) NOT NULL, `condition_id` int(11) NOT NULL, PRIMARY KEY (`user_id`,`condition_id`), KEY `fk_ucc_condition` (`condition_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''CREATE TABLE IF NOT EXISTS `user_health_profiles` ( `user_id` int(11) NOT NULL, `age` int(11) DEFAULT NULL, `is_pregnant` tinyint(1) NOT NULL DEFAULT '0', PRIMARY KEY (`user_id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''',
'''ALTER TABLE `ckeck_medicines` ADD CONSTRAINT `fk_check_med_check` FOREIGN KEY (`ckeck_id`) REFERENCES `interaction_checks` (`check_id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_check_med_drug` FOREIGN KEY (`drug_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `drug_contraindications` ADD CONSTRAINT `fk_contra_condition` FOREIGN KEY (`condition_id`) REFERENCES `health_conditions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_contra_medication` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `drug_interactions` ADD CONSTRAINT `fk_interaction_drug1` FOREIGN KEY (`drug_1_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_interaction_drug2` FOREIGN KEY (`drug_2_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `interaction_checks` ADD CONSTRAINT `fk_checks_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE SET NULL ON UPDATE CASCADE, ADD CONSTRAINT `fk_checks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `interaction_conditions` ADD CONSTRAINT `fk_int_cond_check` FOREIGN KEY (`interaction_check_id`) REFERENCES `interaction_checks` (`check_id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_int_cond_condition` FOREIGN KEY (`condition_id`) REFERENCES `health_conditions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `medications` ADD CONSTRAINT `fk_med_classification` FOREIGN KEY (`classification_id`) REFERENCES `drug_classification` (`id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `medicine_sideeffects` ADD CONSTRAINT `fk_med_side_effect` FOREIGN KEY (`side_effect_id`) REFERENCES `side_effects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_med_side_med` FOREIGN KEY (`medicine_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `med_associated` ADD CONSTRAINT `fk_med_assoc_med` FOREIGN KEY (`medicine_id`) REFERENCES `medications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_med_assoc_sym` FOREIGN KEY (`associated_symptom_id`) REFERENCES `associated_symptoms` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `password_resets` ADD CONSTRAINT `fk_pr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `patient_conditions` ADD CONSTRAINT `fk_pat_cond_condition` FOREIGN KEY (`condition_id`) REFERENCES `health_conditions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_pat_cond_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `pharmacists` ADD CONSTRAINT `fk_pharmacists_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `players` ADD CONSTRAINT `fk_players_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `player_attempts` ADD CONSTRAINT `fk_attempt_player` FOREIGN KEY (`player_id`) REFERENCES `players` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_attempt_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `questions` ADD CONSTRAINT `fk_questions_interaction` FOREIGN KEY (`interaction_id`) REFERENCES `drug_interactions` (`interaction_id`) ON DELETE SET NULL ON UPDATE CASCADE''',
'''ALTER TABLE `user_chronic_conditions` ADD CONSTRAINT `fk_ucc_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, ADD CONSTRAINT `fk_ucc_condition` FOREIGN KEY (`condition_id`) REFERENCES `health_conditions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''ALTER TABLE `user_health_profiles` ADD CONSTRAINT `fk_uhp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE''',
'''DROP TRIGGER IF EXISTS `trg_di_before_insert`''',
'''DROP TRIGGER IF EXISTS `trg_di_before_update`''',
'''CREATE TRIGGER `trg_di_before_insert` BEFORE INSERT ON `drug_interactions`
  FOR EACH ROW BEGIN
  IF NEW.drug_1_id = NEW.drug_2_id THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'drug_1_id and drug_2_id must be different';
  END IF;
  END''',
'''CREATE TRIGGER `trg_di_before_update` BEFORE UPDATE ON `drug_interactions`
  FOR EACH ROW BEGIN
  IF NEW.drug_1_id = NEW.drug_2_id THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'drug_1_id and drug_2_id must be different';
  END IF;
  END''',
]

uri = input('Paste your DATABASE_URL here, then press Enter: ').strip()
u = urlparse(uri)
if not u.username or not u.hostname:
    raise SystemExit('The link is empty or incomplete. It must start with mysql://')
conn = pymysql.connect(host=u.hostname, port=u.port or 3306, user=unquote(u.username),
                       password=unquote(u.password), database=u.path.lstrip('/'),
                       charset='utf8mb4', ssl={'fake_flag_to_enable_tls': True}, autocommit=True)
cur = conn.cursor()
print('Connected to database:', u.path.lstrip('/'))
cur.execute('SHOW TABLES')
tables = [r[0] for r in cur.fetchall()]
if tables:
    print('The database already has %d tables: %s' % (len(tables), ', '.join(tables)))
    if input('Type YES to DELETE them and recreate everything: ') != 'YES':
        raise SystemExit('Cancelled. Nothing was changed.')
    cur.execute('SET FOREIGN_KEY_CHECKS=0')
    for t in tables:
        cur.execute('DROP TABLE IF EXISTS `%s`' % t)
    cur.execute('SET FOREIGN_KEY_CHECKS=1')
failed = 0
for s in STATEMENTS:
    try:
        cur.execute(s)
    except Exception as e:
        failed += 1
        print('FAILED:', s[:70], '->', e)
cur.execute('SHOW TABLES')
print('Done. Tables now in database:', len(cur.fetchall()), '| failed statements:', failed)