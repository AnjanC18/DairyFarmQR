-- ==========================================================
-- SMART DAIRY FARM MANAGEMENT SYSTEM - DATABASE SCHEMA
-- MCA Minor Project
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `dairy_farm` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `dairy_farm`;

-- --------------------------------------------------------
-- Table: users
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `role` ENUM('admin', 'manager', 'staff') DEFAULT 'staff',
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: animals
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `animals` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `tag_number` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) DEFAULT NULL,
    `species` ENUM('Cow', 'Buffalo', 'Goat', 'Other') DEFAULT 'Cow',
    `breed` VARCHAR(100) NOT NULL,
    `gender` ENUM('Female', 'Male') DEFAULT 'Female',
    `dob` DATE DEFAULT NULL,
    `weight_kg` DECIMAL(6,2) DEFAULT NULL,
    `milking_status` ENUM('Milking', 'Dry', 'Pregnant', 'Sick', 'Calf', 'Sold') DEFAULT 'Milking',
    `health_status` ENUM('Healthy', 'Under Treatment', 'Quarantined', 'Critical') DEFAULT 'Healthy',
    `qr_code_image` VARCHAR(255) DEFAULT NULL,
    `entry_date` DATE DEFAULT (CURRENT_DATE),
    `notes` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: milk_productions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `milk_productions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `animal_id` INT NOT NULL,
    `date` DATE NOT NULL,
    `session` ENUM('Morning', 'Evening', 'Afternoon') NOT NULL,
    `quantity_liters` DECIMAL(5,2) NOT NULL,
    `fat_percentage` DECIMAL(4,2) DEFAULT 4.0,
    `snf_percentage` DECIMAL(4,2) DEFAULT 8.5,
    `rate_per_liter` DECIMAL(6,2) DEFAULT 40.00,
    `total_amount` DECIMAL(8,2) GENERATED ALWAYS AS (`quantity_liters` * `rate_per_liter`) STORED,
    `recorded_by` VARCHAR(100) DEFAULT 'Admin',
    `remarks` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`animal_id`) REFERENCES `animals`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: feed_inventories
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `feed_inventories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `feed_name` VARCHAR(100) NOT NULL,
    `category` ENUM('Green Fodder', 'Dry Fodder', 'Concentrate', 'Mineral Mixture', 'Silage', 'Other') NOT NULL,
    `current_stock` DECIMAL(8,2) NOT NULL DEFAULT 0.0,
    `unit` VARCHAR(20) DEFAULT 'kg',
    `unit_cost` DECIMAL(7,2) NOT NULL DEFAULT 0.0,
    `minimum_threshold` DECIMAL(8,2) DEFAULT 50.0,
    `supplier` VARCHAR(150) DEFAULT NULL,
    `last_restocked` DATE DEFAULT (CURRENT_DATE),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: feed_consumptions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `feed_consumptions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `feed_id` INT NOT NULL,
    `date` DATE NOT NULL,
    `quantity_used` DECIMAL(8,2) NOT NULL,
    `group_or_animal` VARCHAR(100) DEFAULT 'All Milking Cattle',
    `cost` DECIMAL(8,2) DEFAULT 0.0,
    `recorded_by` VARCHAR(100) DEFAULT 'Admin',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`feed_id`) REFERENCES `feed_inventories`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: vaccinations
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `vaccinations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `animal_id` INT NOT NULL,
    `vaccine_name` VARCHAR(120) NOT NULL,
    `administered_date` DATE NOT NULL,
    `next_due_date` DATE NOT NULL,
    `veterinarian` VARCHAR(100) DEFAULT NULL,
    `status` ENUM('Completed', 'Upcoming', 'Overdue') DEFAULT 'Completed',
    `remarks` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`animal_id`) REFERENCES `animals`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: employees
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `employees` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `role` VARCHAR(80) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) DEFAULT NULL,
    `salary` DECIMAL(8,2) NOT NULL DEFAULT 0.0,
    `joining_date` DATE NOT NULL,
    `status` ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
    `address` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: expenses
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `expenses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(150) NOT NULL,
    `category` ENUM('Feed', 'Veterinary & Medical', 'Maintenance & Repairs', 'Labor & Wages', 'Utilities & Electricity', 'Equipment & Machinery', 'Fuel & Transport', 'Miscellaneous') NOT NULL,
    `amount` DECIMAL(9,2) NOT NULL,
    `date` DATE NOT NULL,
    `paid_to` VARCHAR(120) DEFAULT NULL,
    `payment_method` ENUM('Cash', 'Bank Transfer', 'UPI', 'Cheque') DEFAULT 'Cash',
    `receipt_number` VARCHAR(50) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Demo Data Seed
-- --------------------------------------------------------

-- Default Admin User (Password: admin123)
-- werkzeug hash for admin123: scrypt:32768:8:1$KqV486Z3zYhO4V8f$3448a3130d297d28bf3d839bb002da7793d56eb7220cfadbe1cf98492023cb3be696c21e64dfd410ae2b1e19efc24e3ba6c8db54ce55aee7bc6dbf964ce2fef1
INSERT INTO `users` (`username`, `email`, `password_hash`, `full_name`, `role`) VALUES
('admin', 'admin@dairy.com', 'scrypt:32768:8:1$KqV486Z3zYhO4V8f$3448a3130d297d28bf3d839bb002da7793d56eb7220cfadbe1cf98492023cb3be696c21e64dfd410ae2b1e19efc24e3ba6c8db54ce55aee7bc6dbf964ce2fef1', 'Farm Manager Admin', 'admin')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Demo Animals
INSERT INTO `animals` (`tag_number`, `name`, `species`, `breed`, `gender`, `dob`, `weight_kg`, `milking_status`, `health_status`, `qr_code_image`, `entry_date`) VALUES
('DF-101', 'Gauri', 'Cow', 'Gir', 'Female', '2021-03-15', 420.0, 'Milking', 'Healthy', 'DF-101.png', '2023-01-10'),
('DF-102', 'Kamdhenu', 'Cow', 'Sahiwal', 'Female', '2020-07-20', 460.0, 'Milking', 'Healthy', 'DF-102.png', '2022-11-05'),
('DF-103', 'Lakshmi', 'Buffalo', 'Murrah', 'Female', '2021-01-12', 540.0, 'Milking', 'Healthy', 'DF-103.png', '2023-02-18'),
('DF-104', 'Nandini', 'Cow', 'Holstein Friesian (HF)', 'Female', '2022-05-10', 490.0, 'Milking', 'Healthy', 'DF-104.png', '2023-08-01'),
('DF-105', 'Radha', 'Cow', 'Jersey', 'Female', '2021-09-02', 380.0, 'Dry', 'Healthy', 'DF-105.png', '2023-04-12'),
('DF-106', 'Surabhi', 'Cow', 'Red Sindhi', 'Female', '2022-11-25', 410.0, 'Pregnant', 'Healthy', 'DF-106.png', '2024-01-15'),
('DF-107', 'Kaali', 'Buffalo', 'Jaffarabadi', 'Female', '2020-10-18', 580.0, 'Sick', 'Under Treatment', 'DF-107.png', '2023-05-20'),
('DF-108', 'Chhoti', 'Cow', 'Gir', 'Female', '2024-04-01', 95.0, 'Calf', 'Healthy', 'DF-108.png', '2024-04-01')
ON DUPLICATE KEY UPDATE `tag_number`=`tag_number`;

-- Demo Feed
INSERT INTO `feed_inventories` (`feed_name`, `category`, `current_stock`, `unit`, `unit_cost`, `minimum_threshold`, `supplier`) VALUES
('Green Napier Grass', 'Green Fodder', 1200.0, 'kg', 2.50, 300.0, 'Agro Green Farm'),
('Wheat Straw (Bhusa)', 'Dry Fodder', 850.0, 'kg', 6.00, 200.0, 'Kisan Agro Traders'),
('Cattle Feed Pellets (20% Protein)', 'Concentrate', 450.0, 'kg', 24.00, 100.0, 'Godrej Agrovet'),
('Mineral Mixture & Calcium', 'Mineral Mixture', 35.0, 'kg', 65.00, 20.0, 'VetCare Health'),
('Maize Silage', 'Silage', 1500.0, 'kg', 4.50, 400.0, 'Silage India Ltd')
ON DUPLICATE KEY UPDATE `feed_name`=`feed_name`;

-- Demo Employees
INSERT INTO `employees` (`name`, `role`, `phone`, `email`, `salary`, `joining_date`, `status`, `address`) VALUES
('Ramesh Kumar', 'Head Milker & Supervisor', '+91 9876543210', 'ramesh@dairy.com', 22000.00, '2022-01-15', 'Active', 'Village Rampur, Sector 4'),
('Suresh Yadav', 'Animal Caretaker & Feeder', '+91 9876543211', 'suresh@dairy.com', 16000.00, '2022-06-01', 'Active', 'Near Dairy Farm Colony'),
('Dr. Alok Verma', 'Visiting Veterinarian', '+91 9876543212', 'dr.alok@vetcare.in', 28000.00, '2021-08-10', 'Active', 'City Veterinary Hospital Road'),
('Pooja Sharma', 'Accountant & Store In-charge', '+91 9876543213', 'pooja@dairy.com', 20000.00, '2023-03-01', 'Active', 'Civil Lines, Block B')
ON DUPLICATE KEY UPDATE `name`=`name`;
