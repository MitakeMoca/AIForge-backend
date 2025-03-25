from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dataset` ADD `likes` INT NOT NULL DEFAULT 0;
        ALTER TABLE `model` ALTER COLUMN `model_path` SET DEFAULT '';
        ALTER TABLE `user` ALTER COLUMN `image_id` SET DEFAULT 0;
        ALTER TABLE `user` ALTER COLUMN `admin` SET DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ALTER COLUMN `image_id` DROP DEFAULT;
        ALTER TABLE `user` ALTER COLUMN `admin` DROP DEFAULT;
        ALTER TABLE `model` ALTER COLUMN `model_path` DROP DEFAULT;
        ALTER TABLE `dataset` DROP COLUMN `likes`;"""
