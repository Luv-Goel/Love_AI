from prisma import Prisma
from love_engine._logging import verbose_logger


async def apply_db_fixes(db: Prisma):
    """
    Do Not Run this in production, only use it as a one-time fix
    """
    verbose_logger.warning(
        "DO NOT run this in Production....Running update_unassigned_teams"
    )
    try:
        sql_query = """
            UPDATE "love_engine_SpendLogs"
            SET team_id = (
                SELECT vt.team_id
                FROM "love_engine_VerificationToken" vt
                WHERE vt.token = "love_engine_SpendLogs".api_key
            )
            WHERE team_id IS NULL
            AND EXISTS (
                SELECT 1
                FROM "love_engine_VerificationToken" vt
                WHERE vt.token = "love_engine_SpendLogs".api_key
            );
        """
        response = await db.query_raw(sql_query)
        print(
            "Updated unassigned teams, Response=%s",
            response,
        )
    except Exception as e:
        raise Exception(f"Error apply_db_fixes: {str(e)}")
    return
