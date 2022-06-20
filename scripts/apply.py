from yoyo import read_migrations, get_backend


backend = get_backend('postgresql://postgres:postgres@db/postgres')
migrations = read_migrations('app/db/migrations')
