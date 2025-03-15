from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `dataset` (
    `dataset_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `project_id` INT NOT NULL,
    `dataset_name` VARCHAR(255) NOT NULL,
    `data_url` VARCHAR(255) NOT NULL,
    `data_type` VARCHAR(100) NOT NULL,
    `data_size` DOUBLE NOT NULL,
    `label` VARCHAR(255) NOT NULL,
    `user_id` VARCHAR(255) NOT NULL,
    `introduction` LONGTEXT NOT NULL,
    `public` INT NOT NULL DEFAULT 0
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `hypara` (
    `hypara_id` VARCHAR(255) NOT NULL PRIMARY KEY,
    `store_path` VARCHAR(255) NOT NULL,
    `project_id` INT NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `model` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `model_name` VARCHAR(255) NOT NULL,
    `model_date` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `model_description` LONGTEXT NOT NULL,
    `model_overview_markdown` LONGTEXT NOT NULL,
    `model_run_count` INT NOT NULL DEFAULT 0,
    `model_view_count` INT NOT NULL DEFAULT 0,
    `frame` VARCHAR(255) NOT NULL,
    `image_id` INT NOT NULL,
    `pub` INT NOT NULL,
    `model_path` VARCHAR(255) NOT NULL,
    `user_id` VARCHAR(255) NOT NULL,
    `hypara_path` VARCHAR(255) NOT NULL,
    `tag` VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `project` (
    `project_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `project_name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `user_id` VARCHAR(255) NOT NULL,
    `status` VARCHAR(100) NOT NULL,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `visibility` VARCHAR(100) NOT NULL,
    `model_id` INT NOT NULL,
    `train_dataset_id` INT NOT NULL,
    `test_dataset_id` INT NOT NULL,
    `store_path` VARCHAR(255) NOT NULL,
    `project_type` VARCHAR(100) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `tag` (
    `tag_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `tag_name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `user_id` VARCHAR(255) NOT NULL PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `level` INT NOT NULL DEFAULT 0,
    `email` VARCHAR(255) NOT NULL,
    `image_id` VARCHAR(255) NOT NULL,
    `admin` INT NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `md` (
    `dataset_id` INT NOT NULL,
    `model_id` INT NOT NULL,
    FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`) ON DELETE CASCADE,
    FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_md_dataset_f145b5` (`dataset_id`, `model_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `favor` (
    `user_id` VARCHAR(255) NOT NULL,
    `model_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_favor_user_id_0ac8b6` (`user_id`, `model_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
