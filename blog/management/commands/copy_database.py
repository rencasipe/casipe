import os
import sqlite3
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from blog.models import ThematicCategory, Word, ExampleSentence

class Command(BaseCommand):
    help = 'Copy data from backup database to main database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-path',
            default='db.sqlite3.backup',
            help='Path to the backup database file'
        )

    def handle(self, *args, **options):
        backup_path = options['backup_path']
        
        if not os.path.exists(backup_path):
            self.stdout.write(self.style.ERROR(f'Backup file not found: {backup_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting data copy from {backup_path} to main database'))
        
        # Setup direct SQLite connections for more control
        try:
            # Connect to both databases
            source_conn = sqlite3.connect(backup_path)
            source_conn.row_factory = sqlite3.Row
            dest_conn = sqlite3.connect('db.sqlite3')
            
            self.stdout.write(self.style.SUCCESS('Connected to both databases'))
            
            # Copy the data
            with transaction.atomic():
                self._copy_thematic_categories(source_conn, dest_conn)
                self._copy_words(source_conn, dest_conn)
                self._copy_word_categories(source_conn, dest_conn)
                self._copy_example_sentences(source_conn, dest_conn)
                
            self.stdout.write(self.style.SUCCESS('Data successfully copied from backup to main database'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during data copy: {str(e)}'))
            raise
        
        finally:
            # Close connections
            if 'source_conn' in locals():
                source_conn.close()
            if 'dest_conn' in locals():
                dest_conn.close()
    
    def _copy_thematic_categories(self, source_conn, dest_conn):
        """Copy ThematicCategory records"""
        self.stdout.write('Copying thematic categories...')
        
        # Get table name from the source database
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%thematiccategory'")
        table_result = source_cursor.fetchone()
        
        if not table_result:
            self.stdout.write(self.style.WARNING('No thematic category table found in backup'))
            return
            
        table_name = table_result[0]
        
        # Get categories from backup
        source_cursor.execute(f'SELECT id, name, description FROM {table_name}')
        categories = source_cursor.fetchall()
        
        # Import to main DB
        dest_cursor = dest_conn.cursor()
        
        # First, clear existing categories (optional - remove if you want to merge instead)
        dest_cursor.execute('DELETE FROM blog_thematiccategory')
        
        # Then insert new ones
        for category in categories:
            dest_cursor.execute(
                'INSERT OR REPLACE INTO blog_thematiccategory (id, name, description) VALUES (?, ?, ?)',
                (category['id'], category['name'], category['description'])
            )
        
        dest_conn.commit()
        self.stdout.write(f'Copied {len(categories)} thematic categories')
    
    def _copy_words(self, source_conn, dest_conn):
        """Copy Word records"""
        self.stdout.write('Copying words...')
        
        # Get table name from source database
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%word' AND name NOT LIKE '%_categories' AND name NOT LIKE '%example%'")
        table_result = source_cursor.fetchone()
        
        if not table_result:
            self.stdout.write(self.style.WARNING('No word table found in backup'))
            return
            
        table_name = table_result[0]
        
        # Get words from backup
        source_cursor.execute(f'SELECT id, text, definition, gender, has_gender, created_at, updated_at FROM {table_name}')
        words = source_cursor.fetchall()
        
        # Import to main DB
        dest_cursor = dest_conn.cursor()
        
        # First, clear existing words (optional - remove if you want to merge instead)
        dest_cursor.execute('DELETE FROM blog_word')
        
        # Then insert new ones
        for word in words:
            dest_cursor.execute(
                'INSERT OR REPLACE INTO blog_word (id, text, definition, gender, has_gender, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (word['id'], word['text'], word['definition'], word['gender'], word['has_gender'], word['created_at'], word['updated_at'])
            )
        
        dest_conn.commit()
        self.stdout.write(f'Copied {len(words)} words')
    
    def _copy_word_categories(self, source_conn, dest_conn):
        """Copy Word-ThematicCategory relationships"""
        self.stdout.write('Copying word-category relationships...')
        
        # Get table name from source database
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%word%categories%'")
        table_result = source_cursor.fetchone()
        
        if not table_result:
            self.stdout.write(self.style.WARNING('No word-category relationship table found in backup'))
            return
            
        table_name = table_result[0]
        
        # Get word-category relationships from backup
        source_cursor.execute(f'SELECT * FROM {table_name}')
        relationships = source_cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in source_cursor.description]
        word_id_col = next((col for col in columns if 'word_id' in col), None)
        category_id_col = next((col for col in columns if 'category_id' in col or 'thematiccategory_id' in col), None)
        
        if not word_id_col or not category_id_col:
            self.stdout.write(self.style.ERROR(f'Could not determine column names in {table_name}. Columns found: {columns}'))
            return
            
        # Import to main DB
        dest_cursor = dest_conn.cursor()
        
        # First, clear existing relationships
        dest_cursor.execute('DELETE FROM blog_word_thematic_categories')
        
        # Then insert new ones
        for relationship in relationships:
            word_id = relationship[columns.index(word_id_col)]
            category_id = relationship[columns.index(category_id_col)]
            
            # Get column names from destination table
            dest_cursor.execute("PRAGMA table_info(blog_word_thematic_categories)")
            dest_columns = [info[1] for info in dest_cursor.fetchall()]
            
            # Determine the id column (primary key)
            id_col = next((col for col in dest_columns if col == 'id'), None)
            
            # If there's an ID column, we need to generate a new ID
            if id_col:
                dest_cursor.execute('SELECT MAX(id) FROM blog_word_thematic_categories')
                max_id = dest_cursor.fetchone()[0]
                new_id = 1 if max_id is None else max_id + 1
                
                dest_cursor.execute(
                    'INSERT INTO blog_word_thematic_categories (id, word_id, thematiccategory_id) VALUES (?, ?, ?)',
                    (new_id, word_id, category_id)
                )
            else:
                dest_cursor.execute(
                    'INSERT INTO blog_word_thematic_categories (word_id, thematiccategory_id) VALUES (?, ?)',
                    (word_id, category_id)
                )
        
        dest_conn.commit()
        self.stdout.write(f'Copied {len(relationships)} word-category relationships')
    
    def _copy_example_sentences(self, source_conn, dest_conn):
        """Copy ExampleSentence records"""
        self.stdout.write('Copying example sentences...')
        
        # Get table name from source database
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%examplesentence%'")
        table_result = source_cursor.fetchone()
        
        if not table_result:
            self.stdout.write(self.style.WARNING('No example sentence table found in backup'))
            return
            
        table_name = table_result[0]
        
        # Get example sentences from backup
        source_cursor.execute(f'SELECT id, word_id, text, translation, created_at FROM {table_name}')
        examples = source_cursor.fetchall()
        
        # Import to main DB
        dest_cursor = dest_conn.cursor()
        
        # First, clear existing examples (optional - remove if you want to merge instead)
        dest_cursor.execute('DELETE FROM blog_examplesentence')
        
        # Then insert new ones
        for example in examples:
            dest_cursor.execute(
                'INSERT OR REPLACE INTO blog_examplesentence (id, word_id, text, translation, created_at) VALUES (?, ?, ?, ?, ?)',
                (example['id'], example['word_id'], example['text'], example['translation'], example['created_at'])
            )
        
        dest_conn.commit()
        self.stdout.write(f'Copied {len(examples)} example sentences')
