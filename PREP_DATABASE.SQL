CREATE DATABASE IF NOT EXISTS inv_tracking;

USE inv_tracking;

CREATE TABLE IF NOT EXISTS inventory (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Item_Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Weight DECIMAL(10,2),
    Price DECIMAL (10,2),
    Mfg_Date DATE,
    Exp_Date DATE,
    Nutritiants TEXT
);