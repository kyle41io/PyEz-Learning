# 🔄 Data Migration: SQLite → PostgreSQL

## ✅ Step 1: Export Data from SQLite (Already Done)

Your current SQLite database is at: `/Users/lysa/Documents/PyEz-Learning/db.sqlite3`

Export all data to a JSON file:

```bash
cd /Users/lysa/Documents/PyEz-Learning
source venv/bin/activate
python manage.py dumpdata --natural-foreign --natural-primary > data_backup.json
```

This creates `data_backup.json` with ALL your data (users, lessons, exams, progress, etc.)

---

## 📦 Step 2: Set Up PostgreSQL Locally (Choose One Option)

### Option A: Use Railway PostgreSQL (Recommended - Easiest)

1. Go to [railway.app](https://railway.app) and sign up
2. Create new project → Add PostgreSQL database
3. Copy the `DATABASE_URL` from Railway dashboard
4. Create `.env` file in your project root:
   ```
   DATABASE_URL=postgresql://postgres:password@host:5432/railway
   ```

### Option B: Install PostgreSQL Locally (Mac)

```bash
# Install PostgreSQL via Homebrew
brew install postgresql@14

# Start PostgreSQL
brew services start postgresql@14

# Create database
createdb pyez_learning

# Add to .env file
echo "DATABASE_URL=postgresql://localhost/pyez_learning" > .env
```

### Option C: Use Docker (Advanced)

```bash
docker run -d \
  --name pyez-postgres \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=pyez_learning \
  -p 5432:5432 \
  postgres:14

# Add to .env
echo "DATABASE_URL=postgresql://postgres:password123@localhost:5432/pyez_learning" > .env
```

---

## 🚀 Step 3: Migrate to PostgreSQL

Once you have PostgreSQL set up and `DATABASE_URL` in `.env`:

```bash
cd /Users/lysa/Documents/PyEz-Learning
source venv/bin/activate

# 1. Run migrations on PostgreSQL (creates tables)
python manage.py migrate

# 2. Import your data
python manage.py loaddata data_backup.json
```

**Expected Output:**
```
Installed 150 object(s) from 1 fixture(s)
```

---

## ✅ Step 4: Verify Migration

```bash
# Check if data is there
python manage.py shell
```

In the shell:
```python
from users.models import User
from curriculum.models import Lesson
from exams.models import ActiveExam

print(f"Users: {User.objects.count()}")
print(f"Lessons: {Lesson.objects.count()}")
print(f"Exams: {ActiveExam.objects.count()}")

# Exit shell
exit()
```

---

## 🎯 Step 5: Test Your App

```bash
# Start server with PostgreSQL
python manage.py runserver
```

Visit http://localhost:8000 and verify:
- ✅ You can log in with existing accounts
- ✅ Lessons show up
- ✅ Exams are there
- ✅ Student progress is preserved

---

## 🚨 Troubleshooting

### "No such table" error
```bash
# Make sure migrations ran
python manage.py migrate
```

### "Could not connect to database"
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Check PostgreSQL is running
psql $DATABASE_URL -c "SELECT 1"
```

### "Invalid fixture data"
```bash
# Re-export with exclude problematic apps
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --natural-foreign \
  --natural-primary \
  > data_backup_clean.json

# Then load
python manage.py loaddata data_backup_clean.json
```

### "Duplicate key" errors
This happens if you loaded data multiple times. Fix:
```bash
# Clear PostgreSQL database
python manage.py flush --noinput

# Re-run migrations
python manage.py migrate

# Reload data
python manage.py loaddata data_backup.json
```

---

## 📋 Quick Commands Summary

```bash
# 1. Export from SQLite
python manage.py dumpdata --natural-foreign --natural-primary > data_backup.json

# 2. Set up DATABASE_URL in .env

# 3. Migrate PostgreSQL
python manage.py migrate

# 4. Import data
python manage.py loaddata data_backup.json

# 5. Verify
python manage.py shell
>>> from users.models import User; print(User.objects.count())

# 6. Test
python manage.py runserver
```

---

## 🎉 After Successful Migration

1. **Keep SQLite backup**: Don't delete `db.sqlite3` until you're 100% sure PostgreSQL works
2. **Update .gitignore**: Already done ✅
3. **Commit changes**: 
   ```bash
   git add .
   git commit -m "Switch to PostgreSQL"
   git push origin main
   ```
4. **Deploy to Railway**: Your production will use Railway's PostgreSQL automatically!

---

## 💡 Pro Tips

- **Backup regularly**: `python manage.py dumpdata > backup_$(date +%Y%m%d).json`
- **Keep SQLite for dev**: Without DATABASE_URL, app uses SQLite automatically
- **Use migrations**: Never edit database directly, always use Django migrations
- **Test locally first**: Make sure PostgreSQL works locally before deploying

---

Need help? Check the error message and the troubleshooting section above!
