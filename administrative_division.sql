CREATE TABLE `tb_sys_administrative_division` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `sup_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '父级区划代码',
  `data_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '区划代码',
  `data_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '区划名称',
  `pinyin_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '拼音码',
  `data_level` tinyint(1) NOT NULL COMMENT '区划级别',
  `data_order` int DEFAULT NULL COMMENT '排序',
  `is_show` tinyint(1) DEFAULT NULL COMMENT '是否显示',
  `can_select` tinyint(1) DEFAULT NULL COMMENT '是否能选中',
  `class_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '城乡分类代码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_data_code` (`data_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;