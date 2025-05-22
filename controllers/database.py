import warnings

import aiomysql
import pymysql

from controllers.db_pool import db_pool

async def execute(statement: str, args: [] = None):
    pool = db_pool.get_pool()

    if pool is None:
        raise ConnectionAbortedError('A connection with the pool could not be established as the pool could not be found')

    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    await cursor.execute(statement, args)
                    await conn.commit()

                    if cursor.description:
                        column_names = [desc[0] for desc in cursor.description]
                        rows = await cursor.fetchall()
                        result = [dict(zip(column_names, row)) for row in rows]

                        return result

                    return []
    except pymysql.err.Warning:
        pass
    except aiomysql.Error as err:
        await conn.rollback()
        print('An aiomysql error occurred while executing a statement:\n{}\n-----\nArgs: {}\nError: {}'.format(statement, args, err))
        return aiomysql.Error