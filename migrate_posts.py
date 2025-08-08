#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casipe.settings')
django.setup()

from blog.models import Post
from django.contrib.auth import get_user_model
User = get_user_model()

def copy_posts_from_backup():
    # Connect to the backup database
    backup_conn = sqlite3.connect('db.sqlite3.backup')
    backup_cursor = backup_conn.cursor()
    
    # Get all posts from the backup database
    backup_cursor.execute('''
        SELECT id, title, slug, content, image, is_published, 
               published_date, author_id, created_at, updated_at 
        FROM blog_post
    ''')
    
    posts = backup_cursor.fetchall()
    print(f"Found {len(posts)} posts in the backup database")
    
    # Track successes and failures
    success_count = 0
    error_count = 0
    
    # Copy each post to the current database
    for post in posts:
        try:
            post_id, title, slug, content, image, is_published, published_date, author_id, created_at, updated_at = post
            
            # Check if the user exists
            try:
                author = User.objects.get(id=author_id)
            except User.DoesNotExist:
                print(f"Warning: User with ID {author_id} does not exist for post '{title}'. Using default admin user.")
                # Try to get the first superuser as a fallback
                try:
                    author = User.objects.filter(is_superuser=True).first()
                    if not author:
                        print(f"Error: No superuser found. Skipping post '{title}'.")
                        error_count += 1
                        continue
                except:
                    print(f"Error: Failed to find any user. Skipping post '{title}'.")
                    error_count += 1
                    continue
            
            # Check if the post with the same slug already exists
            existing_post = Post.objects.filter(slug=slug).first()
            if existing_post:
                print(f"Post with slug '{slug}' already exists. Creating a unique slug.")
                base_slug = slug
                counter = 1
                while Post.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
            
            # Parse dates if they exist
            if published_date:
                try:
                    published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                except:
                    published_date = None
            
            # Handle image path
            image_path = image if image else None
            
            # Create the new post
            new_post = Post(
                title=title,
                slug=slug,
                content=content,
                image=image_path,
                is_published=is_published,
                published_date=published_date,
                author=author,
            )
            
            # Set created_at and updated_at if you want to preserve them
            # Note: This might require temporarily disabling auto_now/auto_now_add
            if created_at:
                new_post.created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if updated_at:
                new_post.updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            # Save the post
            new_post.save()
            
            success_count += 1
            print(f"Successfully migrated post: '{title}'")
            
        except Exception as e:
            error_count += 1
            print(f"Error migrating post: {str(post[:2])}")
            print(f"Error details: {str(e)}")
    
    # Close connection to backup database
    backup_conn.close()
    
    # Print summary
    print("\nMigration Summary:")
    print(f"Total posts processed: {len(posts)}")
    print(f"Successfully migrated: {success_count}")
    print(f"Failed to migrate: {error_count}")

if __name__ == "__main__":
    print("Starting migration of posts from backup database...")
    copy_posts_from_backup()
    print("Migration completed!")
