"""Module to manage database of Rus and Esp words."""
import sqlite3


def create_db():
    """Create a new database if there is no one."""
    conn = sqlite3.connect('words.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spanish TEXT NOT NULL,
        russian TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_db()


def word_exist(spanish_word):
    """Check is the word exists in the database."""
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM words WHERE spanish = ? LIMIT 1', (spanish_word,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def add_word(spanish_word, russian_word):
    """Adding new words into database."""
    spanish_word = spanish_word.lower()
    russian_word = russian_word.lower()

    if word_exist(spanish_word):
        print(f'Слово {spanish_word} уже существует в базе.')
        return

    try:
        conn = sqlite3.connect('words.db')
        c = conn.cursor()
        c.execute(
            'INSERT INTO words (spanish, russian) VALUES (?, ?)',
            (spanish_word, russian_word)
        )
        conn.commit()
        print(f'Слово {spanish_word} успешно добавлено в базу.')

    except sqlite3.Error as error:
        print(f'Ошибка при работе с базой данных: {error}')

    finally:
        conn.close()


def delete_word(spanish_word):
    """Delete word from database."""
    try:
        conn = sqlite3.connect('words.db')
        c = conn.cursor()
        c.execute(
            'DELETE FROM words WHERE spanish = ?', (spanish_word,)
        )

        if c.rowcount > 0:
            print(f'Слово {spanish_word} успешно удалено.')
        else:
            print(f'Слово "{spanish_word}" не найдено в базе.')
        conn.commit()

    except sqlite3 as error:
        print(f'Ошибка при работе с базой данных: {error}')

    finally:
        conn.close()
