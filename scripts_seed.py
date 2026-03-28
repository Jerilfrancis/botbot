from app.db import init_db, get_db

init_db()
conn = get_db()

conn.execute("INSERT OR IGNORE INTO users(id,name,email,password,role) VALUES(1,'Admin','admin@learnx.dev','admin123','admin')")
conn.execute("INSERT OR IGNORE INTO users(id,name,email,password,role) VALUES(2,'Mentor A','mentor@learnx.dev','mentor123','mentor')")
conn.execute("INSERT OR IGNORE INTO users(id,name,email,password,role) VALUES(3,'Student A','student@learnx.dev','student123','student')")
conn.execute("INSERT OR IGNORE INTO courses(id,mentor_id,title,topic,description,is_published) VALUES(1,2,'Python Basics','Python','Start Python from zero',1)")
conn.execute("INSERT OR IGNORE INTO modules(id,course_id,title,position,is_preview,video_url) VALUES(1,1,'Introduction',1,1,'https://example.com/video')")
conn.commit()
conn.close()

print('Seed data inserted.')
