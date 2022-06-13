-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2022-06-13 08:05:49
-- 伺服器版本： 10.4.24-MariaDB
-- PHP 版本： 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `elfdb`
--

-- --------------------------------------------------------

--
-- 資料表結構 `env_control_record`
--

CREATE TABLE `env_control_record` (
  `plant_id` int(11) NOT NULL,
  `control_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `operation` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `sunshine` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `env_control_record`
--

INSERT INTO `env_control_record` (`plant_id`, `control_time`, `operation`, `humidity`, `sunshine`) VALUES
(0, '2022-06-12 11:06:05', 0, 10, 10);

-- --------------------------------------------------------

--
-- 資料表結構 `plant`
--

CREATE TABLE `plant` (
  `plant_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `plant_name` varchar(10) NOT NULL,
  `plant_type` varchar(32) NOT NULL,
  `machine_id` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `plant`
--

INSERT INTO `plant` (`plant_id`, `user_id`, `plant_name`, `plant_type`, `machine_id`) VALUES
(1, 0, '咪咪貓薄荷', '薄荷', 'FF:EE:AA:FF:CC:CC'),
(2, 0, '植物一', '沙漠玫瑰', 'FF:EE:AA:FF:CC:BB');

-- --------------------------------------------------------

--
-- 資料表結構 `plant_picture`
--

CREATE TABLE `plant_picture` (
  `machine_id` varchar(32) NOT NULL,
  `cap_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `plant_pic` mediumblob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `plant_picture`
--

INSERT INTO `plant_picture` (`machine_id`, `cap_time`, `plant_pic`) VALUES
INSERT INTO `plant_picture` (`machine_id`, `cap_time`, `plant_pic`) VALUES

-- --------------------------------------------------------

--
-- 資料表結構 `user`
--

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 傾印資料表的資料 `user`
--

INSERT INTO `user` (`user_id`) VALUES
(0),
(1);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `plant`
--
ALTER TABLE `plant`
  ADD PRIMARY KEY (`plant_id`);

--
-- 資料表索引 `plant_picture`
--
ALTER TABLE `plant_picture`
  ADD PRIMARY KEY (`machine_id`,`cap_time`);

--
-- 資料表索引 `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `plant`
--
ALTER TABLE `plant`
  MODIFY `plant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;