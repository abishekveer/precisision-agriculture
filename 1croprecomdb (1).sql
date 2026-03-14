-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 07, 2022 at 08:18 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `1croprecomdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `admintb`
--

CREATE TABLE `admintb` (
  `UserName` varchar(250) NOT NULL,
  `Password` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admintb`
--

INSERT INTO `admintb` (`UserName`, `Password`) VALUES
('admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `querytb`
--

CREATE TABLE `querytb` (
  `id` bigint(250) NOT NULL auto_increment,
  `UserName` varchar(250) NOT NULL,
  `Nitrogen` varchar(250) NOT NULL,
  `Phosphorus` varchar(250) NOT NULL,
  `Potassium` varchar(250) NOT NULL,
  `Temperature` varchar(250) NOT NULL,
  `Humidity` varchar(250) NOT NULL,
  `PH` varchar(250) NOT NULL,
  `Rainfall` varchar(250) NOT NULL,
  `DResult` varchar(250) NOT NULL,
  `CropInfo` varchar(250) NOT NULL,
  `Fertilizer` varchar(1000) NOT NULL,
  `Location` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=15 ;

--
-- Dumping data for table `querytb`
--

INSERT INTO `querytb` (`id`, `UserName`, `Nitrogen`, `Phosphorus`, `Potassium`, `Temperature`, `Humidity`, `PH`, `Rainfall`, `DResult`, `CropInfo`, `Fertilizer`, `Location`) VALUES
(12, 'jai', '70', '120', '220', '22.65', '55', '4.5', '200', 'Predict', 'chickpea', 'The generally recommended doses for chickpea include 20–30 kg nitrogen (N) and 40–60 kg phosphorus (P) ha-1. If soils are low in potassium (K), an application of 17 to 25 kg K ha-1 is recommended', 'Salem'),
(13, 'jai', '120', '120', '200', '22.65', '55', '6.5', '100', 'Predict', 'chickpea', 'The generally recommended doses for chickpea include 20–30 kg nitrogen (N) and 40–60 kg phosphorus (P) ha-1. If soils are low in potassium (K), an application of 17 to 25 kg K ha-1 is recommended', 'Erode'),
(14, 'jai', '20', '40', '120', '23', '52', '8', '80', 'Predict', 'papaya', 'Generally 90 g of Urea, 250 g of Super phosphate and 140 g of Muriate of Potash per plant are recommended for each application', 'Ariyalur');

-- --------------------------------------------------------

--
-- Table structure for table `regtb`
--

CREATE TABLE `regtb` (
  `Name` varchar(250) NOT NULL,
  `Gender` varchar(250) NOT NULL,
  `Age` varchar(250) NOT NULL,
  `Email` varchar(250) NOT NULL,
  `Mobile` varchar(250) NOT NULL,
  `Address` varchar(250) NOT NULL,
  `UserName` varchar(250) NOT NULL,
  `Password` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `regtb`
--

INSERT INTO `regtb` (`Name`, `Gender`, `Age`, `Email`, `Mobile`, `Address`, `UserName`, `Password`) VALUES
('jai', 'male', '20', 'jai@gmail.com', '9894637541', 'No 16, Samnath Plaza, Madurai Main Road, Melapudhur', 'jai', 'jai');
