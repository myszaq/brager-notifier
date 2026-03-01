CREATE TABLE `measurements` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`created_at` DATETIME NOT NULL DEFAULT current_timestamp(),
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `idx_measurements_created_at` (`created_at`) USING BTREE
)
COMMENT='Table used to store common id and creation date for all remaining data tables.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=INNODB;

CREATE TABLE `boiler_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`boiler_temperature` DECIMAL(5,2) NOT NULL,
	`boiler_setting` INT(11) NOT NULL,
	`boiler_status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`boiler_pump_status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`outdoor_temperature` DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_boiler_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store boiler related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;

CREATE TABLE `burner_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`burner_power` DECIMAL(5,2) NOT NULL,
	`flame_brightness` INT(11) NOT NULL,
	`blower_efficiency` INT(11) NOT NULL,
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_burner_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store burner related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;

CREATE TABLE `dhw_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`dhw_temperature` DECIMAL(5,2) NOT NULL,
	`dhw_setting` INT(11) NOT NULL,
	`dhw_pump_status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`dhw_operating_mode` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_dhw_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store DHW (domestic hot water) related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;

CREATE TABLE `fuel_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`fuel_level` INT(11) NOT NULL,
	`burned_fuel_amount` INT(11) NOT NULL,
	`burned_fuel_in_24h` DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_fuel_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store fuel related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;

CREATE TABLE `fuel_refills` (
	`entry_id` INT(11) NOT NULL AUTO_INCREMENT,
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`previous_fuel_level` INT(11) NOT NULL,
	`refill_date` DATETIME NOT NULL DEFAULT current_timestamp(),
	PRIMARY KEY (`entry_id`) USING BTREE,
	INDEX `FK_fuel_refills` (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_fuel_refills` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store basic information about refilling fuel based on the data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=INNODB;

CREATE TABLE `return_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`return_temperature` DECIMAL(5,2) NOT NULL,
	`return_pump_status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_return_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store return flow related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;

CREATE TABLE `valve_params` (
	`measurement_id` INT(11) NOT NULL DEFAULT '0',
	`valve_temperature` DECIMAL(5,2) NOT NULL,
	`valve_setting` INT(11) NOT NULL,
	`valve_pump_status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`valve_operating_mode` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	PRIMARY KEY (`measurement_id`) USING BTREE,
	CONSTRAINT `FK_valve_params` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON UPDATE NO ACTION ON DELETE CASCADE
)
COMMENT='This table is used to store valve related data collected from Brager Connect application.'
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;
