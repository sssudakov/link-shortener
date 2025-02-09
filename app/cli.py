import click
from flask.cli import with_appcontext
from app.models import Link
from app.services import create_short_link, get_link_by_code, soft_delete_link, delete_link
from werkzeug.exceptions import NotFound

@click.group() 
def cli():
    pass

@cli.command("create-link")
@click.argument("original_url")
@with_appcontext
def create_link_command(original_url):
    try:
        link = create_short_link(original_url)
        click.echo(f"Created short link: {link.short_code} for {link.original_url}")
    except Exception as e:
        click.echo(f"Creation link Error: {e}", err=True)


@cli.command("soft-delete-link")
@click.argument("short_code")
@with_appcontext
def soft_delete_link_command(short_code):
    try:
        soft_delete_link(short_code)
        click.echo(f"URL with code {short_code} has soft deleted.")
    except NotFound:
        click.echo(f"URL with code{short_code} not found.", err=True)
    except Exception as e:
        (click.echo(f"Error: {e}", err=True)


@cli.command("delete-link"))
@click.argument("short_code")
@with_appcontext
def delete_link_command(short_code):
    try:
        delete_link(short_code)
        click.echo(f"URL with code {short_code} has deleted.")
    except NotFound:
        click.echo(f"URL with code{short_code} not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command("get-link")
@click.argument("short_code")
@with_appcontext
def get_link_command(short_code):
    try:
        link = get_link_by_code(short_code)
        click.echo(f"ID: {link.id}")
        click.echo(f"Original URL: {link.original_url}")
        click.echo(f"Short Code: {link.short_code}")
        click.echo(f"Clicks: {link.clicks}")
        click.echo(f"Created At: {link.created_at}")
        click.echo(f"Deleted At: {link.deleted_at if link.deleted_at else 'Not deleted'}")
    except NotFound:
        click.echo(f"URL with code {short_code} not found", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command("list-links")
@with_appcontext
def list_links_command():
    try:
        links = Link.query.all()
        if not links:
          click.echo("There are no links in the database.")
          return

        for link in links:
          click.echo(f"ID: {link.id}, Original URL: {link.original_url}, Short Code: {link.short_code}, Clicks:{link.clicks}, Created At: {link.created_at}, Deleted At: {link.deleted_at if link.deleted_at else 'Not deleted'}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command("flush-redis")
@with_appcontext
def flush_redis_command():
    """Clears all keys from Redis"""
    try:
        from flask import current_app
        current_app.redis.flushall()
        click.echo("Redis cache cleared successfully.")
    except Exception as e:
        click.echo("Error: " + str(e), err=True)