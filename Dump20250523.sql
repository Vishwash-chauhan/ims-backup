CREATE DATABASE  IF NOT EXISTS `preety_enterprises` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `preety_enterprises`;
-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: preety_enterprises
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) NOT NULL,
  `contact_number` varchar(20) DEFAULT NULL,
  `email_address` varchar(255) DEFAULT NULL,
  `billing_address_line1` varchar(255) DEFAULT NULL,
  `billing_pincode` varchar(10) DEFAULT NULL,
  `billing_city` varchar(100) DEFAULT NULL,
  `billing_state` varchar(100) DEFAULT NULL,
  `billing_country` varchar(100) DEFAULT 'India',
  `shipping_address_line1` varchar(255) DEFAULT NULL,
  `shipping_pincode` varchar(10) DEFAULT NULL,
  `shipping_city` varchar(100) DEFAULT NULL,
  `shipping_state` varchar(100) DEFAULT NULL,
  `shipping_country` varchar(100) DEFAULT 'India',
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(255) NOT NULL,
  `product_code` varchar(50) DEFAULT NULL,
  `hsn_code` varchar(20) DEFAULT NULL,
  `product_image_path` varchar(255) DEFAULT NULL,
  `measuring_units` varchar(50) DEFAULT NULL,
  `reorder_level` int DEFAULT NULL,
  `gst_available` enum('yes','no') DEFAULT 'no',
  `gst_percentage` decimal(5,2) DEFAULT NULL,
  `description` text,
  `current_stock` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_code` (`product_code`),
  KEY `idx_product_name` (`product_name`),
  KEY `idx_product_code` (`product_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_invoice_items`
--

DROP TABLE IF EXISTS `purchase_invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_invoice_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity_purchased` int NOT NULL,
  `price_per_unit_before_gst` decimal(10,2) NOT NULL,
  `gst_percentage` decimal(5,2) DEFAULT '0.00',
  `gst_amount_per_unit` decimal(10,2) DEFAULT '0.00',
  `item_discount_amount` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_gst_amount` decimal(10,2) NOT NULL,
  `item_final_amount` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `purchase_invoice_id` (`purchase_invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `purchase_invoice_items_ibfk_1` FOREIGN KEY (`purchase_invoice_id`) REFERENCES `purchase_invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `purchase_invoice_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_invoice_items`
--

LOCK TABLES `purchase_invoice_items` WRITE;
/*!40000 ALTER TABLE `purchase_invoice_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_invoices`
--

DROP TABLE IF EXISTS `purchase_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) NOT NULL,
  `invoice_date` date NOT NULL,
  `supplier_id` int NOT NULL,
  `total_amount_before_gst` decimal(12,2) DEFAULT '0.00',
  `total_gst_amount` decimal(10,2) DEFAULT '0.00',
  `overall_discount_amount` decimal(10,2) DEFAULT '0.00',
  `total_invoice_amount` decimal(12,2) NOT NULL,
  `payment_status` varchar(50) DEFAULT 'Pending',
  `bill_copy_path` varchar(255) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `supplier_id` (`supplier_id`),
  CONSTRAINT `purchase_invoices_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_invoices`
--

LOCK TABLES `purchase_invoices` WRITE;
/*!40000 ALTER TABLE `purchase_invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_return_items`
--

DROP TABLE IF EXISTS `purchase_return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_return_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_return_id` int NOT NULL,
  `product_id` int NOT NULL,
  `original_purchase_invoice_item_id` int DEFAULT NULL,
  `quantity_returned` int NOT NULL,
  `price_per_unit_at_return` decimal(10,2) NOT NULL,
  `gst_percentage_applied` decimal(5,2) DEFAULT '0.00',
  `gst_amount_claimed_back_per_unit` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_gst_claimed_back` decimal(10,2) NOT NULL,
  `item_final_value` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `purchase_return_id` (`purchase_return_id`),
  KEY `product_id` (`product_id`),
  KEY `original_purchase_invoice_item_id` (`original_purchase_invoice_item_id`),
  CONSTRAINT `purchase_return_items_ibfk_1` FOREIGN KEY (`purchase_return_id`) REFERENCES `purchase_returns` (`id`) ON DELETE CASCADE,
  CONSTRAINT `purchase_return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `purchase_return_items_ibfk_3` FOREIGN KEY (`original_purchase_invoice_item_id`) REFERENCES `purchase_invoice_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_return_items`
--

LOCK TABLES `purchase_return_items` WRITE;
/*!40000 ALTER TABLE `purchase_return_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_returns`
--

DROP TABLE IF EXISTS `purchase_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_returns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_date` date NOT NULL,
  `original_purchase_invoice_id` int NOT NULL,
  `supplier_id` int NOT NULL,
  `return_reason` text,
  `total_items_value_before_gst` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_gst_claimed_back` decimal(10,2) NOT NULL DEFAULT '0.00',
  `net_amount_receivable` decimal(12,2) NOT NULL DEFAULT '0.00',
  `mode_of_refund_received` varchar(50) DEFAULT NULL,
  `refund_receipt_option` enum('full-amount','partial-amount') DEFAULT 'full-amount',
  `partial_amount_received_input` decimal(12,2) DEFAULT NULL,
  `final_amount_received` decimal(12,2) NOT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `original_purchase_invoice_id` (`original_purchase_invoice_id`),
  KEY `supplier_id` (`supplier_id`),
  CONSTRAINT `purchase_returns_ibfk_1` FOREIGN KEY (`original_purchase_invoice_id`) REFERENCES `purchase_invoices` (`id`),
  CONSTRAINT `purchase_returns_ibfk_2` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_returns`
--

LOCK TABLES `purchase_returns` WRITE;
/*!40000 ALTER TABLE `purchase_returns` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_invoice_items`
--

DROP TABLE IF EXISTS `sales_invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sales_invoice_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity_sold` int NOT NULL,
  `price_per_unit_before_gst` decimal(10,2) NOT NULL,
  `gst_percentage` decimal(5,2) DEFAULT '0.00',
  `gst_amount_per_unit` decimal(10,2) DEFAULT '0.00',
  `item_discount_amount` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_gst_amount` decimal(10,2) NOT NULL,
  `item_final_amount` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `sales_invoice_id` (`sales_invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `sales_invoice_items_ibfk_1` FOREIGN KEY (`sales_invoice_id`) REFERENCES `sales_invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sales_invoice_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_invoice_items`
--

LOCK TABLES `sales_invoice_items` WRITE;
/*!40000 ALTER TABLE `sales_invoice_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_invoices`
--

DROP TABLE IF EXISTS `sales_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) NOT NULL,
  `invoice_date` date NOT NULL,
  `customer_id` int NOT NULL,
  `executive_id` int DEFAULT NULL,
  `total_amount_before_gst` decimal(12,2) DEFAULT '0.00',
  `total_gst_amount` decimal(10,2) DEFAULT '0.00',
  `overall_discount_amount` decimal(10,2) DEFAULT '0.00',
  `total_invoice_amount` decimal(12,2) NOT NULL,
  `payment_status` varchar(50) DEFAULT 'Pending',
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `customer_id` (`customer_id`),
  KEY `executive_id` (`executive_id`),
  CONSTRAINT `sales_invoices_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `sales_invoices_ibfk_2` FOREIGN KEY (`executive_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_invoices`
--

LOCK TABLES `sales_invoices` WRITE;
/*!40000 ALTER TABLE `sales_invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_return_items`
--

DROP TABLE IF EXISTS `sales_return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_return_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sales_return_id` int NOT NULL,
  `product_id` int NOT NULL,
  `original_sales_invoice_item_id` int DEFAULT NULL,
  `quantity_returned` int NOT NULL,
  `price_per_unit_at_return` decimal(10,2) NOT NULL,
  `gst_percentage_applied` decimal(5,2) DEFAULT '0.00',
  `gst_amount_reversed_per_unit` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_gst_reversed` decimal(10,2) NOT NULL,
  `item_final_value` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `sales_return_id` (`sales_return_id`),
  KEY `product_id` (`product_id`),
  KEY `original_sales_invoice_item_id` (`original_sales_invoice_item_id`),
  CONSTRAINT `sales_return_items_ibfk_1` FOREIGN KEY (`sales_return_id`) REFERENCES `sales_returns` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sales_return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `sales_return_items_ibfk_3` FOREIGN KEY (`original_sales_invoice_item_id`) REFERENCES `sales_invoice_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_return_items`
--

LOCK TABLES `sales_return_items` WRITE;
/*!40000 ALTER TABLE `sales_return_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_returns`
--

DROP TABLE IF EXISTS `sales_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_returns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_date` date NOT NULL,
  `original_invoice_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `executive_id` int DEFAULT NULL,
  `return_reason` text,
  `total_items_value_before_gst` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_gst_reversed` decimal(10,2) NOT NULL DEFAULT '0.00',
  `net_refundable_amount` decimal(12,2) NOT NULL DEFAULT '0.00',
  `mode_of_refund` varchar(50) DEFAULT NULL,
  `refund_option` enum('full-refund','partial-refund') DEFAULT 'full-refund',
  `partial_refund_amount_input` decimal(12,2) DEFAULT NULL,
  `final_amount_refunded` decimal(12,2) NOT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `original_invoice_id` (`original_invoice_id`),
  KEY `customer_id` (`customer_id`),
  KEY `executive_id` (`executive_id`),
  CONSTRAINT `sales_returns_ibfk_1` FOREIGN KEY (`original_invoice_id`) REFERENCES `sales_invoices` (`id`),
  CONSTRAINT `sales_returns_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `sales_returns_ibfk_3` FOREIGN KEY (`executive_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_returns`
--

LOCK TABLES `sales_returns` WRITE;
/*!40000 ALTER TABLE `sales_returns` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier_products`
--

DROP TABLE IF EXISTS `supplier_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier_products` (
  `supplier_id` int NOT NULL,
  `product_id` int NOT NULL,
  PRIMARY KEY (`supplier_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `supplier_products_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `supplier_products_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_products`
--

LOCK TABLES `supplier_products` WRITE;
/*!40000 ALTER TABLE `supplier_products` DISABLE KEYS */;
/*!40000 ALTER TABLE `supplier_products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_name` varchar(255) NOT NULL,
  `supplier_contact` varchar(50) DEFAULT NULL,
  `gst_available` enum('yes','no') DEFAULT 'no',
  `gst_number` varchar(15) DEFAULT NULL,
  `address_line1` varchar(255) DEFAULT NULL,
  `address_pincode` varchar(10) DEFAULT NULL,
  `address_city` varchar(100) DEFAULT NULL,
  `address_state` varchar(100) DEFAULT NULL,
  `address_country` varchar(100) DEFAULT 'India',
  `account_available` enum('yes','no') DEFAULT 'no',
  `account_holder_name` varchar(255) DEFAULT NULL,
  `account_number` varchar(50) DEFAULT NULL,
  `ifsc_code` varchar(20) DEFAULT NULL,
  `branch` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_supplier_name` (`supplier_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `password_hash` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-23 18:41:04
