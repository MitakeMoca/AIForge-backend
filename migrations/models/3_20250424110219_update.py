from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `model` ADD `secret_key` VARCHAR(255) NOT NULL DEFAULT 'MitakeMoca';
        ALTER TABLE `project` ALTER COLUMN `project_field` SET DEFAULT 'No field';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `model` DROP COLUMN `secret_key`;
        ALTER TABLE `project` ALTER COLUMN `project_field` DROP DEFAULT;"""
