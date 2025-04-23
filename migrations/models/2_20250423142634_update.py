from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `project` ADD `project_field` VARCHAR(100) NOT NULL;
        ALTER TABLE `project` ALTER COLUMN `store_path` SET DEFAULT '';
        ALTER TABLE `project` ALTER COLUMN `status` SET DEFAULT 'init';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `project` DROP COLUMN `project_field`;
        ALTER TABLE `project` ALTER COLUMN `store_path` DROP DEFAULT;
        ALTER TABLE `project` ALTER COLUMN `status` DROP DEFAULT;"""
