-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: fmcg
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
  `customer_id` int NOT NULL AUTO_INCREMENT,
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
  PRIMARY KEY (`customer_id`)
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
  `product_code` varchar(45) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `hsn_code` varchar(20) DEFAULT NULL,
  `product_image_path` varchar(255) DEFAULT NULL,
  `measuring_units` varchar(50) DEFAULT NULL,
  `reorder_level` int DEFAULT NULL,
  `gst_available` enum('yes','no') DEFAULT 'no',
  `gst_percentage` decimal(5,2) DEFAULT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_code_UNIQUE` (`product_code`)
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
-- Table structure for table `purchase_items`
--

DROP TABLE IF EXISTS `purchase_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_items` (
  `purchase_item_id` int NOT NULL,
  `purchase_id` varchar(45) DEFAULT NULL,
  `product_id` varchar(45) DEFAULT NULL,
  `quantity_purchased` int DEFAULT NULL,
  `price_per_unit` decimal(10,2) DEFAULT NULL,
  `gross_amount` decimal(10,2) DEFAULT NULL,
  `descount` decimal(10,2) DEFAULT NULL,
  `net_amount` decimal(10,2) DEFAULT NULL,
  `total_payable_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`purchase_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_items`
--

LOCK TABLES `purchase_items` WRITE;
/*!40000 ALTER TABLE `purchase_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_items` ENABLE KEYS */;
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
  `price_per_unit_before_gst` decimal(10,2) NOT NULL,
  `gst_percentage_applied` decimal(5,2) DEFAULT '0.00',
  `gst_amount_claimed_back` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_with_gst` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
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
  `overall_return_discount_type` enum('percentage','fixed') DEFAULT NULL,
  `overall_return_discount_value` decimal(10,2) DEFAULT NULL,
  `calculated_overall_return_discount_amount` decimal(10,2) DEFAULT '0.00',
  `total_after_overall_discount` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_gst_claimed_back` decimal(10,2) NOT NULL DEFAULT '0.00',
  `net_amount_receivable` decimal(12,2) NOT NULL DEFAULT '0.00',
  `mode_of_refund_received` varchar(50) DEFAULT NULL,
  `refund_receipt_option` enum('full-amount','partial-amount') NOT NULL DEFAULT 'full-amount',
  `partial_amount_received_input` decimal(12,2) DEFAULT NULL,
  `final_amount_received` decimal(12,2) NOT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
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
-- Table structure for table `purchase_table`
--

DROP TABLE IF EXISTS `purchase_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_table` (
  `purchase_id` int NOT NULL AUTO_INCREMENT,
  `purchase_date` date DEFAULT NULL,
  `vendor_id` varchar(45) DEFAULT NULL,
  `gross_amount` decimal(10,2) DEFAULT NULL,
  `discount` decimal(10,2) DEFAULT NULL,
  `net_amount` decimal(10,2) DEFAULT NULL,
  `gst_amount` decimal(10,2) DEFAULT NULL,
  `total_payable_amount` decimal(10,2) DEFAULT NULL,
  `mode_of_payment` varchar(45) DEFAULT NULL,
  `method_of_payment` varchar(45) DEFAULT NULL,
  `payment_option` varchar(45) DEFAULT NULL,
  `amount_paid` decimal(10,2) DEFAULT NULL,
  `purchase_tablecol` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`purchase_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_table`
--

LOCK TABLES `purchase_table` WRITE;
/*!40000 ALTER TABLE `purchase_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sale_items`
--

DROP TABLE IF EXISTS `sale_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale_items` (
  `sale_item_id` int NOT NULL AUTO_INCREMENT,
  `sale_id` varchar(45) DEFAULT NULL,
  `product_id` varchar(45) DEFAULT NULL,
  `quantity_sold` int DEFAULT NULL,
  `price_per_unit` decimal(10,2) DEFAULT NULL,
  `gross_amount` decimal(10,2) DEFAULT NULL,
  `discount` decimal(10,2) DEFAULT NULL,
  `net_amount` decimal(10,2) DEFAULT NULL,
  `total_payable_amt` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`sale_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sale_items`
--

LOCK TABLES `sale_items` WRITE;
/*!40000 ALTER TABLE `sale_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `sale_items` ENABLE KEYS */;
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
  `original_invoice_item_id` int DEFAULT NULL,
  `quantity_returned` int NOT NULL,
  `price_per_unit_before_gst` decimal(10,2) NOT NULL,
  `gst_percentage_applied` decimal(5,2) DEFAULT '0.00',
  `gst_amount_reversed` decimal(10,2) DEFAULT '0.00',
  `item_sub_total_before_gst` decimal(10,2) NOT NULL,
  `item_total_with_gst` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
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
  `total_items_value_before_gst` decimal(12,2) DEFAULT '0.00',
  `overall_return_discount_type` enum('percentage','fixed') DEFAULT NULL,
  `overall_return_discount_value` decimal(10,2) DEFAULT NULL,
  `calculated_overall_return_discount_amount` decimal(10,2) DEFAULT '0.00',
  `total_after_overall_discount` decimal(12,2) DEFAULT '0.00',
  `total_gst_reversed` decimal(10,2) DEFAULT '0.00',
  `net_refundable_amount` decimal(12,2) DEFAULT '0.00',
  `mode_of_refund` varchar(50) DEFAULT NULL,
  `refund_option` enum('full-refund','partial-refund') DEFAULT 'full-refund',
  `partial_refund_amount_input` decimal(12,2) DEFAULT NULL,
  `final_amount_refunded` decimal(12,2) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
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
-- Table structure for table `sales_table`
--

DROP TABLE IF EXISTS `sales_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_table` (
  `sales_id` int NOT NULL AUTO_INCREMENT,
  `sales_date` date DEFAULT NULL,
  `executive_name` varchar(45) DEFAULT NULL,
  `customer_id` varchar(45) DEFAULT NULL,
  `gross_amount` decimal(10,2) DEFAULT NULL,
  `discount` decimal(10,2) DEFAULT NULL,
  `net_amount` decimal(10,2) DEFAULT NULL,
  `gst_amount` decimal(10,2) DEFAULT NULL,
  `total_payable_amount` decimal(10,2) DEFAULT NULL,
  `mode_of_payment` varchar(45) DEFAULT NULL,
  `method_of_payment` varchar(45) DEFAULT NULL,
  `payment_option` varchar(45) DEFAULT NULL,
  `amount_paid` decimal(10,2) DEFAULT NULL,
  `balance_due` decimal(10,2) DEFAULT NULL,
  `invoice_number` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`sales_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_table`
--

LOCK TABLES `sales_table` WRITE;
/*!40000 ALTER TABLE `sales_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier_supplied_products`
--

DROP TABLE IF EXISTS `supplier_supplied_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier_supplied_products` (
  `id` int NOT NULL,
  `supplier_id` varchar(45) DEFAULT NULL,
  `product_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_supplied_products`
--

LOCK TABLES `supplier_supplied_products` WRITE;
/*!40000 ALTER TABLE `supplier_supplied_products` DISABLE KEYS */;
/*!40000 ALTER TABLE `supplier_supplied_products` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-26 11:33:59
